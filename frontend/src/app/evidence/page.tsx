"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Archive,
  ShieldCheck,
  Search,
  Plus,
  AlertTriangle,
  CheckCircle2,
  FileCheck,
  Copy,
  Check,
  ExternalLink,
  Clock,
  User,
  Scale,
  Database,
  ArrowRight,
  RefreshCw,
  Hash,
  FileText,
  Lock,
  Layers,
  Sparkles,
} from "lucide-react";
import {
  listEvidence,
  createEvidence,
  getEvidenceDetail,
  verifyEvidenceIntegrity,
  appendCustodyAction,
  getCases,
} from "@/lib/api";
import {
  EvidenceItem,
  EvidenceDetail,
  InvestigationCase,
  IntegrityVerificationResult,
} from "@/lib/types";

function EvidenceLockerContent() {
  const searchParams = useSearchParams();
  const initialCase = searchParams.get("case_id") || "";
  const initialWallet = searchParams.get("wallet") || "";
  const initialTx = searchParams.get("txid") || "";
  const initialAmount = searchParams.get("amount") || "";
  const initialDesc = searchParams.get("desc") || "";

  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [selectedCaseFilter, setSelectedCaseFilter] = useState<string>(initialCase);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Detail Modal / Drawer state
  const [activeEvidenceId, setActiveEvidenceId] = useState<string | null>(null);
  const [activeDetail, setActiveDetail] = useState<EvidenceDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);
  const [verificationResult, setVerificationResult] = useState<IntegrityVerificationResult | null>(null);
  const [verifying, setVerifying] = useState<boolean>(false);

  // New Custody Action form
  const [custodyAction, setCustodyAction] = useState<string>("REVIEWED");
  const [custodyActor, setCustodyActor] = useState<string>("Forensics Examiner");
  const [custodyNotes, setCustodyNotes] = useState<string>("");
  const [appendingCustody, setAppendingCustody] = useState<boolean>(false);

  // Preserve as Evidence Modal state
  const [showPreserveModal, setShowPreserveModal] = useState<boolean>(Boolean(initialTx || initialWallet));
  const [newCaseId, setNewCaseId] = useState<string>(initialCase);
  const [newArtifactType, setNewArtifactType] = useState<string>("TRANSACTION_SNAPSHOT");
  const [newWalletAddress, setNewWalletAddress] = useState<string>(initialWallet);
  const [newTxHash, setNewTxHash] = useState<string>(initialTx);
  const [newAmountBtc, setNewAmountBtc] = useState<string>(initialAmount);
  const [newCollector, setNewCollector] = useState<string>("Forensics Examiner");
  const [newDescription, setNewDescription] = useState<string>(
    initialDesc || (initialTx ? `Preserved forensic transaction snapshot: ${initialTx}` : "")
  );
  const [newRawJson, setNewRawJson] = useState<string>(
    JSON.stringify(
      {
        sample_finding: "Suspicious fund transfer matching peel-chain dispersion pattern.",
        blockchain: "Bitcoin Public Ledger",
        txid: initialTx || undefined,
        wallet: initialWallet || undefined,
        amount: initialAmount || undefined,
        captured_at: new Date().toISOString(),
      },
      null,
      2
    )
  );
  const [preserving, setPreserving] = useState<boolean>(false);

  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedCaseFilter]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [evRes, casesRes] = await Promise.all([
        listEvidence(selectedCaseFilter || undefined),
        getCases().catch(() => []),
      ]);
      setEvidenceList(evRes);
      setCases(casesRes);
      if (casesRes.length > 0) {
        if (initialCase) {
          const match = casesRes.find(c => c.id === initialCase || c.case_id === initialCase);
          if (match) {
            setNewCaseId(match.id);
            setSelectedCaseFilter(match.id);
          } else {
            setNewCaseId(casesRes[0].id);
          }
        } else if (!newCaseId) {
          setNewCaseId(casesRes[0].id);
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load evidence";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function handleOpenDetail(id: string) {
    setActiveEvidenceId(id);
    setDetailLoading(true);
    setVerificationResult(null);
    try {
      const detail = await getEvidenceDetail(id);
      setActiveDetail(detail);
    } catch (err) {
      console.error("Error loading detail:", err);
    } finally {
      setDetailLoading(false);
    }
  }

  async function handleVerifyIntegrity(id: string) {
    setVerifying(true);
    try {
      const res = await verifyEvidenceIntegrity(id, "Automated Forensics Verifier");
      setVerificationResult(res);
      // Refresh detail to show the newly appended VERIFIED entry in timeline
      const updated = await getEvidenceDetail(id);
      setActiveDetail(updated);
      // Refresh list count
      loadData();
    } catch (err) {
      console.error("Integrity verification error:", err);
    } finally {
      setVerifying(false);
    }
  }

  async function handleAppendCustody() {
    if (!activeEvidenceId || !custodyActor.trim()) return;
    setAppendingCustody(true);
    try {
      await appendCustodyAction(activeEvidenceId, {
        action_performed: custodyAction,
        actor_name: custodyActor,
        notes: custodyNotes || `Custodial action ${custodyAction} performed.`,
      });
      setCustodyNotes("");
      const updated = await getEvidenceDetail(activeEvidenceId);
      setActiveDetail(updated);
      loadData();
    } catch (err) {
      console.error("Error recording custody:", err);
    } finally {
      setAppendingCustody(false);
    }
  }

  async function handlePreserveEvidence(e: React.FormEvent) {
    e.preventDefault();
    if (!newCaseId) {
      alert("Please select an investigation case to associate with this evidence.");
      return;
    }
    setPreserving(true);
    try {
      let parsedPayload: Record<string, unknown> = {};
      try {
        parsedPayload = JSON.parse(newRawJson);
      } catch {
        parsedPayload = { raw_text: newRawJson };
      }

      await createEvidence({
        case_id: newCaseId,
        artifact_type: newArtifactType,
        wallet_address: newWalletAddress.trim() || undefined,
        transaction_hash: newTxHash.trim() || undefined,
        amount_btc: newAmountBtc ? parseFloat(newAmountBtc) : undefined,
        source: "Public Bitcoin Blockchain / Mempool API",
        collector: newCollector,
        description: newDescription,
        raw_payload: parsedPayload,
      });

      setShowPreserveModal(false);
      setNewDescription("");
      loadData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to preserve evidence");
    } finally {
      setPreserving(false);
    }
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(id);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800">
              Module 8 • Evidence Management Subsystem
            </span>
            <span className="text-xs font-mono text-slate-500">ISO/IEC 27037 • RFC 8785 Hashing</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-100 flex items-center gap-3">
            <Archive className="w-7 h-7 text-cyan-400" />
            Digital Evidence Locker & Vault
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Cryptographically sealed repository preserving public Bitcoin ledger artifacts.
            Every seizure generates a deterministic SHA-256 fingerprint and initiates an append-only Chain of Custody provenance log.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => setShowPreserveModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-sm font-semibold flex items-center gap-2 shadow-lg shadow-cyan-950/50 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            PRESERVE AS EVIDENCE
          </button>
        </div>
      </div>

      {/* Forensic Legal Advisory Callout */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 shadow-md flex items-start gap-3.5 text-xs text-slate-300 font-sans">
        <Scale className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-semibold text-slate-200 font-mono flex items-center gap-2">
            <span>LEGAL JURISPRUDENCE & STATUTORY ADVISORY</span>
            <span className="text-[10px] text-amber-400 border border-amber-800/80 px-1.5 py-0.2 rounded bg-amber-950/40">
              Indian Evidence Act § 65B / ISO 27037
            </span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Public Bitcoin blockchain ledger data constitutes electronic reference material.
            Proper legal procedures—including cryptographic hash preservation, verifiable custody provenance,
            and Section 65B electronic certificate generation—are statutory requirements before digital evidence
            can be introduced into judicial proceedings.
          </p>
        </div>
      </div>

      {/* Filter and Control Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-slate-400">Filter by Case:</span>
          <select
            value={selectedCaseFilter}
            onChange={(e) => setSelectedCaseFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            <option value="">All Forensic Cases ({evidenceList.length} items)</option>
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                [{c.case_id}] {c.title.substring(0, 30)}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadData}
            className="px-3 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-xs font-mono text-slate-300 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Evidence Table */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-semibold tracking-wide uppercase text-slate-300 font-mono">
              Preserved Digital Artifacts Inventory
            </h2>
          </div>
          <span className="text-xs font-mono text-slate-500">
            {evidenceList.length} Preserved Items
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 font-mono text-xs">
            Loading preserved evidence artifacts...
          </div>
        ) : evidenceList.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <div className="inline-flex p-3 rounded-full bg-slate-950 border border-slate-800 text-slate-500">
              <Archive className="w-6 h-6" />
            </div>
            <div className="text-sm text-slate-400 font-mono">No evidence artifacts preserved yet.</div>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Click &quot;PRESERVE AS EVIDENCE&quot; to seize a blockchain transaction snapshot,
              wallet analytical finding, or ML report into the immutable vault.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/60">
                  <th className="py-3 px-3">Evidence ID</th>
                  <th className="py-3 px-3">Artifact Type</th>
                  <th className="py-3 px-3">Target Finding</th>
                  <th className="py-3 px-3">SHA-256 Digest</th>
                  <th className="py-3 px-3">Seized At (UTC)</th>
                  <th className="py-3 px-3">Collector</th>
                  <th className="py-3 px-3">Custody Log</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {evidenceList.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-3 font-bold text-slate-200">
                      {item.id.substring(0, 8)}...
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950/60 text-cyan-300 border border-cyan-800">
                        {item.artifact_type}
                      </span>
                    </td>
                    <td className="py-3 px-3 max-w-xs">
                      {item.transaction_hash ? (
                        <div className="truncate text-slate-300" title={item.transaction_hash}>
                          TX: {item.transaction_hash.substring(0, 16)}...
                        </div>
                      ) : item.wallet_address ? (
                        <div className="truncate text-slate-300" title={item.wallet_address}>
                          Addr: {item.wallet_address.substring(0, 16)}...
                        </div>
                      ) : (
                        <span className="text-slate-500">{item.description || "General Snapshot"}</span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1.5 text-slate-400">
                        <span className="font-mono text-[11px] text-cyan-300">
                          {item.sha256_hash.substring(0, 10)}...{item.sha256_hash.substring(58)}
                        </span>
                        <button
                          onClick={() => copyToClipboard(item.sha256_hash, item.id)}
                          className="hover:text-white transition-colors"
                          title="Copy Full SHA-256 Hash"
                        >
                          {copiedHash === item.id ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {new Date(item.seized_at).toLocaleDateString()}{" "}
                      <span className="text-[10px] text-slate-500">
                        {new Date(item.seized_at).toLocaleTimeString()}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-300">{item.captured_by}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-950 border border-slate-800 text-slate-400">
                        {item.custody_count} events
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => handleOpenDetail(item.id)}
                        className="px-2.5 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-cyan-700/60 rounded text-cyan-400 hover:text-cyan-300 font-bold transition-all cursor-pointer"
                      >
                        Inspect Dossier &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* DETAIL & CHAIN OF CUSTODY MODAL / DRAWER */}
      {activeEvidenceId && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-6 h-6 text-cyan-400" />
                <div>
                  <h3 className="text-lg font-bold text-slate-100 font-mono">
                    Evidence Dossier & Chain of Custody
                  </h3>
                  <div className="text-xs font-mono text-slate-400">
                    Artifact ID: <span className="text-cyan-300 font-bold">{activeEvidenceId}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => {
                  setActiveEvidenceId(null);
                  setActiveDetail(null);
                  setVerificationResult(null);
                }}
                className="text-slate-400 hover:text-white p-2 font-mono text-sm cursor-pointer"
              >
                ✕ Close
              </button>
            </div>

            {detailLoading || !activeDetail ? (
              <div className="py-12 text-center text-slate-400 font-mono text-xs">
                Loading evidence cryptographic dossier...
              </div>
            ) : (
              <div className="space-y-6">
                {/* Cryptographic Verification Card */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                      Cryptographic SHA-256 Fingerprint
                    </span>
                    <button
                      onClick={() => handleVerifyIntegrity(activeDetail.id)}
                      disabled={verifying}
                      className="px-3 py-1.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg text-xs font-bold font-mono flex items-center gap-1.5 shadow-md shadow-emerald-950/40 cursor-pointer disabled:opacity-50"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${verifying ? "animate-spin" : ""}`} />
                      {verifying ? "Recomputing Hash..." : "VERIFY INTEGRITY NOW"}
                    </button>
                  </div>

                  <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800/80 font-mono text-xs text-cyan-300 break-all select-all flex items-center justify-between gap-2">
                    <span>{activeDetail.sha256_hash}</span>
                    <button
                      onClick={() => copyToClipboard(activeDetail.sha256_hash, "detail-hash")}
                      className="text-slate-400 hover:text-white shrink-0"
                    >
                      {copiedHash === "detail-hash" ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>

                  {/* Dynamic Verification Result Banner */}
                  {verificationResult && (
                    <div
                      className={`p-3.5 rounded-lg border flex items-start gap-3 ${
                        verificationResult.verified
                          ? "bg-emerald-950/40 border-emerald-600/70 text-emerald-300"
                          : "bg-rose-950/40 border-rose-600/70 text-rose-300"
                      }`}
                    >
                      {verificationResult.verified ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                      )}
                      <div>
                        <div className="text-sm font-bold font-mono">
                          {verificationResult.status}
                        </div>
                        <div className="text-xs mt-0.5 opacity-90">{verificationResult.message}</div>
                        <div className="text-[10px] text-slate-400 font-mono mt-1">
                          Verified At: {new Date(verificationResult.verification_timestamp).toLocaleString()} • Log ID: {verificationResult.custody_entry_id?.substring(0, 8)}...
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Evidence Metadata Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-500 uppercase text-[10px]">Type</div>
                    <div className="font-bold text-cyan-400 mt-0.5">{activeDetail.artifact_type}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-500 uppercase text-[10px]">Collector</div>
                    <div className="font-bold text-slate-200 mt-0.5">{activeDetail.captured_by}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-500 uppercase text-[10px]">Source</div>
                    <div className="font-bold text-slate-200 mt-0.5 truncate" title={activeDetail.source}>
                      {activeDetail.source}
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-500 uppercase text-[10px]">Seized Date</div>
                    <div className="font-bold text-slate-200 mt-0.5">
                      {new Date(activeDetail.seized_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                {/* Description & Payload Details */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                  <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                    Investigative Context & Canonical Payload
                  </span>
                  <p className="text-xs text-slate-300 font-sans leading-relaxed">
                    {activeDetail.description || "No customized notes recorded."}
                  </p>

                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 font-mono text-[11px] text-slate-400 max-h-40 overflow-y-auto">
                    <pre>{JSON.stringify(activeDetail.raw_payload, null, 2)}</pre>
                  </div>
                </div>

                {/* APPEND-ONLY CHAIN OF CUSTODY TIMELINE */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <FileCheck className="w-4 h-4 text-emerald-400" />
                      <h4 className="text-xs font-semibold tracking-wide uppercase text-slate-200 font-mono">
                        APPEND-ONLY CHAIN OF CUSTODY TIMELINE
                      </h4>
                    </div>
                    <span className="text-[11px] font-mono text-slate-500">
                      {activeDetail.custody_entries.length} Certified Events
                    </span>
                  </div>

                  <div className="space-y-3">
                    {activeDetail.custody_entries.map((entry, idx) => (
                      <div
                        key={entry.id}
                        className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 flex items-start justify-between gap-3 text-xs font-mono"
                      >
                        <div className="flex items-start gap-3">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-950 border border-slate-700 text-cyan-300 shrink-0">
                            #{idx + 1} {entry.action_performed}
                          </span>
                          <div>
                            <div className="text-slate-200 font-sans">{entry.notes}</div>
                            <div className="text-[10px] text-slate-500 mt-1">
                              Actor: <span className="text-slate-400">{entry.actor_name}</span> • Timestamp:{" "}
                              {new Date(entry.timestamp).toLocaleString()}
                            </div>
                          </div>
                        </div>

                        <span className="text-[10px] text-slate-500 font-mono shrink-0">
                          Hash: {entry.current_hash.substring(0, 8)}...
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Form to Append New Custody Action */}
                  <div className="pt-3 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-12 gap-3 text-xs">
                    <div className="md:col-span-3">
                      <select
                        value={custodyAction}
                        onChange={(e) => setCustodyAction(e.target.value)}
                        className="w-full px-2.5 py-2 bg-slate-900 border border-slate-800 rounded text-slate-300 font-mono"
                      >
                        <option value="REVIEWED">REVIEWED</option>
                        <option value="EXPORTED">EXPORTED</option>
                        <option value="VERIFIED">VERIFIED</option>
                      </select>
                    </div>

                    <div className="md:col-span-3">
                      <input
                        type="text"
                        placeholder="Examiner Name..."
                        value={custodyActor}
                        onChange={(e) => setCustodyActor(e.target.value)}
                        className="w-full px-2.5 py-2 bg-slate-900 border border-slate-800 rounded text-slate-300 font-mono"
                      />
                    </div>

                    <div className="md:col-span-4">
                      <input
                        type="text"
                        placeholder="Custodial notes (e.g. Prepared for judicial filing)..."
                        value={custodyNotes}
                        onChange={(e) => setCustodyNotes(e.target.value)}
                        className="w-full px-2.5 py-2 bg-slate-900 border border-slate-800 rounded text-slate-300"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <button
                        onClick={handleAppendCustody}
                        disabled={appendingCustody}
                        className="w-full h-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded font-bold font-mono transition-colors cursor-pointer disabled:opacity-50"
                      >
                        {appendingCustody ? "Logging..." : "+ Log Event"}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* PRESERVE AS EVIDENCE MODAL */}
      {showPreserveModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <form
            onSubmit={handlePreserveEvidence}
            className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl shadow-2xl p-6 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Plus className="w-5 h-5 text-cyan-400" />
                <h3 className="text-base font-bold text-slate-100 font-mono">
                  Preserve Blockchain Artifact as Evidence
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowPreserveModal(false)}
                className="text-slate-400 hover:text-white p-1 text-sm font-mono cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div>
                <label className="text-slate-400 block mb-1">Target Case:</label>
                <select
                  value={newCaseId}
                  onChange={(e) => setNewCaseId(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-200"
                >
                  <option value="">-- Select Investigation Case --</option>
                  {cases.map((c) => (
                    <option key={c.id} value={c.id}>
                      [{c.case_id}] {c.title.substring(0, 25)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Artifact Type:</label>
                <select
                  value={newArtifactType}
                  onChange={(e) => setNewArtifactType(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-200"
                >
                  <option value="TRANSACTION_SNAPSHOT">TRANSACTION_SNAPSHOT</option>
                  <option value="WALLET_FINDING">WALLET_FINDING</option>
                  <option value="GRAPH_CLUSTER">GRAPH_CLUSTER</option>
                  <option value="ML_ANOMALY_RECORD">ML_ANOMALY_RECORD</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Wallet Address (Optional):</label>
                <input
                  type="text"
                  placeholder="e.g. 13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94"
                  value={newWalletAddress}
                  onChange={(e) => setNewWalletAddress(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-200"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Transaction Hash (Optional):</label>
                <input
                  type="text"
                  placeholder="64-char hex TXID..."
                  value={newTxHash}
                  onChange={(e) => setNewTxHash(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-200"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Amount BTC (Optional):</label>
                <input
                  type="number"
                  step="any"
                  placeholder="e.g. 0.50"
                  value={newAmountBtc}
                  onChange={(e) => setNewAmountBtc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-200"
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Collector / Officer Name:</label>
                <input
                  type="text"
                  value={newCollector}
                  onChange={(e) => setNewCollector(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-200"
                />
              </div>
            </div>

            <div className="text-xs font-mono">
              <label className="text-slate-400 block mb-1">Forensic Description / Seizure Rationale:</label>
              <textarea
                rows={2}
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                required
                placeholder="Document why this artifact is being preserved for court or forensic analysis..."
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-200 font-sans"
              />
            </div>

            <div className="text-xs font-mono">
              <label className="text-slate-400 block mb-1">Raw Blockchain Payload (JSON):</label>
              <textarea
                rows={4}
                value={newRawJson}
                onChange={(e) => setNewRawJson(e.target.value)}
                required
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-300 font-mono text-[11px]"
              />
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowPreserveModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-mono text-xs cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={preserving}
                className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-mono text-xs font-bold transition-all shadow-lg shadow-cyan-950/50 cursor-pointer disabled:opacity-50"
              >
                {preserving ? "Freezing & Hashing..." : "Freeze & Seal Evidence"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default function EvidenceLockerPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-400">Loading evidence locker...</div>}>
      <EvidenceLockerContent />
    </Suspense>
  );
}
