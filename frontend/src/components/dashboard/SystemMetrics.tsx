"use client";

import React, { useEffect, useState } from "react";
import { fetchHealth } from "@/lib/api";
import { HealthResponse } from "@/lib/types";
import {
  Server,
  Database,
  ShieldAlert,
  Cpu,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers
} from "lucide-react";

export default function SystemMetrics() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth);
  }, []);

  const isHealthy = health?.status === "operational";
  const isDbConnected = health?.database?.status === "connected";

  const metrics = [
    {
      title: "API GATEWAY (FASTAPI)",
      value: isHealthy ? "OPERATIONAL" : "DEGRADED",
      subtext: `v${health?.version ?? "1.0.0"} · /api/v1/health`,
      status: isHealthy ? "good" : "bad",
      icon: Server,
      color: "cyan",
    },
    {
      title: "FORENSIC DATABASE",
      value: (health?.database?.dialect?.toUpperCase() ?? "SQLITE"),
      subtext: isDbConnected ? "Relational Engine Connected" : "Connection Error",
      status: isDbConnected ? "good" : "warn",
      icon: Database,
      color: "emerald",
    },
    {
      title: "DIGITAL EVIDENCE VAULT",
      value: "SHA-256 READY",
      subtext: "RFC 8785 Canonical JSON Hash Engine",
      status: "good",
      icon: ShieldAlert,
      color: "blue",
    },
    {
      title: "AI ANOMALY PIPELINE",
      value: "ISOLATION FOREST",
      subtext: "14 Behavioral Heuristics Standby",
      status: "good",
      icon: Cpu,
      color: "purple",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((m) => {
        const Icon = m.icon;
        return (
          <div
            key={m.title}
            className="bg-[#0e1628] border border-[#1b2848] hover:border-cyan-500/40 rounded-lg p-4 transition-all duration-200"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-mono tracking-wider text-slate-400 font-semibold">
                {m.title}
              </span>
              <div
                className={`p-2 rounded-md ${
                  m.color === "cyan"
                    ? "bg-cyan-950/60 text-cyan-400"
                    : m.color === "emerald"
                    ? "bg-emerald-950/60 text-emerald-400"
                    : m.color === "blue"
                    ? "bg-blue-950/60 text-blue-400"
                    : "bg-purple-950/60 text-purple-400"
                }`}
              >
                <Icon className="w-4 h-4" />
              </div>
            </div>

            <div className="flex items-baseline space-x-2">
              <span className="text-xl font-bold font-mono tracking-tight text-white">
                {m.value}
              </span>
              {m.status === "good" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-amber-400" />
              )}
            </div>

            <p className="text-xs text-slate-400 mt-2 font-mono flex items-center space-x-1">
              <span>{m.subtext}</span>
            </p>
          </div>
        );
      })}
    </div>
  );
}
