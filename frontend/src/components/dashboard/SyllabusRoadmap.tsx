import React from "react";
import { BookOpen, CheckCircle, Clock, ShieldCheck, Scale, Cpu, FileText } from "lucide-react";

interface SyllabusModule {
  number: number;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  topics: string[];
  systemFeature: string;
  status: "Phase 1 Foundation" | "Phase 2 Pipeline" | "Phase 3 ML" | "Phase 4 Forensics" | "Phase 5 Report";
  statusColor: string;
}

const MODULES: SyllabusModule[] = [
  {
    number: 1,
    title: "Understanding Cyber Crime",
    icon: ShieldCheck,
    topics: ["Cybercrime categories", "Ransomware mechanics", "Real-world ransomware cases"],
    systemFeature: "Ransomware incident taxonomy & historical case archives (WannaCry, LockBit, DarkSide).",
    status: "Phase 1 Foundation",
    statusColor: "emerald",
  },
  {
    number: 2,
    title: "Life Cycle of Cyber Crime",
    icon: Clock,
    topics: ["Reconnaissance", "Incident response lifecycle", "Case studies"],
    systemFeature: "NIST SP 800-61 incident lifecycle tracker & multi-hop counterparty wallet reconnaissance.",
    status: "Phase 2 Pipeline",
    statusColor: "cyan",
  },
  {
    number: 3,
    title: "Legal Perspectives in Cyber Forensics",
    icon: Scale,
    topics: ["Cybercrime legal perspectives", "Indian IT Act 2000 (Sec 65B)", "DPDP Act 2023 / GDPR"],
    systemFeature: "Section 65B Indian IT Act 2000 digital certificate generation and privacy-by-design public ledger processing.",
    status: "Phase 1 Foundation",
    statusColor: "emerald",
  },
  {
    number: 4,
    title: "Understanding Computer Forensics",
    icon: FileText,
    topics: ["Digital evidence lifecycle", "Chain of custody", "Integrity verification", "Forensic challenges"],
    systemFeature: "ISO/IEC 27037 Evidence Vault, SHA-256 tamper verification, and immutable hash-chained audit ledger.",
    status: "Phase 4 Forensics",
    statusColor: "blue",
  },
  {
    number: 5,
    title: "Role of AI in Cybersecurity",
    icon: Cpu,
    topics: ["Proactive vs reactive defense", "ML in cybersecurity", "Anomaly detection"],
    systemFeature: "Scikit-learn Isolation Forest unsupervised model with 14 engineered UTXO behavioral heuristics.",
    status: "Phase 3 ML",
    statusColor: "purple",
  },
];

export default function SyllabusRoadmap() {
  return (
    <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg p-5">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#1b2848]">
        <div className="flex items-center space-x-2.5">
          <BookOpen className="w-5 h-5 text-cyan-400" />
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase font-mono">
            Academic Syllabus Alignment & Architecture Map (Modules 1 – 5)
          </h2>
        </div>
        <span className="text-xs font-mono text-cyan-400 bg-cyan-950/50 border border-cyan-800/40 px-2.5 py-1 rounded">
          B.Tech Cybersecurity Curriculum
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {MODULES.map((mod) => {
          const Icon = mod.icon;
          return (
            <div
              key={mod.number}
              className="bg-[#121c33] border border-[#1e2f54] rounded-md p-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#1a2b4d] text-cyan-300 font-bold">
                    MODULE {mod.number}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                    {mod.status}
                  </span>
                </div>

                <h3 className="text-xs font-bold text-white mb-2 flex items-center space-x-2">
                  <Icon className="w-4 h-4 text-cyan-400" />
                  <span>{mod.title}</span>
                </h3>

                <div className="mb-3">
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                    Key Topics Covered:
                  </span>
                  <ul className="text-xs text-slate-300 space-y-1">
                    {mod.topics.map((t, idx) => (
                      <li key={idx} className="flex items-center space-x-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400/60" />
                        <span className="text-[11px]">{t}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="pt-2 border-t border-[#1b2848]">
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                  Engineered Platform Capability:
                </span>
                <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                  {mod.systemFeature}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
