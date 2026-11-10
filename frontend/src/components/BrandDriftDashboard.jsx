import React, { useState, useEffect } from 'react';
import {
  BarChart3, TrendingUp, AlertTriangle, Lightbulb, CheckCircle2,
  HelpCircle, RefreshCw, Layers, ShieldCheck
} from 'lucide-react';
import { fetchBrandDrift } from '../services/api';

export default function BrandDriftDashboard({ brand }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, [brand]);

  async function loadAnalytics() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchBrandDrift(brand?.id);
      setAnalytics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
        <div className="h-8 w-8 border-2 border-sky-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-xs font-semibold text-white">Aggregating Brand Drift Governance Insights...</p>
      </div>
    );
  }

  if (error || !analytics) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center text-xs text-rose-400">
        Failed to load analytics: {error || 'No data'}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Total Content Submissions
          </span>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white font-mono">{analytics.total_submissions}</span>
            <span className="text-xs text-slate-500">reviewed</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Average Compliance Score
          </span>
          <div className="flex items-baseline space-x-2">
            <span
              className={`text-3xl font-extrabold font-mono ${
                analytics.average_compliance_score >= 80
                  ? 'text-emerald-400'
                  : 'text-amber-400'
              }`}
            >
              {analytics.average_compliance_score}
            </span>
            <span className="text-xs text-slate-500">/100</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Publication Approvals
          </span>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-emerald-400 font-mono">{analytics.approved_count}</span>
            <span className="text-xs text-slate-500">
              ({analytics.total_submissions > 0 ? Math.round((analytics.approved_count / analytics.total_submissions) * 100) : 0}%)
            </span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-1">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Pending / In Review
          </span>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-sky-400 font-mono">{analytics.pending_count}</span>
            <span className="text-xs text-slate-500">awaiting approval</span>
          </div>
        </div>
      </div>

      {/* Proactive Guideline Gap Recommendations */}
      <div className="bg-gradient-to-r from-sky-950/40 via-slate-900 to-indigo-950/40 border border-sky-500/30 rounded-2xl p-6 space-y-4">
        <div className="flex items-center space-x-2.5">
          <Lightbulb className="h-5 w-5 text-amber-400" />
          <h3 className="text-sm font-bold text-white">
            Governance Insights: Automated Guideline Gap Recommendations
          </h3>
        </div>
        <p className="text-xs text-slate-300">
          BrandSentinel AI monitors repeated author corrections to uncover unclear brand documentation and knowledge gaps.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {(analytics.guideline_gap_recommendations || []).map((rec, idx) => (
            <div key={idx} className="p-3.5 bg-slate-900/90 border border-slate-800 rounded-xl space-y-1">
              <span className="text-[11px] font-bold text-sky-400 uppercase tracking-wider block">
                {rec.area}
              </span>
              <p className="text-xs text-slate-300 leading-relaxed">{rec.recommendation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Breakdown: Recurring Violations & Unsupported Claims */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Recurring Terminology Violations */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <Layers className="h-4 w-4 text-rose-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                Top Recurring Terminology Violations
              </h4>
            </div>
            <span className="text-[11px] text-slate-500">Frequency</span>
          </div>

          {(analytics.top_recurring_violations || []).length === 0 ? (
            <p className="text-xs text-slate-500 italic text-center py-6">
              No repeated terminology violations recorded.
            </p>
          ) : (
            <div className="space-y-2.5">
              {analytics.top_recurring_violations.map((v, i) => (
                <div
                  key={i}
                  className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center space-x-2">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-400 font-mono text-[10px] flex items-center justify-center font-bold">
                      {i + 1}
                    </span>
                    <span className="font-mono text-rose-300 font-medium">"{v.term}"</span>
                  </div>
                  <span className="font-mono font-bold text-white bg-slate-800 px-2.5 py-0.5 rounded-full text-[11px]">
                    {v.count} occurrences
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Frequent Unsupported Claims */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 text-amber-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                Unverified Claim Hotspots (ClaimGuard)
              </h4>
            </div>
            <span className="text-[11px] text-slate-500">Author Claims</span>
          </div>

          {(analytics.unsupported_claims_summary || []).length === 0 ? (
            <p className="text-xs text-slate-500 italic text-center py-6">
              No recurring unsupported claims detected.
            </p>
          ) : (
            <div className="space-y-2.5">
              {analytics.unsupported_claims_summary.map((c, i) => (
                <div
                  key={i}
                  className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-1.5 text-xs"
                >
                  <p className="text-slate-300 font-medium italic">"{c.claim}"</p>
                  <div className="flex justify-between items-center text-[10px] text-slate-400">
                    <span className="text-amber-400 font-semibold">{c.status}</span>
                    <span className="font-mono">{c.frequency} submissions flagged</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

