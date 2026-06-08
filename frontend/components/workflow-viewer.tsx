"use client";

import React from "react";
import { CheckCircle2, Circle, Loader2, Sparkles, AlertCircle } from "lucide-react";

interface WorkflowViewerProps {
  steps: string[];
  currentStep: string;
  reasoning?: string;
  confidence?: number;
}

export default function WorkflowViewer({ 
  steps, 
  currentStep, 
  reasoning, 
  confidence 
}: WorkflowViewerProps) {
  
  // Default mockup steps for demo visualizer if nothing is generated yet
  const defaultDemoSteps = [
    "Schema Analysis",
    "Data Quality Analysis",
    "Statistics Analysis",
    "Visualization Planning",
    "Report Synthesis"
  ];

  const displaySteps = steps.length > 0 ? steps : defaultDemoSteps;

  const getStepStatus = (stepName: string, idx: number) => {
    // If the planner itself is complete, and we have custom steps
    if (currentStep === "Planner Complete" && steps.length > 0) {
      if (idx === 0) return "active"; // Focus on the first execution step (e.g. Quality/Schema)
      return "pending";
    }

    if (currentStep.toLowerCase() === "idle" || steps.length === 0) {
      return "pending";
    }

    // Standard checking if matching current step
    const currentIdx = displaySteps.findIndex(
      (s) => s.toLowerCase().replace(/\s+/g, "") === currentStep.toLowerCase().replace(/\s+/g, "")
    );

    if (currentIdx === -1) {
      // Fallback
      if (idx === 0) return "active";
      return "pending";
    }

    if (idx < currentIdx) return "completed";
    if (idx === currentIdx) return "active";
    return "pending";
  };

  return (
    <div className="p-6 rounded-xl border border-slate-900 bg-slate-900/20 backdrop-blur-sm flex flex-col gap-6 w-full animate-in fade-in duration-300">
      <div className="flex items-center justify-between border-b border-slate-900 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-indigo-400" />
          <h3 className="font-semibold text-sm text-slate-200">Execution Workflow Planner</h3>
        </div>
        {confidence !== undefined && confidence > 0 && (
          <span className="text-[10px] bg-indigo-950 border border-indigo-900 text-indigo-400 px-2 py-0.5 rounded font-bold">
            Confidence: {(confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>

      {/* Steps Visual List */}
      <div className="flex flex-col gap-4 relative pl-4 border-l border-slate-900 ml-3">
        {displaySteps.map((step, idx) => {
          const status = getStepStatus(step, idx);
          
          return (
            <div key={idx} className="flex items-start gap-3 relative group">
              {/* Status Indicator Icon */}
              <div className="absolute left-[-26px] top-0.5 bg-slate-950 rounded-full p-0.5 transition-all">
                {status === "completed" ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 fill-emerald-500/10" />
                ) : status === "active" ? (
                  <Loader2 className="h-4 w-4 text-indigo-400 animate-spin" />
                ) : (
                  <Circle className="h-4 w-4 text-slate-700" />
                )}
              </div>

              <div>
                <span className={`text-sm font-semibold transition-colors ${
                  status === "completed" 
                    ? "text-emerald-400/90" 
                    : status === "active" 
                      ? "text-indigo-400" 
                      : "text-slate-500"
                }`}>
                  {step}
                </span>
                {status === "active" && (
                  <p className="text-[10px] text-indigo-400/80 mt-0.5 animate-pulse">
                    Node executing in LangGraph blackboard session...
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Reasoning Info Card */}
      {reasoning && (
        <div className="p-4 rounded-lg bg-indigo-950/20 border border-indigo-500/10 flex items-start gap-3">
          <AlertCircle className="h-4 w-4 text-indigo-400 shrink-0 mt-0.5" />
          <div className="text-xs text-slate-400 leading-normal">
            <span className="font-semibold text-slate-200 block mb-1">Planner Reasoning:</span>
            {reasoning}
          </div>
        </div>
      )}
    </div>
  );
}
