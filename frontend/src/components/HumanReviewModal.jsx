import React, { useState } from 'react';
import {
  X, Check, Edit2, RotateCcw, ThumbsUp, ThumbsDown,
  AlertTriangle, FileCheck, ShieldCheck, Sparkles, UserCheck, Copy
} from 'lucide-react';
import { reviewFinding, submitFinalDecision } from '../services/api';

export default function HumanReviewModal({ submission, onClose, onReviewComplete }) {
  const findings = submission?.report?.findings || [];
  const [editingFindingId, setEditingFindingId] = useState(null);
  const [customRevisionText, setCustomRevisionText] = useState('');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [loadingId, setLoadingId] = useState(null);
  const [isCopied, setIsCopied] = useState(false);

  // Final Decision State
  const [reviewerName, setReviewerName] = useState('Vishwanath S A');
  const [reviewerRole, setReviewerRole] = useState('Brand Governance Lead');
  const [decisionNotes, setDecisionNotes] = useState('');
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);
  const [error, setError] = useState(null);

  // Compute live assembled text with accepted/edited revisions
  let liveAssembledText = submission.extracted_text || '';
  findings.forEach((f) => {
    if ((f.review_status === 'ACCEPTED' || f.review_status === 'EDITED') && f.flagged_text) {
      const replacement = f.reviewed_revision || f.suggested_revision || '';
      if (replacement && liveAssembledText.includes(f.flagged_text)) {
        liveAssembledText = liveAssembledText.replace(f.flagged_text, replacement);
      }
    }
  });

  async function handleAction(findingId, status, customText = null) {
    setLoadingId(findingId);
    setError(null);
    try {
      await reviewFinding(findingId, status, customText, reviewerNotes);
      setEditingFindingId(null);
      setCustomRevisionText('');
      setReviewerNotes('');
      onReviewComplete();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingId(null);
    }
  }

  async function handleFinalDecision(decision) {
    setIsSubmittingDecision(true);
    setError(null);
    try {
      await submitFinalDecision(submission.id, {
        reviewer_name: reviewerName,
        reviewer_role: reviewerRole,
        decision: decision,
        decision_notes: decisionNotes,
        final_content: liveAssembledText
      });
      onReviewComplete();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmittingDecision(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden my-6">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2.5">
            <UserCheck className="h-5 w-5 text-sky-400" />
            <div>
              <h3 className="text-sm font-bold text-white">Human Review & Approval Workflow</h3>
              <p className="text-xs text-slate-400">
                Authorised reviewer accepts, edits, or rejects suggested corrections and renders final sign-off.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {error && (
          <div className="mx-6 mt-4 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-xl text-xs flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Live Assembled Preview */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-sky-400 flex items-center space-x-1.5">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Live Publication Preview (Updated as you accept/edit revisions)</span>
              </span>
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => {
                    if (liveAssembledText) {
                      navigator.clipboard.writeText(liveAssembledText);
                      setIsCopied(true);
                      setTimeout(() => setIsCopied(false), 2000);
                    }
                  }}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium flex items-center space-x-1 transition border border-slate-700"
                  title="Copy revised content to clipboard"
                >
                  {isCopied ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span>Copy Clean Text</span>
                    </>
                  )}
                </button>
                <span className="text-[11px] text-slate-500 font-mono">
                  {findings.filter((f) => f.review_status === 'ACCEPTED').length} accepted |{' '}
                  {findings.filter((f) => f.review_status === 'REJECTED').length} rejected
                </span>
              </div>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-200 leading-relaxed font-sans max-h-36 overflow-y-auto">
              {liveAssembledText || <span className="text-slate-500 italic">No text content available.</span>}
            </div>
          </div>

          {/* Findings Review List */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Detected Issues & Smart Corrections ({findings.length})
            </h4>

            {findings.map((f, index) => {
              const isEditing = editingFindingId === f.id;
              const isLoading = loadingId === f.id;

              return (
                <div
                  key={f.id}
                  className={`p-4 rounded-xl border transition space-y-3 ${
                    f.review_status === 'ACCEPTED'
                      ? 'bg-emerald-950/15 border-emerald-500/30'
                      : f.review_status === 'EDITED'
                      ? 'bg-sky-950/15 border-sky-500/30'
                      : f.review_status === 'REJECTED'
                      ? 'bg-slate-950/40 border-slate-800 opacity-60'
                      : 'bg-slate-800/40 border-slate-700/80'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-white">Issue #{index + 1}</span>
                      <span className="text-[10px] text-slate-400 uppercase font-mono">[{f.category}]</span>
                      <span
                        className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                          f.severity === 'CRITICAL'
                            ? 'bg-rose-500/20 text-rose-300'
                            : f.severity === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-300'
                            : 'bg-sky-500/20 text-sky-300'
                        }`}
                      >
                        {f.severity}
                      </span>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      <button
                        onClick={() => handleAction(f.id, 'ACCEPTED')}
                        disabled={isLoading}
                        className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                          f.review_status === 'ACCEPTED'
                            ? 'bg-emerald-600 text-white'
                            : 'bg-slate-800 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30'
                        }`}
                        title="Accept this suggestion and replace text"
                      >
                        <Check className="h-3.5 w-3.5" />
                        <span>Accept</span>
                      </button>

                      <button
                        onClick={() => {
                          setEditingFindingId(f.id);
                          setCustomRevisionText(f.reviewed_revision || f.suggested_revision || '');
                        }}
                        className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                          f.review_status === 'EDITED'
                            ? 'bg-sky-600 text-white'
                            : 'bg-slate-800 hover:bg-sky-600/30 text-sky-400 border border-sky-500/30'
                        }`}
                        title="Edit suggestion before applying"
                      >
                        <Edit2 className="h-3.5 w-3.5" />
                        <span>Edit</span>
                      </button>

                      <button
                        onClick={() => handleAction(f.id, 'REJECTED')}
                        disabled={isLoading}
                        className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center space-x-1 transition ${
                          f.review_status === 'REJECTED'
                            ? 'bg-slate-700 text-white'
                            : 'bg-slate-800 hover:bg-slate-700 text-slate-400 border border-slate-700'
                        }`}
                        title="Reject suggestion and retain original"
                      >
                        <RotateCcw className="h-3.5 w-3.5" />
                        <span>Reject</span>
                      </button>
                    </div>
                  </div>

                  {/* Flagged Original vs Suggested */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div>
                      <span className="text-[10px] text-rose-400 font-semibold block mb-0.5">Flagged Original:</span>
                      <div className="bg-rose-950/20 border border-rose-500/20 text-rose-200 p-2 rounded">
                        "{f.flagged_text}"
                      </div>
                    </div>

                    <div>
                      <span className="text-[10px] text-emerald-400 font-semibold block mb-0.5">
                        {f.review_status === 'EDITED' ? 'Custom Edited Revision:' : 'Suggested Revision:'}
                      </span>
                      <div className="bg-emerald-950/20 border border-emerald-500/20 text-emerald-200 p-2 rounded">
                        "{f.reviewed_revision || f.suggested_revision}"
                      </div>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400">{f.explanation}</p>

                  {/* Inline Edit Box */}
                  {isEditing && (
                    <div className="p-3 bg-slate-900 border border-sky-500/40 rounded-xl space-y-2 mt-2">
                      <label className="text-[11px] font-semibold text-white block">
                        Edit Revision Text (Creator-Intent Preserving):
                      </label>
                      <input
                        type="text"
                        value={customRevisionText}
                        onChange={(e) => setCustomRevisionText(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                      />
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => setEditingFindingId(null)}
                          className="px-2.5 py-1 text-xs text-slate-400 hover:text-white"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleAction(f.id, 'EDITED', customRevisionText)}
                          className="px-3 py-1 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-semibold"
                        >
                          Save Custom Revision
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Final Sign-Off Decision Section */}
          <div className="pt-6 border-t border-slate-800 space-y-4 bg-slate-950/40 p-5 rounded-2xl border">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Final Publication Gate & Reviewer Sign-Off</span>
            </h4>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Authorised Reviewer Name</label>
                <input
                  type="text"
                  value={reviewerName}
                  onChange={(e) => setReviewerName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Reviewer Role</label>
                <input
                  type="text"
                  value={reviewerRole}
                  onChange={(e) => setReviewerRole(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-slate-400 font-medium mb-1">Governance Notes / Audit Rationale</label>
                <input
                  type="text"
                  placeholder="e.g. Approved with accepted terminology revisions. Complies with 2024 messaging policy."
                  value={decisionNotes}
                  onChange={(e) => setDecisionNotes(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-end gap-3 pt-3">
              <button
                type="button"
                onClick={() => handleFinalDecision('REJECTED')}
                disabled={isSubmittingDecision}
                className="px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold transition disabled:opacity-50"
              >
                Reject Publication
              </button>

              <button
                type="button"
                onClick={() => handleFinalDecision('CHANGES_REQUESTED')}
                disabled={isSubmittingDecision}
                className="px-4 py-2 bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-semibold transition disabled:opacity-50"
              >
                Request Creator Changes
              </button>

              <button
                type="button"
                onClick={() => handleFinalDecision('APPROVED')}
                disabled={isSubmittingDecision}
                className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition shadow-lg shadow-emerald-600/25 disabled:opacity-50 flex items-center space-x-1.5"
              >
                <Check className="h-4 w-4" />
                <span>Approve for Publication</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

