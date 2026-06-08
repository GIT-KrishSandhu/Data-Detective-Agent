"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { 
  ShieldAlert, 
  FileSpreadsheet, 
  BarChart3, 
  Sparkles, 
  ArrowRight, 
  Database, 
  Play, 
  Terminal,
  Activity,
  Search,
  Loader2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import UploadDataset from "@/components/upload-dataset";

export default function Home() {
  const router = useRouter();
  const [selectedGoal, setSelectedGoal] = useState<string>("quality");
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [uploadedMeta, setUploadedMeta] = useState<any | null>(null);
  const [isLaunching, setIsLaunching] = useState<boolean>(false);

  const goals = [
    {
      id: "quality",
      title: "Data Quality Audit",
      description: "Inspect datasets for anomalies, missing fields, schema mismatches, and integrity issues.",
      icon: ShieldAlert,
      color: "from-amber-500/20 to-red-500/20 border-amber-500/30 text-amber-400",
    },
    {
      id: "eda",
      title: "Exploratory Data Analysis",
      description: "Understand patterns, distributions, statistical measures, and structural insights.",
      icon: BarChart3,
      color: "from-blue-500/20 to-indigo-500/20 border-blue-500/30 text-blue-400",
    },
    {
      id: "summary",
      title: "Executive Summary",
      description: "Produce evidence-backed summaries, key takeaways, and metric highlights for stakeholders.",
      icon: Sparkles,
      color: "from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400",
    },
    {
      id: "powerbi",
      title: "Power BI Preparation",
      description: "Shape datasets, suggest star schemas, clean column names, and verify normalization for reports.",
      icon: FileSpreadsheet,
      color: "from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400",
    },
  ];

  const handleUploadSuccess = (data: any) => {
    setDatasetId(data.dataset_id);
    setUploadedMeta(data.metadata);
  };

  const handleLaunchAnalysis = async () => {
    if (!datasetId) return;
    setIsLaunching(true);

    const goalMap: Record<string, string> = {
      quality: "Data Quality Audit",
      eda: "Exploratory Data Analysis",
      summary: "Executive Summary",
      powerbi: "Power BI Preparation"
    };

    const targetGoal = goalMap[selectedGoal] || "Data Quality Audit";

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiBase}/api/v1/agents/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          dataset_id: datasetId,
          goal: targetGoal
        })
      });

      if (!response.ok) {
        const errDetails = await response.json();
        throw new Error(errDetails.detail || "Analysis trigger failed.");
      }

      // Transition to exploration dashboard once plan is generated
      router.push(`/explore?id=${datasetId}&launched=true`);
    } catch (err: any) {
      alert(err.message || "An unexpected error occurred during analysis setup.");
    } finally {
      setIsLaunching(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white overflow-x-hidden relative">
      {/* Background Gradient Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-purple-500/10 blur-[140px] pointer-events-none" />
      
      {/* Navbar */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Database className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="font-semibold text-lg bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-slate-200">Data Detective Agent</span>
              <span className="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-400 border border-indigo-900">v1.0 (Ingestion)</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-slate-400">
            <a href="#features" className="hover:text-slate-100 transition-colors">Features</a>
            <a href="#agents" className="hover:text-slate-100 transition-colors">Agents League</a>
            <a href="#docs" className="hover:text-slate-100 transition-colors">Documentation</a>
            <Button variant="outline" className="border-slate-800 bg-slate-900/50 hover:bg-slate-900 hover:text-white text-slate-300">
              System Health
            </Button>
          </nav>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-12 flex flex-col gap-12">
        {/* Hero Section */}
        <section className="text-center max-w-3xl mx-auto flex flex-col gap-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/50 border border-indigo-800/40 text-indigo-400 text-xs w-fit mx-auto">
            <Sparkles className="h-3 w-3" />
            <span>Built for Microsoft Agents League Hackathon</span>
          </div>
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400 leading-tight">
            Evidence-First Multi-Agent Data Readiness
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed">
            Upload your dataset, select an analytical objective, and let a network of coordinate-driven agents plan, audit, clean, and generate report outputs directly traceable to raw data.
          </p>
        </section>

        {/* Core Workspace Scaffolding */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start mt-4">
          {/* Controls Panel */}
          <div className="lg:col-span-2 flex flex-col gap-8">
            {/* Step 1: Upload */}
            <div className="p-6 rounded-xl border border-slate-900 bg-slate-950/20 backdrop-blur-sm flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <span className="h-6 w-6 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-xs font-bold text-slate-400">1</span>
                <h3 className="font-semibold text-lg">Upload Dataset</h3>
              </div>

              <UploadDataset onUploadSuccess={handleUploadSuccess} />
            </div>

            {/* Step 2: Select Goal */}
            <div className="p-6 rounded-xl border border-slate-900 bg-slate-950/20 backdrop-blur-sm flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <span className="h-6 w-6 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-xs font-bold text-slate-400">2</span>
                <h3 className="font-semibold text-lg">Define Analytical Goal</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {goals.map((g) => {
                  const Icon = g.icon;
                  const isSelected = selectedGoal === g.id;
                  return (
                    <div
                      key={g.id}
                      onClick={() => setSelectedGoal(g.id)}
                      className={`p-4 rounded-lg border text-left cursor-pointer transition-all flex flex-col justify-between gap-3 group relative overflow-hidden ${
                        isSelected 
                          ? `bg-slate-900 border-indigo-500 shadow-md shadow-indigo-500/5` 
                          : "bg-slate-950/40 border-slate-900 hover:border-slate-800"
                      }`}
                    >
                      <div className={`absolute top-0 right-0 w-16 h-16 bg-gradient-to-br ${g.color} opacity-0 group-hover:opacity-100 transition-opacity blur-lg pointer-events-none`} />
                      <div className="flex items-center justify-between z-10">
                        <div className={`h-8 w-8 rounded-lg flex items-center justify-center border ${
                          isSelected ? "bg-indigo-950 border-indigo-800/40 text-indigo-400" : "bg-slate-900 border-slate-800 text-slate-400"
                        }`}>
                          <Icon className="h-4 w-4" />
                        </div>
                        {isSelected && (
                          <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-400 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-900">
                            Selected
                          </span>
                        )}
                      </div>
                      <div className="z-10">
                        <h4 className="font-semibold text-sm text-slate-200">{g.title}</h4>
                        <p className="text-xs text-slate-400 mt-1 leading-relaxed">{g.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="mt-4 pt-4 border-t border-slate-900 flex justify-end gap-3">
                {datasetId && (
                  <Link href={`/explore?id=${datasetId}`}>
                    <Button 
                      variant="outline" 
                      className="border-slate-800 bg-slate-900/50 hover:bg-slate-900 hover:text-white text-slate-300 font-medium"
                    >
                      <Search className="h-4 w-4 mr-2" />
                      Explore Ingested Schema
                    </Button>
                  </Link>
                )}
                <Button 
                  disabled={!datasetId || isLaunching} 
                  onClick={handleLaunchAnalysis}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-lg shadow-indigo-500/20 disabled:bg-slate-900 disabled:text-slate-600 disabled:shadow-none min-w-[200px]"
                >
                  {isLaunching ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Planning Workflows...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Launch Agents Analysis
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>

          {/* Console / Monitoring Panel */}
          <div className="flex flex-col gap-6">
            <div className="p-6 rounded-xl border border-slate-900 bg-slate-950/40 backdrop-blur-sm flex flex-col gap-4 h-full">
              <div className="flex items-center justify-between border-b border-slate-900 pb-3">
                <div className="flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-indigo-400" />
                  <h3 className="font-semibold text-sm text-slate-300">Agent Network Activity</h3>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className={`h-2 w-2 rounded-full ${datasetId ? "bg-indigo-500 animate-pulse" : "bg-slate-700"}`} />
                  <span className={`text-[10px] uppercase tracking-wider font-semibold ${datasetId ? "text-indigo-400" : "text-slate-500"}`}>
                    {datasetId ? "Awaiting Agent Launch" : "Idle"}
                  </span>
                </div>
              </div>

              {/* Log stream placeholder */}
              <div className="flex-1 bg-slate-950 rounded-lg p-4 font-mono text-xs text-slate-400 flex flex-col gap-3 min-h-[300px] border border-slate-900 overflow-y-auto">
                <div className="text-slate-600">-- Data Detective Agent System Ingestion --</div>
                <div className="text-indigo-400">[System] Ready to accept spreadsheet upload.</div>
                <div className="text-slate-500">[System] CORS allowed on http://localhost:3000</div>
                
                {datasetId && (
                  <>
                    <div className="text-emerald-400">[Ingest] Dataset saved to disk storage.</div>
                    <div className="text-slate-300">[Ingest] Unique ID: {datasetId}</div>
                    <div className="text-slate-300">[Ingest] Discovered {uploadedMeta?.column_count} columns across {uploadedMeta?.row_count} rows.</div>
                    <div className="text-indigo-400">[System] Awaiting trigger events to execute Multi-Agent Planner chain.</div>
                  </>
                )}
              </div>

              {/* Quick Info Box */}
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-900 flex flex-col gap-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                  <Activity className="h-3.5 w-3.5 text-indigo-400" />
                  <span>Agent Core Values</span>
                </div>
                <ul className="text-[11px] text-slate-400 flex flex-col gap-1 list-disc pl-4 leading-normal">
                  <li>Traceability: No unsupported claims</li>
                  <li>Evidence-first: Every chart has query tracking</li>
                  <li>Safety: Edits require human-in-the-loop approvals</li>
                  <li>No forecasting: Descriptive analysis only</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 mt-16 py-8 text-center text-xs text-slate-500">
        <p>© 2026 Data Detective Agent • Prepared for the Microsoft Agents League Hackathon</p>
      </footer>
    </div>
  );
}
