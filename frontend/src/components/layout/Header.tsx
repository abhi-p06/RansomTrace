"use client";

import React, { useState, useEffect } from "react";
import { fetchHealth } from "@/lib/api";
import { HealthResponse } from "@/lib/types";
import {
  RefreshCw,
  Database,
  Server,
  ShieldCheck,
} from "lucide-react";

export default function Header() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [lastCheck, setLastCheck] = useState<string>("");

  const checkStatus = async () => {
    setLoading(true);
    try {
      const data = await fetchHealth();
      setHealth(data);
      setLastCheck(new Date().toLocaleTimeString());
    } catch {
      // Ignore health check network errors in background poll
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    fetchHealth()
      .then((data) => {
        if (isMounted) {
          setHealth(data);
          setLastCheck(new Date().toLocaleTimeString());
        }
      })
      .catch(() => {});

    const interval = setInterval(async () => {
      try {
        const data = await fetchHealth();
        if (isMounted) {
          setHealth(data);
          setLastCheck(new Date().toLocaleTimeString());
        }
      } catch {
        // Polling retry
      }
    }, 30000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const isBackendHealthy = health?.status === "operational";
  const isDbConnected = health?.database?.status === "connected";

  return (
    <header className="h-16 bg-[#0a0f1d]/90 backdrop-blur border-b border-[#1a2540] px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Breadcrumb / Title */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono uppercase text-slate-400">Environment:</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/40">
            PHASE 1 FOUNDATION
          </span>
        </div>
        <span className="text-slate-600">/</span>
        <div className="flex items-center space-x-1.5 text-xs text-slate-300 font-medium">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Forensic Sandboxed Mode</span>
        </div>
      </div>

      {/* Real-time Status Badges & Controls */}
      <div className="flex items-center space-x-3">
        {/* Backend API Health Pill */}
        <div
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-mono border ${
            isBackendHealthy
              ? "bg-emerald-950/40 text-emerald-300 border-emerald-800/60"
              : "bg-red-950/40 text-red-300 border-red-800/60"
          }`}
        >
          <Server className="w-3.5 h-3.5" />
          <span>API: {health?.status?.toUpperCase() ?? "CHECKING"}</span>
        </div>

        {/* Database Health Pill */}
        <div
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-mono border ${
            isDbConnected
              ? "bg-blue-950/40 text-blue-300 border-blue-800/60"
              : "bg-amber-950/40 text-amber-300 border-amber-800/60"
          }`}
          title={health?.database?.detail}
        >
          <Database className="w-3.5 h-3.5" />
          <span>DB: {health?.database?.dialect?.toUpperCase() ?? "UNKNOWN"}</span>
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isDbConnected ? "bg-emerald-400" : "bg-amber-400"
            }`}
          />
        </div>

        {/* Refresh Status Button */}
        <button
          onClick={checkStatus}
          disabled={loading}
          className="p-1.5 rounded hover:bg-[#16233d] text-slate-400 hover:text-white transition-all disabled:opacity-50"
          title={`Click to re-verify status (Last checked: ${lastCheck || "Never"})`}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
        </button>

        <div className="h-6 w-px bg-[#1a2540]" />

        {/* Investigator Profile */}
        <div className="flex items-center space-x-2 pl-2">
          <div className="w-7 h-7 rounded-full bg-[#16233d] border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-mono text-xs font-bold">
            CS
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-medium text-slate-200">Investigator</span>
            <span className="text-[10px] text-slate-400 font-mono">B.Tech Forensic Lab</span>
          </div>
        </div>
      </div>
    </header>
  );
}
