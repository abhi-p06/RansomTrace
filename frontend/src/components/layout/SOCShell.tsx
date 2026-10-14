"use client";

import React from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";

interface SOCShellProps {
  children: React.ReactNode;
}

export default function SOCShell({ children }: SOCShellProps) {
  return (
    <div className="flex h-screen bg-[#070a13] text-slate-100 overflow-hidden">
      {/* Static Sidebar */}
      <Sidebar />

      {/* Main Investigation Workspace */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />

        {/* Investigative Ethical & Legal Disclaimer Banner */}
        <div className="bg-[#12182b] border-b border-[#1e2c4c] px-6 py-2 flex items-center justify-between text-xs text-slate-300">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span className="font-mono text-[11px] text-cyan-300 uppercase tracking-wide">
              Academic & Forensic Notice:
            </span>
            <span className="text-[11px] text-slate-300">
              RansomTrace analyzes publicly available Bitcoin ledger data for educational and cybercrime investigation forensics.
            </span>
          </div>
          <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest hidden md:inline">
            Sec 65B IT Act 2000 Compliant
          </span>
        </div>

        {/* Dynamic Page Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#070a13]">
          {children}
        </main>
      </div>
    </div>
  );
}
