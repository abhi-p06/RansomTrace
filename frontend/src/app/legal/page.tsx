import React from "react";
import { Scale, ShieldCheck, FileText, CheckCircle2, Lock } from "lucide-react";

export default function LegalPage() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="pb-4 border-b border-[#1b2848]">
        <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono mb-1">
          <Scale className="w-4 h-4" />
          <span className="uppercase tracking-wider">Module 3: Legal Perspectives & Forensic Standards</span>
        </div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Cybercrime Jurisprudence & Digital Evidence Legal Framework
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Statutory standards governing electronic evidence admissibility, chain-of-custody, and privacy compliance in RansomTrace.
        </p>
      </div>

      {/* Grid of Legal Articles */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 65B Card */}
        <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg p-5">
          <div className="flex items-center space-x-2 text-emerald-400 mb-3">
            <FileText className="w-5 h-5" />
            <h2 className="text-sm font-bold font-mono uppercase text-white">
              Indian IT Act 2000 (Section 65B)
            </h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-4">
            Under Section 65B of the Indian Evidence Act (amended with the Information Technology Act 2000),
            electronic records are admissible in court only if accompanied by a certificate identifying the
            originating device and certifying that the electronic device operated properly during the capture.
          </p>
          <div className="bg-[#121c33] p-3 rounded border border-[#1e2f54] text-xs font-mono text-cyan-300 space-y-1">
            <div className="flex items-center space-x-1.5 text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>SHA-256 System Immutability Hash</span>
            </div>
            <div className="flex items-center space-x-1.5 text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Investigator Device Metadata & Timestamp</span>
            </div>
            <div className="flex items-center space-x-1.5 text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Automated Sec 65B Certificate Generation in Phase 5</span>
            </div>
          </div>
        </div>

        {/* ISO/IEC 27037 Card */}
        <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg p-5">
          <div className="flex items-center space-x-2 text-cyan-400 mb-3">
            <ShieldCheck className="w-5 h-5" />
            <h2 className="text-sm font-bold font-mono uppercase text-white">
              ISO/IEC 27037 Standards
            </h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-4">
            Specifies requirements for digital evidence handling across four lifecycle stages: Identification,
            Collection, Acquisition, and Preservation. RansomTrace enforces zero in-situ alteration of blockchain
            artifacts through RFC 8785 canonical serialization and cryptographic sealing.
          </p>
          <div className="bg-[#121c33] p-3 rounded border border-[#1e2f54] text-xs font-mono text-cyan-300 space-y-1">
            <div className="flex items-center space-x-1.5 text-cyan-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>RFC 8785 Canonical JSON Serialization</span>
            </div>
            <div className="flex items-center space-x-1.5 text-cyan-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Append-Only Hash-Chained Audit Ledger</span>
            </div>
            <div className="flex items-center space-x-1.5 text-cyan-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Zero-Byte Tamper Detection Verifier</span>
            </div>
          </div>
        </div>

        {/* DPDP Act 2023 Card */}
        <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg p-5">
          <div className="flex items-center space-x-2 text-purple-400 mb-3">
            <Lock className="w-5 h-5" />
            <h2 className="text-sm font-bold font-mono uppercase text-white">
              DPDP Act 2023 / GDPR Compliance
            </h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-4">
            India&apos;s Digital Personal Data Protection Act 2023 and GDPR mandate privacy safeguards. RansomTrace
            strictly processes pseudonymized public blockchain transactions and does not attempt deanonymization,
            PII scraping, or tracking private identities.
          </p>
          <div className="bg-[#121c33] p-3 rounded border border-[#1e2f54] text-xs font-mono text-slate-300 space-y-1">
            <div className="flex items-center space-x-1.5 text-purple-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Public Blockchain Ledger Access Only</span>
            </div>
            <div className="flex items-center space-x-1.5 text-purple-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Zero Personal Data (PII) Stored in Database</span>
            </div>
          </div>
        </div>

        {/* Investigative Indicator Framing */}
        <div className="bg-[#0e1628] border border-[#1b2848] rounded-lg p-5">
          <div className="flex items-center space-x-2 text-amber-400 mb-3">
            <Scale className="w-5 h-5" />
            <h2 className="text-sm font-bold font-mono uppercase text-white">
              Heuristic Risk Indicator Designation
            </h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-4">
            In compliance with forensic science best practices, machine learning anomaly scores generated by
            the Isolation Forest engine are presented strictly as statistical indicators to guide investigative
            inquiries, never as conclusive judicial proof of criminality.
          </p>
          <div className="bg-[#121c33] p-3 rounded border border-[#1e2f54] text-xs font-mono text-amber-300 space-y-1">
            <div className="flex items-center space-x-1.5 text-amber-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Transparent Feature Weight Explanations</span>
            </div>
            <div className="flex items-center space-x-1.5 text-amber-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Mandatory Evidentiary Disclaimer Seals</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
