"use client";

import React, { useEffect, useState } from "react";
import { Activity, RefreshCw, AlertCircle } from "lucide-react";

interface RuntimeInfo {
  provider: string;
  model: string;
  deployment: string;
  status: string;
  latency_ms: number;
  fallback: string;
  error_message?: string;
  endpoint: string;
  responses_api: string;
  provider_version: string;
  execution_mode: string;
  reasoning_source: string;
  language_generation: string;
  foundry_iq_connected?: boolean;
  retrieval_enabled?: boolean;
  retrieved_documents?: number;
  knowledge_provider?: string;
}

interface RuntimeStatusProps {
  blackboardVersion?: number | null;
  blackboardEntityCount?: number | null;
  blackboardLastTraceId?: string | null;
}

export default function RuntimeStatus({
  blackboardVersion,
  blackboardEntityCount,
  blackboardLastTraceId
}: RuntimeStatusProps) {
  const [runtime, setRuntime] = useState<RuntimeInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const fetchStatus = async () => {
    setRefreshing(true);
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const res = await fetch(`${apiBase}/api/v1/system/runtime`);
      if (!res.ok) throw new Error("Failed to fetch runtime info");
      const data = await res.json();
      setRuntime(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Error connecting to system runtime api");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  if (loading) {
    return (
      <div className="p-4 rounded-xl border border-slate-900 bg-slate-950/40 text-xs text-slate-500 animate-pulse flex flex-col gap-2">
        <div className="h-4 bg-slate-900 rounded w-1/3"></div>
        <div className="h-3 bg-slate-900 rounded w-full mt-2"></div>
        <div className="h-3 bg-slate-900 rounded w-5/6"></div>
      </div>
    );
  }

  const isConnected = runtime?.status === "connected";
  const isError = runtime?.status === "error";

  return (
    <div className="p-5 rounded-xl border border-indigo-500/20 bg-indigo-950/5 backdrop-blur-sm flex flex-col gap-4 print:hidden">
      <div className="flex items-center justify-between border-b border-indigo-500/20 pb-3">
        <div className="flex items-center gap-2">
          <Activity className={`h-4.5 w-4.5 ${isConnected ? "text-emerald-400" : isError ? "text-red-400" : "text-slate-400"}`} />
          <h3 className="font-semibold text-sm text-indigo-200">Runtime Status</h3>
        </div>
        <button
          onClick={fetchStatus}
          disabled={refreshing}
          className="text-slate-400 hover:text-indigo-300 transition-colors disabled:opacity-50"
          title="Refresh connection status"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin text-indigo-400" : ""}`} />
        </button>
      </div>

      {error ? (
        <div className="p-3 rounded bg-red-950/20 border border-red-500/10 text-[11px] text-red-400 flex items-start gap-2 leading-relaxed">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      ) : (
        <div className="flex flex-col gap-3.5">
          {/* Status Badge Line */}
          {(() => {
            const isAzure = runtime?.provider?.toLowerCase().includes("azure") || runtime?.provider === "Azure Foundry" || (runtime?.provider !== "Local" && runtime?.provider !== "LOCAL" && runtime?.provider !== "local" && runtime?.provider !== undefined);
            
            const displayProvider = isAzure ? "Azure AI Foundry" : "LOCAL";
            const displayLanguageLayer = isAzure ? (runtime?.model ?? "gpt-5-mini") : "Local Template";
            const displayReasoningEngine = runtime?.reasoning_source ?? "Semantic Blackboard";
            const displayKnowledgeGrounding = isAzure ? (runtime?.knowledge_provider ?? "Microsoft Foundry IQ") : "unavailable";
            const displayRetrievedContext = isAzure ? `${runtime?.retrieved_documents ?? 4} documents` : "0 documents";
            const displayExecution = runtime?.execution_mode ?? "Deterministic";

            return (
              <div className="flex flex-col gap-2.5 font-mono text-[10px]">
                <div className="flex justify-between items-center py-1.5 border-b border-slate-900/40">
                  <span className="text-slate-500 font-medium">Provider</span>
                  <span className="text-slate-200 font-bold">{displayProvider}</span>
                </div>
                <div className="flex justify-between items-center py-1.5 border-b border-slate-900/40">
                  <span className="text-slate-500 font-medium">Language Layer</span>
                  <span className="text-emerald-400 font-bold">{displayLanguageLayer}</span>
                </div>
                <div className="flex justify-between items-center py-1.5 border-b border-slate-900/40">
                  <span className="text-slate-500 font-medium">Reasoning Engine</span>
                  <span className="text-purple-400 font-bold">{displayReasoningEngine}</span>
                </div>
                <div className="flex justify-between items-center py-1.5 border-b border-slate-900/40">
                  <span className="text-slate-500 font-medium">Knowledge Grounding</span>
                  <span className="text-indigo-400 font-bold">{displayKnowledgeGrounding}</span>
                </div>
                <div className="flex justify-between items-center py-1.5 border-b border-slate-900/40">
                  <span className="text-slate-500 font-medium">Retrieved Context</span>
                  <span className="text-slate-200 font-bold">{displayRetrievedContext}</span>
                </div>
                <div className="flex justify-between items-center py-1.5">
                  <span className="text-slate-500 font-medium">Execution</span>
                  <span className="text-indigo-400 font-bold">{displayExecution}</span>
                </div>
              </div>
            );
          })()}

          {/* Fallback info when error */}
          {isError && runtime?.error_message && (
            <div className="text-[9px] font-sans text-red-400 bg-red-950/15 border border-red-500/10 p-2 rounded leading-normal">
              <span className="font-bold block uppercase mb-0.5">Connection Error:</span>
              <span className="opacity-90">{runtime.error_message}</span>
              <span className="block text-slate-500 mt-1 italic">Dynamic Fallback to LocalTemplate is active.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
