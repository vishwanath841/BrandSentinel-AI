import React, { useState, useEffect } from 'react';
import {
  Clock, CheckCircle2, AlertTriangle, XCircle, Trash2,
  ExternalLink, Filter, FileText, ArrowRight, AlertOctagon
} from 'lucide-react';
import { fetchSubmissions, deleteSubmission, deleteAllSubmissions, fetchSubmissionDetail } from '../services/api';

export default function HistoryList({ brand, onSelectSubmission }) {
  const [submissions, setSubmissions] = useState([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDeletingAll, setIsDeletingAll] = useState(false);

  useEffect(() => {
    loadSubmissions();
  }, [brand, statusFilter]);

  async function loadSubmissions() {
    setLoading(true);
    setError(null);
    try {
      const statusParam = statusFilter === 'ALL' ? null : statusFilter;
      const data = await fetchSubmissions(brand?.id, statusParam);
      setSubmissions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(submissionId, e) {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this submission and its review history?')) return;
    try {
      await deleteSubmission(submissionId);
      loadSubmissions();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteAll() {
    if (!confirm(`Are you sure you want to DELETE ALL ${submissions.length} submission records? This action cannot be undone.`)) {
      return;
    }
    setIsDeletingAll(true);
    try {
      await deleteAllSubmissions(brand?.id);
      loadSubmissions();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsDeletingAll(false);
    }
  }

  async function handleOpen(submissionId) {
    try {
      const detailed = await fetchSubmissionDetail(submissionId);
      onSelectSubmission(detailed);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-sm font-bold text-white flex items-center space-x-2">
            <Clock className="h-4 w-4 text-sky-400" />
            <span>Submission History & Governance Audit Trail</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Full immutable log of content reviewed, scores assigned, and reviewer sign-offs.
          </p>
        </div>

        {/* Actions & Filters */}
        <div className="flex flex-wrap items-center gap-2.5">
          {submissions.length > 0 && (
            <button
              onClick={handleDeleteAll}
              disabled={isDeletingAll}
              className="flex items-center space-x-1.5 px-3 py-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-lg text-xs font-semibold transition disabled:opacity-50"
              title="Delete all submission history"
            >
              <Trash2 className="h-3.5 w-3.5 text-rose-400" />
              <span>{isDeletingAll ? 'Deleting...' : 'Delete All'}</span>
            </button>
          )}

          <div className="flex items-center space-x-1.5">
            <Filter className="h-3.5 w-3.5 text-slate-400" />
            <select
              aria-label="Filter by Status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none"
            >
              <option value="ALL">All Statuses</option>
              <option value="APPROVED">Approved</option>
              <option value="PENDING_REVIEW">Pending Review</option>
              <option value="CHANGES_REQUESTED">Changes Requested</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">
          <div className="h-6 w-6 border-2 border-sky-400 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <span>Loading submission history...</span>
        </div>
      ) : submissions.length === 0 ? (
        <div className="p-12 text-center bg-slate-950/40 rounded-xl text-slate-500 text-xs">
          No submissions found for selected filters. Submit content from the Review Workspace to begin.
        </div>
      ) : (
        <div className="space-y-3">
          {submissions.map((sub) => (
            <div
              key={sub.id}
              onClick={() => handleOpen(sub.id)}
              className="p-4 bg-slate-950/60 hover:bg-slate-800/50 border border-slate-800/80 hover:border-slate-700 rounded-xl transition cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
            >
              <div className="space-y-1 flex-1">
                <div className="flex items-center space-x-2.5">
                  <span className="text-xs font-bold text-white group-hover:text-sky-400 transition">
                    {sub.title}
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase font-mono">
                    [{sub.content_type}]
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-400">
                  <span>By: <strong className="text-slate-300">{sub.creator_name}</strong></span>
                  <span>•</span>
                  <span>Channel: {sub.intended_channel}</span>
                  <span>•</span>
                  <span className="font-mono text-slate-500">
                    {new Date(sub.created_at).toLocaleDateString()} {new Date(sub.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>

              <div className="flex items-center space-x-3 self-end sm:self-center">
                {/* Score */}
                {sub.overall_score !== null && (
                  <div className="text-right">
                    <span
                      className={`text-sm font-extrabold font-mono ${
                        sub.overall_score >= 80
                          ? 'text-emerald-400'
                          : sub.overall_score >= 60
                          ? 'text-amber-400'
                          : 'text-rose-400'
                      }`}
                    >
                      {sub.overall_score}
                    </span>
                    <span className="text-[10px] text-slate-500 block">/100 score</span>
                  </div>
                )}

                {/* Status Pill */}
                <span
                  className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full ${
                    sub.status === 'APPROVED'
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : sub.status === 'CHANGES_REQUESTED'
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                      : sub.status === 'REJECTED'
                      ? 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                      : 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                  }`}
                >
                  {sub.status.replace('_', ' ')}
                </span>

                <button
                  onClick={(e) => handleDelete(sub.id, e)}
                  className="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition"
                  title="Delete submission"
                >
                  <Trash2 className="h-4 w-4" />
                </button>

                <ArrowRight className="h-4 w-4 text-slate-500 group-hover:text-white transition" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

