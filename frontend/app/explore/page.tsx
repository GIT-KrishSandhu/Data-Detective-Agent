"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  FileSpreadsheet, 
  Database, 
  Layers, 
  Hash, 
  HelpCircle,
  Clock
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import WorkflowViewer from "@/components/workflow-viewer";

interface ColumnSchema {
  name: string;
  inferred_type: string;
  null_count: number;
  null_percentage: number;
  unique_values: number;
  sample_values: any[];
}

interface DatasetPreview {
  columns: string[];
  inferred_types: Record<string, string>;
  rows: Record<string, any>[];
}

interface DatasetMetadata {
  filename: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  detected_type: string;
  analysis_goal?: string | null;
}

export default function ExplorePage() {
  const searchParams = useSearchParams();
  const datasetId = searchParams.get("id");

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<DatasetMetadata | null>(null);
  const [schemaInfo, setSchemaInfo] = useState<ColumnSchema[]>([]);
  const [previewData, setPreviewData] = useState<DatasetPreview | null>(null);
  const [activeTab, setActiveTab] = useState<"schema" | "preview">("schema");

  // Workflow states
  const [workflowSteps, setWorkflowSteps] = useState<string[]>([]);
  const [plannerReasoning, setPlannerReasoning] = useState<string>("");
  const [plannerConfidence, setPlannerConfidence] = useState<number>(0);
  const [workflowCurrentStep, setWorkflowCurrentStep] = useState<string>("idle");

  useEffect(() => {
    if (!datasetId) {
      setError("No dataset ID provided. Please upload a dataset first.");
      setLoading(false);
      return;
    }

    const fetchDatasetDetails = async () => {
      setLoading(true);
      setError(null);
      
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      try {
        // Fetch full dataset record metadata
        const detailsRes = await fetch(`${apiBase}/api/v1/datasets/${datasetId}`);
        if (!detailsRes.ok) {
          throw new Error("Failed to fetch dataset details.");
        }
        const dsData = await detailsRes.json();
        
        setMetadata({
          filename: dsData.metadata.filename,
          file_size_bytes: dsData.metadata.file_size_bytes,
          row_count: dsData.metadata.row_count,
          column_count: dsData.metadata.column_count,
          detected_type: dsData.metadata.detected_type,
          analysis_goal: dsData.metadata.analysis_goal
        });

        // Set preview and schema states
        setPreviewData(dsData.preview_data);
        setSchemaInfo(dsData.schema_info);

        // If analysis goal has been set, trigger Planner Node
        if (dsData.metadata.analysis_goal) {
          const planRes = await fetch(`${apiBase}/api/v1/agents/analyze`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              dataset_id: datasetId,
              goal: dsData.metadata.analysis_goal
            })
          });

          if (planRes.ok) {
            const plan = await planRes.json();
            setWorkflowSteps(plan.workflow_steps);
            setPlannerReasoning(plan.reasoning);
            setPlannerConfidence(plan.confidence);
            setWorkflowCurrentStep("Planner Complete");
          }
        }

      } catch (err: any) {
        setError(err.message || "Could not retrieve dataset details from server.");
      } finally {
        setLoading(false);
      }
    };

    fetchDatasetDetails();
  }, [datasetId]);

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getTypeBadgeColor = (type: string): string => {
    switch (type.toLowerCase()) {
      case "integer":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "float":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
      case "boolean":
        return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      case "datetime":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/20";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center gap-4">
        <div className="h-10 w-10 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
        <p className="text-sm text-slate-400">Loading dataset explorer metadata...</p>
      </div>
    );
  }

  if (error || !metadata || !previewData) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center gap-4 px-6 text-center">
        <div className="h-12 w-12 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
          <HelpCircle className="h-6 w-6" />
        </div>
        <h2 className="text-xl font-bold text-slate-200">Unable to Load Dataset</h2>
        <p className="text-sm text-slate-400 max-w-md">{error || "The selected dataset could not be found."}</p>
        <Link href="/">
          <Button className="bg-indigo-600 hover:bg-indigo-500 text-white mt-2">
            <ArrowLeft className="h-4 w-4 mr-2" /> Back to Dashboard
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white pb-16">
      {/* Navbar */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-slate-400 hover:text-slate-200 transition-colors">
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div className="h-8 w-8 rounded bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center">
              <Database className="h-4.5 w-4.5 text-white" />
            </div>
            <div>
              <span className="font-semibold text-sm block leading-none">{metadata.filename}</span>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Dataset Ingestion Explorer</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/">
              <Button variant="ghost" className="text-xs text-slate-400 hover:text-slate-100 hover:bg-slate-900">
                Workspace
              </Button>
            </Link>
            <span className="h-4 w-px bg-slate-900" />
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-900 text-emerald-400 flex items-center gap-1.5 font-semibold">
              <span className="h-1.5 w-1.5 bg-emerald-400 rounded-full" />
              Verified Ingest
            </span>
          </div>
        </div>
      </header>

      {/* Content Container */}
      <main className="max-w-7xl mx-auto px-6 py-8 flex flex-col gap-8">
        
        {/* Metadata Banner Details */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 p-6 rounded-xl border border-slate-900 bg-slate-900/20 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-indigo-950 border border-indigo-900/40 text-indigo-400 flex items-center justify-center shrink-0">
              <FileSpreadsheet className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs text-slate-500 block">Filename</span>
              <span className="text-sm font-semibold text-slate-200 block truncate max-w-[180px]" title={metadata.filename}>
                {metadata.filename}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 border-t md:border-t-0 md:border-l border-slate-900 pt-4 md:pt-0 md:pl-6">
            <div className="h-10 w-10 rounded-lg bg-emerald-950 border border-emerald-900/40 text-emerald-400 flex items-center justify-center shrink-0">
              <Layers className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs text-slate-500 block">Dimensions</span>
              <span className="text-sm font-semibold text-slate-200 block">
                {metadata.row_count.toLocaleString()} rows × {metadata.column_count} columns
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 border-t md:border-t-0 md:border-l border-slate-900 pt-4 md:pt-0 md:pl-6">
            <div className="h-10 w-10 rounded-lg bg-cyan-950 border border-cyan-900/40 text-cyan-400 flex items-center justify-center shrink-0">
              <Hash className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs text-slate-500 block">File Size</span>
              <span className="text-sm font-semibold text-slate-200 block">
                {formatBytes(metadata.file_size_bytes)}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3 border-t md:border-t-0 md:border-l border-slate-900 pt-4 md:pt-0 md:pl-6">
            <div className="h-10 w-10 rounded-lg bg-amber-950 border border-amber-900/40 text-amber-400 flex items-center justify-center shrink-0">
              <Clock className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs text-slate-500 block">Ingestion Type</span>
              <span className="text-sm font-semibold text-slate-200 block uppercase">
                {metadata.detected_type} format
              </span>
            </div>
          </div>
        </section>

        {/* Workflow Viewer Panel */}
        {metadata.analysis_goal && (
          <WorkflowViewer
            steps={workflowSteps}
            currentStep={workflowCurrentStep}
            reasoning={plannerReasoning}
            confidence={plannerConfidence}
          />
        )}

        {/* Tab Controls */}
        <div className="flex items-center gap-2 border-b border-slate-900 pb-px">
          <button
            onClick={() => setActiveTab("schema")}
            className={`px-4 py-2 border-b-2 text-sm font-medium transition-all ${
              activeTab === "schema"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Schema Discovery Table
          </button>
          <button
            onClick={() => setActiveTab("preview")}
            className={`px-4 py-2 border-b-2 text-sm font-medium transition-all ${
              activeTab === "preview"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Raw Dataset Preview (First 20 Rows)
          </button>
        </div>

        {/* Tab Panels */}
        <div className="rounded-xl border border-slate-900 bg-slate-950 overflow-hidden">
          {activeTab === "schema" ? (
            /* SCHEMA DISCOVERY TABLE PANEL */
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-slate-900/50">
                  <TableRow className="hover:bg-transparent border-slate-900">
                    <TableHead className="text-slate-300 font-semibold w-[20%]">Column Name</TableHead>
                    <TableHead className="text-slate-300 font-semibold w-[12%]">Inferred Type</TableHead>
                    <TableHead className="text-slate-300 font-semibold w-[15%]">Null Count</TableHead>
                    <TableHead className="text-slate-300 font-semibold w-[15%]">Null Percentage</TableHead>
                    <TableHead className="text-slate-300 font-semibold w-[15%]">Unique Values</TableHead>
                    <TableHead className="text-slate-300 font-semibold w-[23%]">Sample Values</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {schemaInfo.map((col, index) => (
                    <TableRow key={index} className="border-slate-900 hover:bg-slate-900/20">
                      <TableCell className="font-mono text-xs text-slate-200 font-semibold">{col.name}</TableCell>
                      <TableCell>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded border text-[10px] uppercase font-bold tracking-wide ${getTypeBadgeColor(col.inferred_type)}`}>
                          {col.inferred_type}
                        </span>
                      </TableCell>
                      <TableCell className="text-xs text-slate-300 font-mono">{col.null_count.toLocaleString()}</TableCell>
                      <TableCell className="text-xs text-slate-300 font-mono">
                        {(col.null_percentage * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell className="text-xs text-slate-300 font-mono">{col.unique_values.toLocaleString()}</TableCell>
                      <TableCell className="text-xs text-slate-400 font-mono truncate max-w-[250px]" title={col.sample_values.join(", ")}>
                        {col.sample_values.map((s) => (s === null ? "null" : String(s))).join(", ")}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            /* RAW DATASET PREVIEW TABLE PANEL */
            <div className="overflow-x-auto">
              <Table>
                <TableHeader className="bg-slate-900/50">
                  <TableRow className="hover:bg-transparent border-slate-900">
                    <TableHead className="text-slate-400 font-semibold text-center w-[60px]">#</TableHead>
                    {previewData.columns.map((col, idx) => (
                      <TableHead key={idx} className="text-slate-300 font-semibold font-mono text-xs">
                        <div className="flex flex-col">
                          <span>{col}</span>
                          <span className="text-[9px] text-slate-500 uppercase tracking-wider mt-0.5">
                            {previewData.inferred_types[col]}
                          </span>
                        </div>
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {previewData.rows.map((row, rowIdx) => (
                    <TableRow key={rowIdx} className="border-slate-900 hover:bg-slate-900/20">
                      <TableCell className="text-center font-mono text-slate-600 text-xs border-r border-slate-900/80">
                        {rowIdx + 1}
                      </TableCell>
                      {previewData.columns.map((col, colIdx) => (
                        <TableCell key={colIdx} className="text-xs text-slate-300 font-mono whitespace-nowrap">
                          {row[col] === null ? (
                            <span className="text-red-500/60 italic">null</span>
                          ) : (
                            String(row[col])
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
