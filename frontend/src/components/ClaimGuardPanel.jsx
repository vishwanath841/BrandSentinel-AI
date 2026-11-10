import React from 'react';
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

export default function ClaimGuardPanel({ findings }) {
  const claimFindings = findings.filter((f) => f.category === 'CLAIM_GUARD');

  if (claimFindings.length === 0) {
    return null;
  }

  const verified = claimFindings.filter((f) => f.claim_status === 'VERIFIED');
  const contradictions = claimFindings.filter((f) => f.claim_status === 'CONTRADICTION');
  const unsupported = claimFindings.filter((f) => f.claim_status === 'UNSUPPORTED_NEEDS_REVIEW');

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <ShieldCheck className="h-5 w-5 text-sky-400" />
          <h3 className="text-sm font-bold text-white">ClaimGuard: Factual & Promotional Claim Verification</h3>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
            {verified.length} Verified
          </span>
          <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-medium">
            {unsupported.length} Needs Review
          </span>
          <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 font-medium">
            {contradictions.length} Contradictions
          </span>
        </div>
      </div>

      {/* Reliability Principle Callout */}
      <div className="p-3.5 bg-sky-950/30 border border-sky-500/30 rounded-xl text-xs text-sky-200 flex items-start space-x-2.5">
        <HelpCircle className="h-4 w-4 text-sky-400 shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-white">Reliability Principle:</strong> The system distinguishes verified violations from uncertain findings. It will not claim a promotional statement is false solely because supporting evidence was not found; it labels it as unsupported or requiring review.
        </p>
      </div>

      {/* Claims List */}
      <div className="space-y-3">
        {claimFindings.map((finding) => {
          const isVerified = finding.claim_status === 'VERIFIED';
          const isContradiction = finding.claim_status === 'CONTRADICTION';
          const isUnsupported = finding.claim_status === 'UNSUPPORTED_NEEDS_REVIEW';

          return (
            <div
              key={finding.id}
              className={`p-4 rounded-xl border transition ${
                isVerified
                  ? 'bg-emerald-950/20 border-emerald-500/30'
                  : isContradiction
                  ? 'bg-rose-950/20 border-rose-500/30'
                  : 'bg-amber-950/20 border-amber-500/30'
              }`}
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center space-x-2">
                  {isVerified && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />}
                  {isContradiction && <XCircle className="h-4 w-4 text-rose-400 shrink-0" />}
                  {isUnsupported && <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0" />}
                  <span
                    className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      isVerified
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : isContradiction
                        ? 'bg-rose-500/20 text-rose-300'
                        : 'bg-amber-500/20 text-amber-300'
                    }`}
                  >
                    {isVerified ? 'Verified Fact' : isContradiction ? 'Direct Contradiction' : 'Unsupported Claim (Needs Review)'}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">Severity: {finding.severity}</span>
              </div>

              <blockquote className="text-xs text-white font-medium bg-slate-900/60 p-2.5 rounded-lg border border-slate-700/50 mb-2">
                "{finding.flagged_text}"
              </blockquote>

              <p className="text-xs text-slate-300 mb-1.5">{finding.explanation}</p>

              {finding.evidence && (
                <div className="text-[11px] text-slate-400 bg-slate-900/40 p-2 rounded border border-slate-800">
                  <span className="font-semibold text-slate-300">Supporting Evidence / Citation:</span> {finding.evidence}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

