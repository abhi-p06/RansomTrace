import React from "react";
import Link from "next/link";
import { ArrowLeft, Construction, Clock, ShieldCheck } from "lucide-react";

interface PhasePlaceholderProps {
  title: string;
  moduleName: string;
  phase: string;
  description: string;
  deliverables: string[];
}

export default function PhasePlaceholder({
  title,
  moduleName,
  phase,
  description,
  deliverables,
}: PhasePlaceholderProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link
        href="/"
        className="inline-flex items-center space-x-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-mono"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Return to SOC Command Center</span>
      </Link>

      <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#1b2848]">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-cyan-950/60 text-cyan-400 border border-cyan-800/40">
              <Construction className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[11px] font-mono text-cyan-400 uppercase tracking-widest block">
                {moduleName} · {phase}
              </span>
              <h1 className="text-xl font-bold text-white tracking-wide">{title}</h1>
            </div>
          </div>
          <span className="text-xs font-mono bg-cyan-950/70 border border-cyan-700/50 text-cyan-300 px-3 py-1 rounded">
            Scheduled Milestone
          </span>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed mb-6 font-sans">
          {description}
        </p>

        <div className="bg-[#121c33] border border-[#1e2f54] rounded-md p-4">
          <span className="text-xs font-mono text-cyan-300 font-bold block mb-3 uppercase tracking-wider flex items-center space-x-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>Planned Engineering Deliverables:</span>
          </span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {deliverables.map((item, idx) => (
              <div key={idx} className="flex items-center space-x-2 text-xs text-slate-300">
                <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
