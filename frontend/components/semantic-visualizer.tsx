"use client";

import React, { useState } from "react";
import { Database, Columns, AlertTriangle, Lightbulb, FileText, CheckCircle2, Info } from "lucide-react";

interface SemanticVisualizerProps {
  semanticDataset: any;
  semanticIssues: any[];
  semanticRecommendations: any[];
  semanticBusinessMetrics: any[];
  semanticPowerbiReadiness: any;
  evaluationResult: any;
}

export default function SemanticVisualizer({
  semanticDataset,
  semanticIssues,
  semanticRecommendations,
  semanticBusinessMetrics,
  semanticPowerbiReadiness,
  evaluationResult
}: SemanticVisualizerProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Extract columns (limit to 3 for display clarity)
  const columnsList = semanticDataset?.columns || [];
  const displayCols = columnsList.slice(0, 3);

  // Helper to check if a card path should glow
  const isPathActive = (pathType: "quality" | "business" | "dataset" | "evaluation") => {
    if (!hoveredNode) return false;
    if (hoveredNode === "dataset" || hoveredNode === "evaluation") return true;
    if (pathType === "quality" && (hoveredNode.startsWith("col-") || hoveredNode === "quality" || hoveredNode === "advice")) {
      return true;
    }
    if (pathType === "business" && (hoveredNode.startsWith("col-") || hoveredNode === "metrics" || hoveredNode === "readiness")) {
      return true;
    }
    return false;
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 p-6 bg-slate-950/40 rounded-xl border border-slate-900 select-none animate-in fade-in duration-300">
      
      {/* LEFT: The Static Semantic Flow Visualizer */}
      <div className="xl:col-span-3 flex flex-col items-center gap-2 relative py-4">
        
        {/* Layer 1: Dataset Node */}
        <div 
          onMouseEnter={() => setHoveredNode("dataset")}
          onMouseLeave={() => setHoveredNode(null)}
          className={`p-5 rounded-xl border text-center z-10 transition-all duration-300 cursor-pointer max-w-sm w-full ${
            hoveredNode === "dataset" || isPathActive("dataset")
              ? "border-indigo-500 bg-indigo-950/20 shadow-lg shadow-indigo-500/5 ring-1 ring-indigo-500/20"
              : "border-slate-800 bg-slate-900/30"
          }`}
        >
          <div className="flex items-center justify-center gap-2 mb-1">
            <Database className="h-4 w-4 text-indigo-400" />
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Blackboard Dataset</span>
          </div>
          <h4 className="font-bold text-sm text-slate-100 truncate">{semanticDataset?.filename || "dataset.csv"}</h4>
          <span className="text-[10px] text-slate-500 font-mono">{(semanticDataset?.row_count || 0).toLocaleString()} Rows</span>
        </div>

        {/* Vertical Line Linker */}
        <div className="w-[3px] h-10 bg-slate-800" />

        {/* Layer 2: Columns Row */}
        <div className="flex justify-center gap-6 md:gap-12 w-full relative z-10">
          {displayCols.map((col: any, idx: number) => {
            const nodeKey = `col-${col.name}`;
            const isHovered = hoveredNode === nodeKey;
            return (
              <div 
                key={idx}
                onMouseEnter={() => setHoveredNode(nodeKey)}
                onMouseLeave={() => setHoveredNode(null)}
                className={`p-4 rounded-lg border text-center transition-all duration-300 cursor-pointer min-w-[100px] max-w-[150px] flex-1 ${
                  isHovered || isPathActive(idx % 2 === 0 ? "quality" : "business")
                    ? "border-indigo-500/50 bg-indigo-950/10"
                    : "border-slate-850 bg-slate-900/20"
                }`}
              >
                <div className="flex items-center justify-center gap-1.5 mb-0.5">
                  <Columns className="h-3.5 w-3.5 text-slate-400" />
                  <span className="text-[10px] font-bold text-slate-300 truncate">{col.name}</span>
                </div>
                <span className="text-[9px] text-slate-500 uppercase font-mono">{col.inferred_type}</span>
              </div>
            );
          })}
        </div>

        {/* Tree Connectors SVG */}
        <svg className="w-full h-12 text-slate-800 pointer-events-none" style={{ marginTop: "-2px" }}>
          <line x1="16.666%" y1="0" x2="50%" y2="100%" stroke="currentColor" strokeWidth="2" strokeDasharray="3" />
          <line x1="50%" y1="0" x2="50%" y2="100%" stroke="currentColor" strokeWidth="2" strokeDasharray="3" />
          <line x1="83.333%" y1="0" x2="50%" y2="100%" stroke="currentColor" strokeWidth="2" strokeDasharray="3" />
        </svg>

        {/* Split Flow: Quality (Left) vs Business Metrics (Right) */}
        <div className="grid grid-cols-2 gap-12 md:gap-24 w-full relative z-10 pt-2">
          
          {/* LEFT PATH: Quality & Advice */}
          <div className="flex flex-col items-center gap-4">
            {/* Layer 3: Quality Check */}
            <div 
              onMouseEnter={() => setHoveredNode("quality")}
              onMouseLeave={() => setHoveredNode(null)}
              className={`p-5 rounded-lg border w-full transition-all duration-300 cursor-pointer max-w-xs ${
                hoveredNode === "quality" || isPathActive("quality")
                  ? "border-amber-500/40 bg-amber-950/10 shadow-md shadow-amber-500/5"
                  : "border-slate-900 bg-slate-900/10"
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <AlertTriangle className="h-4.5 w-4.5 text-amber-400" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">Quality Issues</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-normal">
                Scans null fields, duplicate keys, and bounds anomalies.
              </p>
              <div className="mt-2 text-[10px] font-mono text-slate-500">
                Issues Found: {semanticIssues.length}
              </div>
            </div>

            <div className="w-[3px] h-10 bg-slate-800" />

            {/* Layer 4: Quality Recommendations */}
            <div 
              onMouseEnter={() => setHoveredNode("advice")}
              onMouseLeave={() => setHoveredNode(null)}
              className={`p-5 rounded-lg border w-full transition-all duration-300 cursor-pointer max-w-xs ${
                hoveredNode === "advice" || isPathActive("quality")
                  ? "border-purple-500/40 bg-purple-950/10 shadow-md shadow-purple-500/5"
                  : "border-slate-900 bg-slate-900/10"
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <Lightbulb className="h-4.5 w-4.5 text-purple-400" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400">Resolution Advice</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-normal">
                Actionable advice addressing null patterns and data cleaning.
              </p>
            </div>
          </div>

          {/* RIGHT PATH: Business Metrics & PBI Readiness */}
          <div className="flex flex-col items-center gap-4">
            {/* Layer 3: Business Metric Profiler */}
            <div 
              onMouseEnter={() => setHoveredNode("metrics")}
              onMouseLeave={() => setHoveredNode(null)}
              className={`p-5 rounded-lg border w-full transition-all duration-300 cursor-pointer max-w-xs ${
                hoveredNode === "metrics" || isPathActive("business")
                  ? "border-emerald-500/40 bg-emerald-950/10 shadow-md shadow-emerald-500/5"
                  : "border-slate-900 bg-slate-900/10"
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <Columns className="h-4.5 w-4.5 text-emerald-400" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Business Metrics</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-normal">
                Classifies measures vs dimensions for reporting safety.
              </p>
              <div className="mt-2 text-[10px] font-mono text-slate-500">
                Metrics Inferred: {semanticBusinessMetrics.length}
              </div>
            </div>

            <div className="w-[3px] h-10 bg-slate-800" />

            {/* Layer 4: Power BI Readiness */}
            <div 
              onMouseEnter={() => setHoveredNode("readiness")}
              onMouseLeave={() => setHoveredNode(null)}
              className={`p-5 rounded-lg border w-full transition-all duration-300 cursor-pointer max-w-xs ${
                hoveredNode === "readiness" || isPathActive("business")
                  ? "border-blue-500/40 bg-blue-950/10 shadow-md shadow-blue-500/5"
                  : "border-slate-900 bg-slate-900/10"
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <FileText className="h-4.5 w-4.5 text-blue-400" />
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400">Power BI Schema</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-normal">
                Infers fact/dimension tables and aggregates.
              </p>
              <div className="mt-2 text-[10px] font-mono text-slate-500">
                Index: {semanticPowerbiReadiness?.readiness_score || 0}%
              </div>
            </div>
          </div>

        </div>

        {/* Tree Connection SVG returning paths to Evaluation */}
        <svg className="w-full h-12 text-slate-800 pointer-events-none">
          <line x1="25%" y1="0" x2="50%" y2="100%" stroke="currentColor" strokeWidth="2" strokeDasharray="3" />
          <line x1="75%" y1="0" x2="50%" y2="100%" stroke="currentColor" strokeWidth="2" strokeDasharray="3" />
        </svg>

        {/* Layer 5: Evaluation Node */}
        <div 
          onMouseEnter={() => setHoveredNode("evaluation")}
          onMouseLeave={() => setHoveredNode(null)}
          className={`p-5 rounded-xl border text-center z-10 transition-all duration-300 cursor-pointer max-w-sm w-full ${
            hoveredNode === "evaluation" || isPathActive("evaluation")
              ? "border-emerald-500 bg-emerald-950/20 shadow-lg shadow-emerald-500/5 ring-1 ring-emerald-500/20"
              : "border-slate-800 bg-slate-900/30"
          }`}
        >
          <div className="flex items-center justify-center gap-2 mb-1">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Evaluation Audit</span>
          </div>
          <h4 className="font-bold text-sm text-slate-100">
            {evaluationResult ? `Analysis Rating: ${(evaluationResult.overall_analysis_score * 100).toFixed(0)}%` : "Awaiting Audit"}
          </h4>
          <span className="text-[10px] text-slate-500 font-mono">Truth Validation Grounded</span>
        </div>

      </div>

      {/* RIGHT: Detail Inspector Drawer */}
      <div className="p-5 rounded-xl border border-slate-900 bg-slate-950 flex flex-col gap-4 max-h-[500px] overflow-y-auto">
        <div className="flex items-center gap-2 border-b border-slate-900 pb-2.5">
          <Info className="h-4 w-4 text-indigo-400" />
          <h4 className="font-semibold text-xs text-slate-200 uppercase tracking-wider font-mono">Entity Inspector</h4>
        </div>

        {/* Conditional detailing depending on hovered node */}
        {hoveredNode === "dataset" && (
          <div className="flex flex-col gap-3 text-xs leading-normal">
            <span className="font-bold text-indigo-400">Dataset Entity Summary</span>
            <div><span className="text-slate-500">Filename:</span> <span className="text-slate-300 font-mono font-bold">{semanticDataset?.filename}</span></div>
            <div><span className="text-slate-500">File Size:</span> <span className="text-slate-300 font-mono font-bold">{semanticDataset?.file_size_bytes?.toLocaleString()} bytes</span></div>
            <div><span className="text-slate-500">Columns Detected:</span> <span className="text-slate-300 font-mono font-bold">{semanticDataset?.column_count}</span></div>
            <div><span className="text-slate-500">Rows Profiled:</span> <span className="text-slate-300 font-mono font-bold">{semanticDataset?.row_count?.toLocaleString()}</span></div>
          </div>
        )}

        {hoveredNode?.startsWith("col-") && (
          <div className="flex flex-col gap-3 text-xs leading-normal">
            <span className="font-bold text-indigo-400">Column Entity Detail</span>
            {(() => {
              const colName = hoveredNode.split("col-")[1];
              const col = columnsList.find((c: any) => c.name === colName);
              if (!col) return <span className="text-slate-500">Column details unavailable.</span>;
              return (
                <>
                  <div><span className="text-slate-500">Column Name:</span> <span className="text-slate-200 font-mono font-bold">{col.name}</span></div>
                  <div><span className="text-slate-500">Inferred Type:</span> <span className="text-slate-200 font-bold uppercase">{col.inferred_type}</span></div>
                  <div><span className="text-slate-500">Null Percentage:</span> <span className="text-slate-200 font-mono font-bold">{(col.null_percentage * 100).toFixed(1)}%</span></div>
                  <div><span className="text-slate-500">Unique Values:</span> <span className="text-slate-200 font-mono font-bold">{col.unique_values?.toLocaleString()}</span></div>
                </>
              );
            })()}
          </div>
        )}

        {hoveredNode === "quality" && (
          <div className="flex flex-col gap-3 text-xs leading-normal">
            <span className="font-bold text-amber-400">Quality Issues Log ({semanticIssues.length})</span>
            {semanticIssues.length === 0 ? (
              <span className="text-slate-500 italic">No quality anomalies registered on blackboard.</span>
            ) : (
              <div className="flex flex-col gap-2.5">
                {semanticIssues.slice(0, 3).map((issue: any, idx: number) => (
                  <div key={idx} className="border-l border-amber-500/30 pl-2 py-0.5 text-[11px]">
                    <span className="font-bold text-slate-300 block">{issue.title} ({issue.severity})</span>
                    <span className="text-slate-500 font-mono">Affected: {issue.affected_columns?.join(", ")}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {hoveredNode === "advice" && (
          <div className="flex flex-col gap-3 text-xs leading-normal">
            <span className="font-bold text-purple-400">Recommendation Entities</span>
            {semanticRecommendations.length === 0 ? (
              <span className="text-slate-500 italic">No resolution recommendations compiled.</span>
            ) : (
              <div className="flex flex-col gap-2.5">
                {semanticRecommendations.slice(0, 3).map((rec: any, idx: number) => (
                  <div key={idx} className="border-l border-purple-500/30 pl-2 py-0.5 text-[11px] text-slate-300">
                    {rec.recommendation_text}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {hoveredNode === "metrics" && (
          <div className="flex flex-col gap-3 text-xs leading-normal">
            <span className="font-bold text-emerald-400">Business Metrics Profile</span>
            {semanticBusinessMetrics.length === 0 ? (
              <span className="text-slate-500 italic">No aggregatable metrics classified.</span>
            ) : (
              <div className="flex flex-col gap-2">
                {semanticBusinessMetrics.slice(0, 4).map((bm: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center text-[11px] font-mono border-b border-slate-900 pb-1">
                    <span className="text-slate-300">{bm.column_name}</span>
                    <span className="text-emerald-400 font-bold">{bm.metric_type} ({bm.default_aggregation})</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {hoveredNode === "readiness" && (
          <div className="flex flex-col gap-3 text-xs leading-normal">
            <span className="font-bold text-blue-400">Power BI Schema Suggestions</span>
            <div><span className="text-slate-500">Readiness Score:</span> <span className="text-slate-200 font-mono font-bold">{semanticPowerbiReadiness?.readiness_score}%</span></div>
            <div><span className="text-slate-500">Status Rating:</span> <span className="text-slate-200 font-mono font-bold">{semanticPowerbiReadiness?.overall_rating_text}</span></div>
            <div className="flex flex-col gap-1 mt-1 border-t border-slate-900 pt-2 text-[11px]">
              <span className="font-bold text-slate-400 block mb-0.5">Star Schema Candidates:</span>
              <div><span className="text-slate-500">Facts:</span> <span className="text-slate-300 font-mono">{semanticPowerbiReadiness?.star_schema_suggestions?.fact_tables?.join(", ") || "None"}</span></div>
              <div><span className="text-slate-500">Dims:</span> <span className="text-slate-300 font-mono truncate block max-w-full" title={semanticPowerbiReadiness?.star_schema_suggestions?.dimension_tables?.join(", ")}>{semanticPowerbiReadiness?.star_schema_suggestions?.dimension_tables?.join(", ") || "None"}</span></div>
            </div>
          </div>
        )}

        {hoveredNode === "evaluation" && (
          <div className="flex flex-col gap-3 text-xs leading-normal">
            <span className="font-bold text-emerald-400">Evaluation Verification Details</span>
            {evaluationResult ? (
              <>
                <div><span className="text-slate-500">Overall Grade:</span> <span className="text-slate-200 font-mono font-bold">{(evaluationResult.overall_analysis_score * 100).toFixed(0)}%</span></div>
                <div><span className="text-slate-500">Completeness:</span> <span className="text-slate-300 font-mono font-bold">{Math.round(evaluationResult.evidence_completeness * 100)}%</span></div>
                <div><span className="text-slate-500">Recommendation Coverage:</span> <span className="text-slate-300 font-mono font-bold">{Math.round(evaluationResult.recommendation_coverage * 100)}%</span></div>
                <div><span className="text-slate-500">Agent Consensus:</span> <span className="text-slate-300 font-mono font-bold">{Math.round(evaluationResult.agent_agreement * 100)}%</span></div>
              </>
            ) : (
              <span className="text-slate-500 italic">Evaluation metrics pending completion.</span>
            )}
          </div>
        )}

        {!hoveredNode && (
          <div className="flex flex-col items-center justify-center py-12 text-center text-slate-500 italic text-[11px]">
            <span>Hover over any pipeline node to inspect its compiled semantic properties and trace parameters.</span>
          </div>
        )}

      </div>

    </div>
  );
}
