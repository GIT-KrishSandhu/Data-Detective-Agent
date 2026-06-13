"use client";

import React, { useEffect, useState } from "react";
import { 
  CheckCircle2, 
  Circle, 
  Loader2, 
  Sparkles, 
  Database, 
  Server, 
  RefreshCw,
  Upload,
  Brain,
  Activity,
  TrendingUp,
  ShieldCheck,
  Award,
  ChevronRight
} from "lucide-react";

interface LogStep {
  type: string;
  agent_name: string;
  agent?: string;
  name?: string;
  tool_name?: string | null;
  status: string;
  started_at: string;
  completed_at: string;
  execution_time_ms: number;
  confidence: number;
  event?: string;
  timestamp?: string;
}

interface WorkflowViewerProps {
  steps: string[];
  currentStep: string;
  reasoning?: string;
  confidence?: number;
  agentExecutionLog?: LogStep[];
  onAnimationComplete?: () => void;
}

export default function WorkflowViewer({ 
  steps, 
  currentStep, 
  reasoning, 
  confidence,
  agentExecutionLog,
  onAnimationComplete
}: WorkflowViewerProps) {
  
  const [animatedLog, setAnimatedLog] = useState<any[]>([]);
  const [activeStepIndex, setActiveStepIndex] = useState<number>(-1);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);

  useEffect(() => {
    if (!Array.isArray(agentExecutionLog) || agentExecutionLog.length === 0) {
      setAnimatedLog([]);
      setIsAnimating(false);
      return;
    }

    const plannerStep = agentExecutionLog.find(l => l?.type === "agent_step" && (l?.agent_name ?? l?.agent ?? l?.name) === "PlannerAgent");
    const qualityStep = agentExecutionLog.find(l => l?.type === "agent_step" && (l?.agent_name ?? l?.agent ?? l?.name) === "QualityAgent");
    const toolSteps = agentExecutionLog.filter(l => l?.type === "tool_step" && (l?.agent_name ?? l?.agent ?? l?.name) === "QualityAgent");
    const biStep = agentExecutionLog.find(l => l?.type === "agent_step" && (l?.agent_name ?? l?.agent ?? l?.name) === "BIReadinessAgent");
    const biToolSteps = agentExecutionLog.filter(l => l?.type === "tool_step" && (l?.agent_name ?? l?.agent ?? l?.name) === "BIReadinessAgent");
    const evaluationStep = agentExecutionLog.find(l => l?.type === "agent_step" && (l?.agent_name ?? l?.agent ?? l?.name) === "EvaluationAgent");

    const visualTimeline: any[] = [];

    // Step 0: Planner Running
    visualTimeline.push({
      key: "planner",
      label: "Planner Agent",
      type: "agent",
      status: "running",
      time: plannerStep?.execution_time_ms || 0
    });

    // Step 1: Planner Blackboard
    visualTimeline.push({
      key: "blackboard_planner",
      label: "Blackboard Updated by Planner (v1)",
      type: "blackboard",
      status: "pending"
    });

    // Step 2: Quality Agent
    visualTimeline.push({
      key: "quality_agent",
      label: "Quality Agent",
      type: "agent",
      status: "pending",
      time: qualityStep?.execution_time_ms || 0
    });

    // Step 3..N: Quality Tools
    toolSteps.forEach((tool, idx) => {
      visualTimeline.push({
        key: `tool_quality_${idx}`,
        label: tool.tool_name || "Data Quality Tool",
        type: "tool",
        status: "pending",
        time: tool.execution_time_ms
      });
    });

    // Step N+1: Quality Blackboard
    visualTimeline.push({
      key: "blackboard_quality",
      label: "Blackboard Updated by Quality Agent (v2)",
      type: "blackboard",
      status: "pending"
    });

    // Step N+2: BI Agent
    visualTimeline.push({
      key: "bi_agent",
      label: "BI Readiness Agent",
      type: "agent",
      status: "pending",
      time: biStep?.execution_time_ms || 0
    });

    // Step N+3..M: BI Tools
    biToolSteps.forEach((tool, idx) => {
      visualTimeline.push({
        key: `tool_bi_${idx}`,
        label: tool.tool_name || "BI Audit Tool",
        type: "tool",
        status: "pending",
        time: tool.execution_time_ms
      });
    });

    // Step M+1: BI Blackboard
    visualTimeline.push({
      key: "blackboard_bi",
      label: "Blackboard Updated by BI Agent (v3)",
      type: "blackboard",
      status: "pending"
    });

    // Step M+2: Evaluation Agent
    visualTimeline.push({
      key: "evaluation_agent",
      label: "Evaluation Agent",
      type: "agent",
      status: "pending",
      time: evaluationStep?.execution_time_ms || 0
    });

    // Step Final: Evaluation Blackboard
    visualTimeline.push({
      key: "blackboard_evaluation",
      label: "Blackboard Updated by Evaluation Agent (v4)",
      type: "blackboard",
      status: "pending"
    });

    setAnimatedLog(visualTimeline);
    setActiveStepIndex(0);
    setIsAnimating(true);
    
    let currentIndex = 0;
    
    const interval = setInterval(() => {
      currentIndex++;
      if (currentIndex < visualTimeline.length) {
        setActiveStepIndex(currentIndex);
        setAnimatedLog(prev => {
          const updated = [...prev];
          updated[currentIndex - 1] = {
            ...updated[currentIndex - 1],
            status: "completed"
          };
          updated[currentIndex] = {
            ...updated[currentIndex],
            status: "running"
          };
          return updated;
        });
      } else {
        setAnimatedLog(prev => {
          return prev.map(item => ({ ...item, status: "completed" }));
        });
        setActiveStepIndex(visualTimeline.length);
        setIsAnimating(false);
        clearInterval(interval);
        if (onAnimationComplete) {
          onAnimationComplete();
        }
      }
    }, 450);

    return () => clearInterval(interval);
  }, [agentExecutionLog]);

  const hasLogs = agentExecutionLog && agentExecutionLog.length > 0;

  const getStageStatus = (stage: string) => {
    if (!isAnimating && hasLogs) return "completed";
    if (!isAnimating && !hasLogs) return stage === "upload" ? "completed" : "pending";

    if (stage === "upload") return "completed";
    if (stage === "planner") {
      return animatedLog.find(l => l.key === "planner")?.status || "pending";
    }
    if (stage === "quality") {
      const item = animatedLog.find(l => l.key === "quality_agent");
      if (item?.status === "completed") {
        const lastTool = animatedLog.filter(l => l.key.startsWith("tool_quality_")).pop();
        if (lastTool && lastTool.status !== "completed") return "running";
        return "completed";
      }
      return item?.status || "pending";
    }
    if (stage === "bi") {
      const item = animatedLog.find(l => l.key === "bi_agent");
      if (item?.status === "completed") {
        const lastTool = animatedLog.filter(l => l.key.startsWith("tool_bi_")).pop();
        if (lastTool && lastTool.status !== "completed") return "running";
        return "completed";
      }
      return item?.status || "pending";
    }
    if (stage === "evaluation") {
      return animatedLog.find(l => l.key === "evaluation_agent")?.status || "pending";
    }
    if (stage === "certificate") {
      return animatedLog.find(l => l.key === "blackboard_evaluation")?.status || "pending";
    }
    return "pending";
  };

  const getStageDuration = (stage: string): string => {
    if (!Array.isArray(agentExecutionLog)) return "";
    let agentName = "";
    if (stage === "planner") agentName = "PlannerAgent";
    else if (stage === "quality") agentName = "QualityAgent";
    else if (stage === "bi") agentName = "BIReadinessAgent";
    else if (stage === "evaluation") agentName = "EvaluationAgent";

    if (!agentName) return "";
    const step = agentExecutionLog.find(l => l?.type === "agent_step" && (l?.agent_name ?? l?.agent ?? l?.name) === agentName);
    return step && step?.execution_time_ms ? `${step.execution_time_ms}ms` : "";
  };

  const getStageConfidence = (stage: string): string => {
    if (!Array.isArray(agentExecutionLog)) return "";
    let agentName = "";
    if (stage === "planner") agentName = "PlannerAgent";
    else if (stage === "quality") agentName = "QualityAgent";
    else if (stage === "bi") agentName = "BIReadinessAgent";
    else if (stage === "evaluation") agentName = "EvaluationAgent";

    if (!agentName) return "";
    const step = agentExecutionLog.find(l => l?.type === "agent_step" && (l?.agent_name ?? l?.agent ?? l?.name) === agentName);
    return step && step?.confidence ? `${(step.confidence * 100).toFixed(0)}%` : "";
  };

  const stages = [
    { id: "upload", label: "Upload", icon: Upload, desc: "Data Ingested" },
    { id: "planner", label: "Planner", icon: Brain, desc: "Inference Graph" },
    { id: "quality", label: "Quality Agent", icon: Activity, desc: "Anomalies Checked" },
    { id: "bi", label: "BI Readiness", icon: TrendingUp, desc: "dashboard Profiler" },
    { id: "evaluation", label: "Evaluation", icon: ShieldCheck, desc: "Truth Verified" },
    { id: "certificate", label: "Certificate", icon: Award, desc: "Compliance Sealed" },
  ];

  return (
    <div className="flex flex-col gap-6 w-full animate-in fade-in duration-300">
      
      {/* TOP: Horizontal Agent Execution Pipeline (Microsoft Fabric Minimal Aesthetic) */}
      <div className="p-5 rounded-xl border border-slate-900 bg-slate-950/40 backdrop-blur-sm flex flex-col gap-4">
        <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider flex items-center gap-1.5 font-mono">
          <Server className="h-3.5 w-3.5" />
          Orchestration Pipeline Nodes
        </span>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 items-center relative">
          {stages.map((stage, index) => {
            const status = getStageStatus(stage.id);
            const Icon = stage.icon;
            const duration = getStageDuration(stage.id);
            const conf = getStageConfidence(stage.id);

            const isCompleted = status === "completed";
            const isRunning = status === "running";
            const isPending = status === "pending";

            return (
              <React.Fragment key={stage.id}>
                {/* Stage Node Card */}
                <div className={`p-3.5 rounded-lg border flex flex-col gap-1.5 transition-all duration-500 relative bg-slate-950/80 ${
                  isCompleted ? "border-emerald-500/30 shadow-md shadow-emerald-500/5 bg-emerald-950/5" :
                  isRunning ? "border-indigo-500/50 shadow-md shadow-indigo-500/10 ring-1 ring-indigo-500/20 bg-indigo-950/10" :
                  "border-slate-900 opacity-40"
                }`}>
                  {/* Status Indicator Dot/Loader */}
                  <div className="absolute top-2 right-2">
                    {isRunning ? (
                      <Loader2 className="h-3 w-3 text-indigo-400 animate-spin" />
                    ) : isCompleted ? (
                      <div className="h-1.5 w-1.5 bg-emerald-400 rounded-full animate-pulse" />
                    ) : (
                      <div className="h-1.5 w-1.5 bg-slate-800 rounded-full" />
                    )}
                  </div>

                  {/* Icon and Title */}
                  <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded ${
                      isCompleted ? "bg-emerald-950 text-emerald-400" :
                      isRunning ? "bg-indigo-950 text-indigo-400" :
                      "bg-slate-900 text-slate-500"
                    }`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="text-xs font-bold text-slate-200">{stage.label}</span>
                  </div>

                  {/* Metrics Row */}
                  <div className="flex items-center justify-between text-[9px] font-mono text-slate-500 mt-1 border-t border-slate-900/60 pt-1.5">
                    <span>{duration || (isCompleted ? "Success" : isPending ? "Waiting" : "Active")}</span>
                    {conf && <span className="text-indigo-400 font-semibold">{conf}</span>}
                  </div>
                </div>

                {/* Arrow Connector (Only on large screens between nodes) */}
                {index < stages.length - 1 && (
                  <div className="hidden lg:flex absolute items-center justify-center pointer-events-none" style={{
                    left: `${(index + 1) * 16.666 - 2.5}%`,
                    width: "5%"
                  }}>
                    <ChevronRight className={`h-4 w-4 ${isCompleted ? "text-emerald-500/40" : "text-slate-800"}`} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* BOTTOM: Split view with timeline logs and planner intent */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full">
        
        {/* LEFT: Multi-Agent Network Activity Log */}
        <div className="lg:col-span-2 p-6 rounded-xl border border-slate-900 bg-slate-950/40 backdrop-blur-sm flex flex-col gap-5">
          <div className="flex items-center justify-between border-b border-slate-900 pb-3">
            <div className="flex items-center gap-2">
              <Server className="h-4.5 w-4.5 text-indigo-400" />
              <h3 className="font-semibold text-sm text-slate-200 font-mono">Telemetry Streams</h3>
            </div>
            {isAnimating ? (
              <span className="flex items-center gap-1.5 text-[10px] bg-indigo-950 border border-indigo-900 text-indigo-400 px-2 py-0.5 rounded font-bold animate-pulse font-mono">
                <RefreshCw className="h-3 w-3 animate-spin" />
                Active Node Execution
              </span>
            ) : (
              <span className="text-[10px] bg-emerald-950 border border-emerald-900 text-emerald-400 px-2 py-0.5 rounded font-bold font-mono">
                ✓ Node Traces Resolved
              </span>
            )}
          </div>

          {!hasLogs ? (
            /* Basic Loading Steps */
            <div className="flex flex-col gap-4 relative pl-4 border-l border-slate-900 ml-3">
              {steps.map((step, idx) => {
                const isActive = currentStep === step || (currentStep === "Planner Complete" && idx === 0);
                const isDone = currentStep === "Planner Complete" && idx > 0;
                return (
                  <div key={idx} className="flex items-start gap-3 relative">
                    <div className="absolute left-[-26px] top-0.5 bg-slate-950 rounded-full p-0.5">
                      {isActive ? (
                        <Loader2 className="h-4 w-4 text-indigo-400 animate-spin" />
                      ) : isDone ? (
                        <Circle className="h-4 w-4 text-slate-700" />
                      ) : (
                        <CheckCircle2 className="h-4 w-4 text-emerald-400 fill-emerald-500/10" />
                      )}
                    </div>
                    <span className={`text-sm font-semibold ${isActive ? "text-indigo-400" : "text-slate-500"}`}>
                      {step}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            /* Premium Animated Agent Execution Steps */
            <div className="flex flex-col gap-3.5 relative pl-4 border-l border-slate-900 ml-3">
              {animatedLog.map((step) => {
                const isAgent = step.type === "agent";
                const isBlackboard = step.type === "blackboard";

                return (
                  <div 
                    key={step.key} 
                    className={`flex items-start gap-3 relative transition-all duration-300 ${
                      step.status === "pending" ? "opacity-30" : "opacity-100"
                    }`}
                  >
                    <div className="absolute left-[-26px] top-0.5 bg-slate-950 rounded-full p-0.5">
                      {step.status === "running" ? (
                        <Loader2 className="h-4 w-4 text-indigo-400 animate-spin" />
                      ) : step.status === "completed" ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-400 fill-emerald-500/10" />
                      ) : (
                        <Circle className="h-4 w-4 text-slate-700" />
                      )}
                    </div>

                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-bold ${
                          isAgent ? "text-indigo-300" : 
                          isBlackboard ? "text-purple-400" : "text-slate-300 font-mono text-xs"
                        }`}>
                          {step.label}
                        </span>
                        {step.status === "completed" && step.time > 0 && (
                          <span className="text-[10px] text-slate-500 font-mono">
                            ({step.time} ms)
                          </span>
                        )}
                      </div>
                      {step.status === "running" && (
                        <span className="text-[10px] text-slate-400 mt-0.5 animate-pulse font-mono">
                          {isAgent ? "Executing cognitive workflow reasoning..." :
                           isBlackboard ? "Pushing trace metrics & Pydantic state to Blackboard memory..." :
                           "Running deterministic validation calculations..."}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* RIGHT: Planner Reasoning & Information Card */}
        <div className="p-6 rounded-xl border border-slate-900 bg-slate-950/40 backdrop-blur-sm flex flex-col gap-4 h-full">
          <div className="flex items-center justify-between border-b border-slate-900 pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4.5 w-4.5 text-indigo-400" />
              <h3 className="font-semibold text-sm text-slate-200">Analysis Plan Objective</h3>
            </div>
            {confidence !== undefined && confidence > 0 && (
              <span className="text-[10px] bg-indigo-950 border border-indigo-900 text-indigo-400 px-2 py-0.5 rounded font-bold font-mono">
                Confidence: {(confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>

          {reasoning ? (
            <div className="flex flex-col gap-3 text-xs text-slate-400 leading-relaxed">
              <span className="font-bold text-slate-300 block">Agent Intent Rationale:</span>
              <div className="p-4 rounded-lg bg-indigo-950/10 border border-indigo-500/10 text-slate-300 leading-relaxed font-sans">
                {reasoning}
              </div>
              <p className="text-[10px] text-slate-500 italic mt-2">
                Derived dynamically by the Planner Agent on start. Re-evaluates routing boundaries to distribute queries across data quality and Power BI readiness profiling scopes.
              </p>
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-xs text-slate-500">
              Awaiting planner execution result...
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
