"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2, Sparkles, AlertCircle, Database, Server, RefreshCw } from "lucide-react";

interface LogStep {
  type: string;
  agent_name: string;
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
    if (!agentExecutionLog || agentExecutionLog.length === 0) {
      setAnimatedLog([]);
      setIsAnimating(false);
      return;
    }

    // Filter and reconstruct the logs for visual display
    // We want a list of items showing the progress:
    // 1. PlannerAgent step
    // 2. Blackboard Updated (Planner)
    // 3. QualityAgent step (container)
    // 4. Quality Agent Tools
    // 5. Blackboard Updated (Quality)
    
    const plannerStep = agentExecutionLog.find(l => l.type === "agent_step" && l.agent_name === "PlannerAgent");
    const qualityStep = agentExecutionLog.find(l => l.type === "agent_step" && l.agent_name === "QualityAgent");
    const toolSteps = agentExecutionLog.filter(l => l.type === "tool_step" && l.agent_name === "QualityAgent");
    const biStep = agentExecutionLog.find(l => l.type === "agent_step" && l.agent_name === "BIReadinessAgent");
    const biToolSteps = agentExecutionLog.filter(l => l.type === "tool_step" && l.agent_name === "BIReadinessAgent");
    const evaluationStep = agentExecutionLog.find(l => l.type === "agent_step" && l.agent_name === "EvaluationAgent");

    const visualTimeline: any[] = [];

    // Step 0: Planner Running -> Completed
    visualTimeline.push({
      key: "planner",
      label: "Planner Agent",
      type: "agent",
      status: "running",
      time: plannerStep?.execution_time_ms || 0
    });

    // Step 1: Planner Blackboard Updated
    visualTimeline.push({
      key: "blackboard_planner",
      label: "Blackboard Updated by Planner (v1)",
      type: "blackboard",
      status: "pending"
    });

    // Step 2: Quality Agent Running -> Completed
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

    // Step N+1: Quality Blackboard Updated
    visualTimeline.push({
      key: "blackboard_quality",
      label: "Blackboard Updated by Quality Agent (v2)",
      type: "blackboard",
      status: "pending"
    });

    // Step N+2: BI Readiness Agent Running -> Completed
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

    // Step M+1: BI Blackboard Updated
    visualTimeline.push({
      key: "blackboard_bi",
      label: "Blackboard Updated by BI Agent (v3)",
      type: "blackboard",
      status: "pending"
    });

    // Step M+2: Evaluation Agent Running -> Completed
    visualTimeline.push({
      key: "evaluation_agent",
      label: "Evaluation Agent",
      type: "agent",
      status: "pending",
      time: evaluationStep?.execution_time_ms || 0
    });

    // Step Final: Evaluation Blackboard Updated
    visualTimeline.push({
      key: "blackboard_evaluation",
      label: "Blackboard Updated by Evaluation Agent (v4)",
      type: "blackboard",
      status: "pending"
    });

    // Run animation
    setAnimatedLog(visualTimeline);
    setActiveStepIndex(0);
    setIsAnimating(true);
    
    let currentIndex = 0;
    
    const interval = setInterval(() => {
      currentIndex++;
      if (currentIndex < visualTimeline.length) {
        setActiveStepIndex(currentIndex);
        
        // Update statuses up to current
        setAnimatedLog(prev => {
          const updated = [...prev];
          // Mark previous as completed
          updated[currentIndex - 1] = {
            ...updated[currentIndex - 1],
            status: "completed"
          };
          // Mark current as running
          updated[currentIndex] = {
            ...updated[currentIndex],
            status: "running"
          };
          return updated;
        });
      } else {
        // All completed
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
    }, 450); // 450ms transition between steps for responsive live look

    return () => clearInterval(interval);
  }, [agentExecutionLog]);

  // If no log is provided, fall back to standard steps list
  const showBasicTimeline = !agentExecutionLog || agentExecutionLog.length === 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full animate-in fade-in duration-300">
      
      {/* LEFT: Multi-Agent Network Activity Log */}
      <div className="lg:col-span-2 p-6 rounded-xl border border-slate-900 bg-slate-950/40 backdrop-blur-sm flex flex-col gap-5">
        <div className="flex items-center justify-between border-b border-slate-900 pb-3">
          <div className="flex items-center gap-2">
            <Server className="h-4.5 w-4.5 text-indigo-400" />
            <h3 className="font-semibold text-sm text-slate-200">Multi-Agent Network Activity</h3>
          </div>
          {isAnimating ? (
            <span className="flex items-center gap-1.5 text-[10px] bg-indigo-950 border border-indigo-900 text-indigo-400 px-2 py-0.5 rounded font-bold animate-pulse">
              <RefreshCw className="h-3 w-3 animate-spin" />
              Agent Core Running
            </span>
          ) : (
            <span className="text-[10px] bg-emerald-950 border border-emerald-900 text-emerald-400 px-2 py-0.5 rounded font-bold">
              ✓ Process Complete
            </span>
          )}
        </div>

        {showBasicTimeline ? (
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
            {animatedLog.map((step, idx) => {
              const isAgent = step.type === "agent";
              const isBlackboard = step.type === "blackboard";
              const isTool = step.type === "tool";

              return (
                <div 
                  key={step.key} 
                  className={`flex items-start gap-3 relative transition-all duration-300 ${
                    step.status === "pending" ? "opacity-30" : "opacity-100"
                  }`}
                >
                  {/* Timeline icon */}
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
                      <span className="text-[10px] text-slate-400 mt-0.5 animate-pulse">
                        {isAgent ? "Running cognitive planning inference..." :
                         isBlackboard ? "Updating shared AgentState memory values..." :
                         "Analyzing dataset structures deterministically..."}
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
            <h3 className="font-semibold text-sm text-slate-200">Analysis Intent</h3>
          </div>
          {confidence !== undefined && confidence > 0 && (
            <span className="text-[10px] bg-indigo-950 border border-indigo-900 text-indigo-400 px-2 py-0.5 rounded font-bold">
              Confidence: {(confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>

        {reasoning ? (
          <div className="flex flex-col gap-3 text-xs text-slate-400 leading-relaxed">
            <span className="font-bold text-slate-300 block">Planner Rationale:</span>
            <div className="p-4 rounded-lg bg-indigo-950/10 border border-indigo-500/10 text-slate-300">
              {reasoning}
            </div>
            <p className="text-[10px] text-slate-500 italic mt-2">
              Based on the metadata, row distribution, and target objective, the Planner Agent routes the pipeline to the appropriate worker nodes.
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-center h-32 text-xs text-slate-500">
            Awaiting planner execution result...
          </div>
        )}
      </div>

    </div>
  );
}
