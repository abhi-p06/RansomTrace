"use client";

import React, { useState } from "react";
import Link from "next/link";
import { FolderPlus, Search, FileBadge, Terminal, CheckCircle2, ShieldAlert } from "lucide-react";
import { fetchHealth } from "@/lib/api";

export default function QuickActions() {
  const [testingConnection, setTestingConnection] = useState(false);
  const [diagnosticMessage, setDiagnosticMessage] = useState<string | null>(null);

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setDiagnosticMessage(null);
    try {
      const data = await fetchHealth();
      setDiagnosticMessage(
        `API: ${data.status.toUpperCase()} | DB: ${data.database.dialect.toUpperCase()} (${data.database.status})`
      );
    } catch {
      setDiagnosticMessage("Failed to reach API gateway.");
    } finally {
      setTestingConnection(false);
    }
  };

  return (
    <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg p-5">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#1b2848]">
        <div className="flex items-center space-x-2">
          <Terminal className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase font-mono">
            Investigator Command Actions
          </h2>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
          Phase 2 Active
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Action 1: Create / Manage Cases */}
        <div className="bg-[#121c33] border border-[#1e2f54] hover:border-cyan-500/40 p-4 rounded-md flex flex-col justify-between transition-all">
          <div>
            <div className="flex items-center space-x-2 text-cyan-400 mb-2">
              <FolderPlus className="w-5 h-5" />
              <span className="text-xs font-bold font-mono uppercase">Case Dossier Manager</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-3">
              Create and manage structured ransomware incident cases with relational database persistence and chain-of-custody logging.
            </p>
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-[#1e2f54]">
            <Link
              href="/cases"
              className="text-xs text-cyan-400 hover:text-cyan-300 font-mono inline-flex items-center space-x-1"
            >
              <span>Manage Cases →</span>
            </Link>
          </div>
        </div>

        {/* Action 2: Inspect WannaCry Dataset */}
        <div className="bg-[#121c33] border border-[#1e2f54] hover:border-cyan-500/40 p-4 rounded-md flex flex-col justify-between transition-all">
          <div>
            <div className="flex items-center space-x-2 text-emerald-400 mb-2">
              <Search className="w-5 h-5" />
              <span className="text-xs font-bold font-mono uppercase">WannaCry 2017 Dossier</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-3">
              Inspect the primary WannaCry extortion investigation dossier stored in the relational database.
            </p>
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-[#1e2f54]">
            <Link
              href="/cases/RT-2017-WCRY"
              className="text-xs text-emerald-400 hover:text-emerald-300 font-mono inline-flex items-center space-x-1"
            >
              <span>Open Dossier (RT-2017-WCRY) →</span>
            </Link>
          </div>
        </div>

        {/* Action 3: Live Diagnostics */}
        <div className="bg-[#121c33] border border-[#1e2f54] hover:border-cyan-500/40 p-4 rounded-md flex flex-col justify-between transition-all">
          <div>
            <div className="flex items-center space-x-2 text-purple-400 mb-2">
              <FileBadge className="w-5 h-5" />
              <span className="text-xs font-bold font-mono uppercase">Subsystem Diagnostics</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-3">
              Validate runtime interconnectivity across FastAPI Gateway, PostgreSQL/SQLite ORM sessions, and Evidence directory.
            </p>
          </div>
          <div className="pt-2 border-t border-[#1e2f54]">
            <button
              onClick={handleTestConnection}
              disabled={testingConnection}
              className="w-full bg-[#1b2a4a] hover:bg-cyan-600 text-cyan-300 hover:text-white text-xs font-mono py-1.5 px-3 rounded transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{testingConnection ? "Pinging Services..." : "Run Gateway Ping Test"}</span>
            </button>
            {diagnosticMessage && (
              <div className="mt-2 text-[10px] font-mono text-cyan-300 bg-cyan-950/70 p-1.5 rounded border border-cyan-800/40 text-center">
                {diagnosticMessage}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
