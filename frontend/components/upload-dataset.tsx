"use client";

import React, { useState, useRef } from "react";
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface UploadDatasetProps {
  onUploadSuccess: (data: any) => void;
}

export default function UploadDataset({ onUploadSuccess }: UploadDatasetProps) {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [datasetResponse, setDatasetResponse] = useState<any | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    setDatasetResponse(null);

    const ext = selectedFile.name.split(".").pop()?.toLowerCase();
    if (ext !== "csv" && ext !== "xlsx" && ext !== "xls") {
      setError("Unsupported file format. Please upload a CSV or Excel spreadsheet.");
      return;
    }

    const maxSize = 50 * 1024 * 1024; // 50MB
    if (selectedFile.size > maxSize) {
      setError("File exceeds the maximum limit of 50 MB.");
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);
    setUploadProgress(15);

    const formData = new FormData();
    formData.append("file", file);

    // Simulate progress while performing network request
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 85) {
          clearInterval(progressInterval);
          return 85;
        }
        return prev + 10;
      });
    }, 150);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiBase}/api/v1/datasets/upload`, {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload failed. Please check file formatting.");
      }

      setUploadProgress(100);
      const data = await response.json();
      
      setTimeout(() => {
        setDatasetResponse(data);
        setIsUploading(false);
        onUploadSuccess(data);
      }, 500);

    } catch (err: any) {
      clearInterval(progressInterval);
      setIsUploading(false);
      setUploadProgress(0);
      setError(err.message || "An unexpected error occurred during ingestion.");
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="flex flex-col gap-6 w-full">
      {/* Upload Box */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={!isUploading && !datasetResponse ? triggerFileInput : undefined}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all relative overflow-hidden ${
          dragActive 
            ? "border-indigo-500 bg-indigo-500/10 scale-[1.01]" 
            : file 
              ? "border-indigo-500/50 bg-indigo-950/20" 
              : "border-slate-800 hover:border-slate-700 bg-slate-950/40 hover:bg-slate-900/10 cursor-pointer"
        } ${isUploading ? "pointer-events-none opacity-80" : ""}`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".csv,.xlsx,.xls"
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="h-10 w-10 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
            <div className="w-full max-w-xs bg-slate-900 rounded-full h-1.5 overflow-hidden">
              <div 
                className="bg-indigo-500 h-full transition-all duration-300 rounded-full"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-sm font-medium text-slate-300">Uploading {file?.name} ({uploadProgress}%)</p>
            <p className="text-xs text-slate-500">Extracting columns & profiling metadata...</p>
          </div>
        ) : datasetResponse ? (
          <div className="flex flex-col items-center gap-3 py-4 text-emerald-400">
            <div className="h-12 w-12 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div>
              <p className="font-semibold text-slate-200">Ingestion Complete</p>
              <p className="text-xs text-slate-500 mt-1">{file?.name}</p>
            </div>
          </div>
        ) : file ? (
          <div className="flex flex-col items-center gap-4 py-4">
            <div className="h-12 w-12 rounded-lg bg-indigo-950 flex items-center justify-center text-indigo-400 border border-indigo-900">
              <FileSpreadsheet className="h-6 w-6" />
            </div>
            <div>
              <p className="font-medium text-slate-200">{file.name}</p>
              <p className="text-xs text-slate-500 mt-1">{formatBytes(file.size)}</p>
            </div>
            <div className="flex gap-3 mt-2" onClick={(e) => e.stopPropagation()}>
              <Button 
                onClick={handleUpload}
                className="bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 text-xs px-4"
              >
                Confirm & Process
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setFile(null)}
                className="border-slate-800 bg-slate-900 text-slate-300 hover:text-white text-xs px-4"
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="h-12 w-12 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400">
              <Upload className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-200">Drag & drop your dataset here, or click to browse</p>
              <p className="text-xs text-slate-500 mt-1">Supports CSV, XLSX up to 50MB</p>
            </div>
          </div>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-lg bg-red-500/5 border border-red-500/20 flex items-start gap-3 text-red-400 text-sm">
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold block text-slate-200">Ingestion Failed</span>
            <span className="text-xs mt-0.5 text-red-400/90">{error}</span>
          </div>
        </div>
      )}

      {/* Dataset Summary (After upload success) */}
      {datasetResponse && (
        <div className="p-6 rounded-xl border border-slate-900 bg-slate-900/30 backdrop-blur-sm flex flex-col gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
          <div className="flex items-center justify-between border-b border-slate-900 pb-3">
            <h3 className="font-semibold text-sm text-slate-200">Dataset Summary Details</h3>
            <span className="text-[10px] bg-indigo-950 border border-indigo-900 text-indigo-400 px-2 py-0.5 rounded uppercase font-bold tracking-wider">
              {datasetResponse.metadata.detected_type}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-900 text-center">
              <span className="text-xs text-slate-500 block">Rows</span>
              <span className="text-xl font-bold text-slate-200 mt-1 block">
                {datasetResponse.metadata.row_count.toLocaleString()}
              </span>
            </div>
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-900 text-center">
              <span className="text-xs text-slate-500 block">Columns</span>
              <span className="text-xl font-bold text-slate-200 mt-1 block">
                {datasetResponse.metadata.column_count.toLocaleString()}
              </span>
            </div>
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-900 text-center">
              <span className="text-xs text-slate-500 block">File Size</span>
              <span className="text-xl font-bold text-slate-200 mt-1 block text-ellipsis overflow-hidden whitespace-nowrap">
                {formatBytes(datasetResponse.metadata.file_size_bytes)}
              </span>
            </div>
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-900 text-center">
              <span className="text-xs text-slate-500 block">Detected Types</span>
              <span className="text-xs font-semibold text-slate-300 mt-2 block overflow-hidden text-ellipsis whitespace-nowrap">
                {Array.from(new Set(Object.values(datasetResponse.preview_data.inferred_types))).join(", ") || "None"}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
