"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldAlert,
  LayoutDashboard,
  FolderLock,
  GitFork,
  Cpu,
  Archive,
  FileCheck,
  Scale,
  FileDown,
  Terminal,
  Activity
} from "lucide-react";

interface NavSection {
  title: string;
  items: {
    label: string;
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    phaseTag?: string;
  }[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: "OPERATIONS",
    items: [
      { label: "Dashboard", href: "/", icon: LayoutDashboard },
      { label: "Cases", href: "/cases", icon: FolderLock },
    ],
  },
  {
    title: "FORENSIC ANALYTICS",
    items: [
      { label: "Wallet Investigation", href: "/ingestion", icon: Terminal },
      { label: "Transactions", href: "/analytics", icon: Activity },
      { label: "Fund Flow", href: "/graph", icon: GitFork },
      { label: "AI Analysis", href: "/ml-risk", icon: Cpu },
      { label: "Risk Analysis", href: "/risk", icon: ShieldAlert },
    ],
  },
  {
    title: "INTEGRITY & EVIDENCE",
    items: [
      { label: "Evidence Locker", href: "/evidence", icon: Archive },
      { label: "Chain of Custody", href: "/custody", icon: FileCheck },
      { label: "Reports", href: "/reports", icon: FileDown },
    ],
  },
  {
    title: "LEGAL & JURISPRUDENCE",
    items: [
      { label: "About / Methodology", href: "/legal", icon: Scale },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0a0f1d] border-r border-[#1a2540] flex flex-col h-screen sticky top-0 select-none">
      {/* Platform Branding */}
      <div className="p-5 border-b border-[#1a2540] flex items-center space-x-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-700 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <ShieldAlert className="w-6 h-6 text-black" />
        </div>
        <div>
          <div className="flex items-center space-x-1.5">
            <span className="font-extrabold text-base tracking-wider text-white">RANSOM</span>
            <span className="font-extrabold text-base tracking-wider text-cyan-400">TRACE</span>
          </div>
          <span className="text-[10px] uppercase font-mono tracking-widest text-slate-400 block">
            SOC Forensics v1.0
          </span>
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title}>
            <div className="px-3 mb-2 text-[10px] font-mono tracking-wider text-slate-400 uppercase font-semibold">
              {section.title}
            </div>
            <nav className="space-y-1">
              {section.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all ${
                      isActive
                        ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30"
                        : "text-slate-300 hover:text-white hover:bg-[#121c33]"
                    }`}
                  >
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.phaseTag && (
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[#16233d] text-slate-400 border border-[#213459]">
                        {item.phaseTag}
                      </span>
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Bottom Security Status Badge */}
      <div className="p-4 border-t border-[#1a2540] bg-[#070c17]">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-[11px] font-mono text-slate-300 uppercase">System Active</span>
          </div>
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
        </div>
        <p className="text-[10px] text-slate-400 font-mono">
          ISO 27037 / Sec 65B Ready
        </p>
      </div>
    </aside>
  );
}
