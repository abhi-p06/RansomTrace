"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  FileCheck,
  ShieldCheck,
  Search,
  Scale,
  Clock,
  ArrowRight,
  Database,
  Hash,
  RefreshCw,
  Archive,
  User,
  CheckCircle2,
  FileText,
  AlertTriangle,
} from "lucide-react";
import { listEvidence, getEvidenceDetail } from "@/lib/api";
import { EvidenceItem, ChainOfCustodyEntryDto } from "@/lib/types";

export default function ChainOfCustodyPage() {
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [custodyLogs, setCustodyLogs] = useState<(ChainOfCustodyEntryDto & { evidenceSnippet?: string; artifactType?: string })[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterAction, setFilterAction] = useState<string>("");

  useEffect(() => {
    loadCustodyData();
  }, []);

  async function loadCustodyData() {
    setLoading(true);
    try {
      const items = await listEvidence();
      setEvidenceList(items);

      // Fetch custody entries for the latest evidence items (bounded to keep performance instant)
      const allEntries: (ChainOfCustodyEntryDto & { evidenceSnippet?: string; artifactType?: string })[] = [];
      const itemsToFetch = items.slice(0, 30);
      await Promise.all(
        itemsToFetch.map(async (ev) => {
          try {
            const detail = await getEvidenceDetail(ev.id);
            detail.custody_entries.forEach((entry) => {
              allEntries.push({
                ...entry,
                evidenceSnippet: ev.transaction_hash ? `TX: ${ev.transaction_hash.substring(0, 14)}...` : (ev.wallet_address ? `Addr: ${ev.wallet_address.substring(0, 14)}...` : ev.id.substring(0, 8)),
                artifactType: ev.artifact_type,
              });
            });
          } catch (e) {
            console.error("Error fetching detail for custody:", e);
          }
        })
      );

      // Sort reverse chronologically
      allEntries.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      setCustodyLogs(allEntries);
    } catch (err) {
      console.error("Error loading custody data:", err);
    } finally {
      setLoading(false);
    }
  }

  const filteredLogs = filterAction
    ? custodyLogs.filter((l) => l.action_performed === filterAction)
    : custodyLogs;

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono uppercase tracking-wider text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
              Module 8 • Chain of Custody
            </span>
            <span className="text-xs font-mono text-slate-500">Append-Only Cryptographic Audit Ledger</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-100 flex items-center gap-3">
            <FileCheck className="w-7 h-7 text-emerald-400" />
            Immutable Chain of Custody (CoC) Ledger
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Tamper-evident chronological provenance log recording every seizure, cryptographic hashing,
            vault storage, examiner review, export, and verification event.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <Link
            href="/evidence"
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-cyan-700/60 text-cyan-400 rounded-lg text-xs font-mono flex items-center gap-2 transition-colors"
          >
            <Archive className="w-3.5 h-3.5" />
            View Evidence Vault &rarr;
          </Link>
        </div>
      </div>

      {/* Advisory Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-start gap-3">
        <Scale className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-semibold text-slate-200 font-mono">
            SECTION 65B INDIAN EVIDENCE ACT & ISO 27037 ADMISSIBILITY
          </div>
          <p className="text-slate-400 font-sans leading-relaxed">
            The integrity of electronic evidence depends upon proving that the digital artifact has remained
            unaltered from seizure to judicial submission. The entries below represent an immutable, append-only
            chain establishing chronological custody.
          </p>
        </div>
      </div>

      {/* Filter and Stats Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-slate-400">Filter by Action:</span>
          <select
            value={filterAction}
            onChange={(e) => setFilterAction(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-emerald-500 cursor-pointer"
          >
            <option value="">All Custodial Events ({custodyLogs.length})</option>
            <option value="COLLECTED">COLLECTED</option>
            <option value="HASHED">HASHED</option>
            <option value="STORED">STORED</option>
            <option value="REVIEWED">REVIEWED</option>
            <option value="EXPORTED">EXPORTED</option>
            <option value="VERIFIED">VERIFIED</option>
          </select>
        </div>

        <button
          onClick={loadCustodyData}
          className="px-3 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded text-xs font-mono text-slate-300 flex items-center gap-1.5 transition-colors cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Ledger
        </button>
      </div>

      {/* Master Custody Timeline Ledger */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
              Provenance Ledger Timeline
            </h2>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {filteredLogs.length} Events Preserved
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 font-mono text-xs">
            Loading custody ledger...
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="py-12 text-center space-y-2">
            <div className="text-slate-400 font-mono text-xs">No custodial events recorded yet.</div>
            <p className="text-xs text-slate-500">
              Preserve a transaction finding in the Evidence Locker to initiate custody logging.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredLogs.map((log) => (
              <div
                key={log.id}
                className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-4 text-xs font-mono"
              >
                <div className="flex items-start gap-3.5">
                  <span
                    className={`px-2.5 py-1 rounded text-[10px] font-extrabold tracking-wider border shrink-0 ${
                      log.action_performed === "VERIFIED"
                        ? "bg-emerald-950/70 border-emerald-700 text-emerald-300"
                        : log.action_performed === "COLLECTED"
                        ? "bg-cyan-950/70 border-cyan-700 text-cyan-300"
                        : log.action_performed === "HASHED"
                        ? "bg-blue-950/70 border-blue-700 text-blue-300"
                        : log.action_performed === "STORED"
                        ? "bg-slate-900 border-slate-700 text-slate-300"
                        : "bg-purple-950/70 border-purple-700 text-purple-300"
                    }`}
                  >
                    {log.action_performed}
                  </span>

                  <div className="space-y-0.5">
                    <div className="text-slate-200 font-sans text-xs">{log.notes}</div>
                    <div className="text-[11px] text-slate-500 flex flex-wrap gap-2">
                      <span>Actor: <span className="text-slate-400 font-semibold">{log.actor_name}</span></span>
                      <span>•</span>
                      <span>Target: <span className="text-cyan-400">{log.evidenceSnippet}</span></span>
                      <span>•</span>
                      <span>Evidence ID: <span className="text-slate-400">{log.evidence_id?.substring(0, 8)}...</span></span>
                    </div>
                  </div>
                </div>

                <div className="text-right shrink-0 font-mono text-[11px] text-slate-500 space-y-0.5">
                  <div className="text-slate-400">{new Date(log.timestamp).toLocaleString()}</div>
                  <div className="text-slate-600">Fingerprint: {log.current_hash.substring(0, 10)}...</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
