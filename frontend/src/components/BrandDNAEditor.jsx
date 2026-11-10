import React, { useState } from 'react';
import {
  BookOpen, Plus, Trash2, CheckCircle2, ShieldAlert,
  Palette, FileUp, Sparkles, AlertTriangle, HelpCircle, Layers
} from 'lucide-react';
import {
  addBrandRule, deleteBrandRule, addApprovedFact,
  deleteApprovedFact, extractGuidelinesFromFile, createBrand
} from '../services/api';

export default function BrandDNAEditor({ brand, onRefreshBrand, onBrandCreated }) {
  const [activeSubTab, setActiveSubTab] = useState('rules'); // rules, facts, visual, upload, new_brand
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // New Rule Form State
  const [ruleName, setRuleName] = useState('');
  const [ruleCategory, setRuleCategory] = useState('TERMINOLOGY');
  const [preferredTerm, setPreferredTerm] = useState('');
  const [forbiddenTerms, setForbiddenTerms] = useState('');
  const [ruleSeverity, setRuleSeverity] = useState('HIGH');
  const [ruleRationale, setRuleRationale] = useState('');

  // New Approved Fact Form State
  const [factTopic, setFactTopic] = useState('');
  const [factText, setFactText] = useState('');
  const [factSource, setFactSource] = useState('');

  // Upload Guideline State
  const [uploadFile, setUploadFile] = useState(null);
  const [extractedGuideline, setExtractedGuideline] = useState(null);

  // New Brand State
  const [newBrandName, setNewBrandName] = useState('');
  const [newBrandIndustry, setNewBrandIndustry] = useState('');
  const [newBrandTagline, setNewBrandTagline] = useState('');
  const [newBrandPrimary, setNewBrandPrimary] = useState('#2563EB');

  async function handleAddRule(e) {
    e.preventDefault();
    if (!ruleName || !forbiddenTerms) return;
    setLoading(true);
    setError(null);
    try {
      const forbiddenList = forbiddenTerms.split(',').map((s) => s.trim()).filter(Boolean);
      await addBrandRule(brand.id, {
        rule_name: ruleName,
        category: ruleCategory,
        preferred_term: preferredTerm,
        forbidden_terms: forbiddenList,
        severity: ruleSeverity,
        rationale: ruleRationale,
        is_active: true
      });
      setRuleName('');
      setPreferredTerm('');
      setForbiddenTerms('');
      setRuleRationale('');
      setSuccessMsg('Brand rule added successfully!');
      setTimeout(() => setSuccessMsg(null), 3000);
      onRefreshBrand();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteRule(ruleId) {
    if (!confirm('Are you sure you want to delete this rule?')) return;
    try {
      await deleteBrandRule(ruleId);
      onRefreshBrand();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAddFact(e) {
    e.preventDefault();
    if (!factTopic || !factText) return;
    setLoading(true);
    setError(null);
    try {
      await addApprovedFact(brand.id, {
        claim_topic: factTopic,
        approved_text: factText,
        verification_source: factSource,
        is_active: true
      });
      setFactTopic('');
      setFactText('');
      setFactSource('');
      setSuccessMsg('Approved fact added to ClaimGuard!');
      setTimeout(() => setSuccessMsg(null), 3000);
      onRefreshBrand();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteFact(factId) {
    if (!confirm('Are you sure you want to delete this approved fact?')) return;
    try {
      await deleteApprovedFact(factId);
      onRefreshBrand();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleUploadGuideline(e) {
    e.preventDefault();
    if (!uploadFile) return;
    setLoading(true);
    setError(null);
    try {
      const res = await extractGuidelinesFromFile(uploadFile);
      setExtractedGuideline(res.brand_profile);
      setSuccessMsg(`Extracted Brand DNA from ${res.filename}!`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleApplyExtractedBrand() {
    if (!extractedGuideline) return;
    setLoading(true);
    try {
      const created = await createBrand({
        ...extractedGuideline,
        slug: extractedGuideline.name.toLowerCase().replace(/[^a-z0-9]/g, '-')
      });
      onBrandCreated(created);
      setExtractedGuideline(null);
      setUploadFile(null);
      setActiveSubTab('rules');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateBrand(e) {
    e.preventDefault();
    if (!newBrandName) return;
    setLoading(true);
    try {
      const created = await createBrand({
        name: newBrandName,
        slug: newBrandName.toLowerCase().replace(/[^a-z0-9]/g, '-'),
        industry: newBrandIndustry || 'General',
        tagline: newBrandTagline || '',
        primary_color: newBrandPrimary,
        voice_traits: ['Professional', 'Clear'],
        avoided_tones: ['Aggressive', 'Hyperbolic', 'Slang']
      });
      onBrandCreated(created);
      setNewBrandName('');
      setNewBrandIndustry('');
      setNewBrandTagline('');
      setActiveSubTab('rules');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Brand Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
        <div
          className="absolute -right-16 -top-16 w-56 h-56 rounded-full blur-3xl opacity-15 pointer-events-none"
          style={{ backgroundColor: brand?.primary_color || '#0284c7' }}
        />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center space-x-3">
              <div
                className="w-4 h-4 rounded-full border border-white/20 shadow-sm"
                style={{ backgroundColor: brand?.primary_color || '#0284c7' }}
              />
              <h2 className="text-2xl font-bold text-white tracking-tight">{brand?.name}</h2>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                {brand?.industry || 'Enterprise'}
              </span>
            </div>
            <p className="text-sm text-slate-400 mt-1 italic">"{brand?.tagline || 'Brand Identity Guideline'}"</p>
            <p className="text-xs text-slate-500 mt-2 max-w-2xl">{brand?.mission}</p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveSubTab('upload')}
              className="flex items-center space-x-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 rounded-xl text-xs font-semibold transition"
            >
              <FileUp className="h-4 w-4" />
              <span>Import Guideline Doc</span>
            </button>
            <button
              onClick={() => setActiveSubTab('new_brand')}
              className="flex items-center space-x-2 px-3 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-semibold transition shadow-md shadow-sky-600/20"
            >
              <Plus className="h-4 w-4" />
              <span>New Brand</span>
            </button>
          </div>
        </div>

        {/* Voice Traits & Avoided Tones */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 pt-5 border-t border-slate-800/80">
          <div>
            <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider block mb-2">
              Approved Brand Voice Traits
            </span>
            <div className="flex flex-wrap gap-1.5">
              {(brand?.voice_traits || []).map((trait, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-medium"
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>

          <div>
            <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider block mb-2">
              Avoided & Prohibited Tones
            </span>
            <div className="flex flex-wrap gap-1.5">
              {(brand?.avoided_tones || []).map((tone, i) => (
                <span
                  key={i}
                  className="px-2.5 py-1 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs font-medium"
                >
                  {tone}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveSubTab('rules')}
          className={`pb-3 text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeSubTab === 'rules'
              ? 'text-sky-400 border-b-2 border-sky-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="h-4 w-4" />
          <span>Terminology & Rules ({brand?.rules?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveSubTab('facts')}
          className={`pb-3 text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeSubTab === 'facts'
              ? 'text-sky-400 border-b-2 border-sky-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <CheckCircle2 className="h-4 w-4" />
          <span>ClaimGuard Approved Facts ({brand?.approved_facts?.length || 0})</span>
        </button>

        <button
          onClick={() => setActiveSubTab('visual')}
          className={`pb-3 text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeSubTab === 'visual'
              ? 'text-sky-400 border-b-2 border-sky-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Palette className="h-4 w-4" />
          <span>Visual Identity Palette</span>
        </button>

        <button
          onClick={() => setActiveSubTab('upload')}
          className={`pb-3 text-xs font-semibold transition-all flex items-center space-x-2 ${
            activeSubTab === 'upload'
              ? 'text-sky-400 border-b-2 border-sky-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileUp className="h-4 w-4" />
          <span>Ingest Guideline PDF/DOCX</span>
        </button>
      </div>

      {/* Feedback Messages */}
      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-xl text-xs flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 rounded-xl text-xs flex items-center space-x-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* TAB 1: Rules & Terminology */}
      {activeSubTab === 'rules' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Rules List */}
          <div className="lg:col-span-2 space-y-3">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center justify-between">
              <span>Configured Terminology & Governance Rules</span>
              <span className="text-xs text-slate-500 font-normal">{brand?.rules?.length || 0} active rules</span>
            </h3>

            {(brand?.rules || []).length === 0 ? (
              <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-2xl text-slate-500 text-xs">
                No rules defined yet. Use the form on the right to add brand-specific terminology.
              </div>
            ) : (
              (brand?.rules || []).map((r) => (
                <div
                  key={r.id}
                  className="p-4 bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-xl transition flex items-start justify-between group"
                >
                  <div className="space-y-1.5 flex-1 pr-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-white">{r.rule_name}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase ${
                          r.severity === 'CRITICAL'
                            ? 'bg-rose-500/15 text-rose-400 border border-rose-500/20'
                            : r.severity === 'HIGH'
                            ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
                            : 'bg-sky-500/15 text-sky-400 border border-sky-500/20'
                        }`}
                      >
                        {r.severity}
                      </span>
                      <span className="text-[10px] text-slate-400 uppercase font-mono">{r.category}</span>
                    </div>

                    <div className="text-xs space-y-1">
                      <div className="flex items-baseline space-x-2">
                        <span className="text-rose-400 font-semibold text-[11px]">Prohibited:</span>
                        <div className="flex flex-wrap gap-1">
                          {(r.forbidden_terms || []).map((term, idx) => (
                            <span key={idx} className="bg-rose-950/40 text-rose-300 px-1.5 py-0.5 rounded text-[11px] font-mono">
                              "{term}"
                            </span>
                          ))}
                        </div>
                      </div>

                      {r.preferred_term && (
                        <div className="flex items-baseline space-x-2">
                          <span className="text-emerald-400 font-semibold text-[11px]">Approved Replacement:</span>
                          <span className="bg-emerald-950/40 text-emerald-300 px-1.5 py-0.5 rounded text-[11px] font-mono font-medium">
                            "{r.preferred_term}"
                          </span>
                        </div>
                      )}

                      {r.rationale && (
                        <p className="text-[11px] text-slate-400 italic pt-1">
                          Rationale: {r.rationale}
                        </p>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => handleDeleteRule(r.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
                    title="Delete rule"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Add Rule Form */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 h-fit space-y-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Plus className="h-4 w-4 text-sky-400" />
              <span>Add Terminology Rule</span>
            </h4>

            <form onSubmit={handleAddRule} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Rule Name</label>
                <input
                  type="text"
                  placeholder="e.g. Approved Product Nomenclature"
                  value={ruleName}
                  onChange={(e) => setRuleName(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 font-medium mb-1">Category</label>
                  <select
                    value={ruleCategory}
                    onChange={(e) => setRuleCategory(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-white focus:outline-none"
                  >
                    <option value="TERMINOLOGY">Terminology</option>
                    <option value="MESSAGING">Messaging</option>
                    <option value="LEGAL">Legal / SLA</option>
                    <option value="COMPETITOR">Competitor</option>
                    <option value="STYLE">Style & Slang</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-medium mb-1">Severity</label>
                  <select
                    value={ruleSeverity}
                    onChange={(e) => setRuleSeverity(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-2 text-white focus:outline-none"
                  >
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">
                  Prohibited / Forbidden Terms (comma separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. magic cloud, infinite storage, cheap tier"
                  value={forbiddenTerms}
                  onChange={(e) => setForbiddenTerms(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Approved Preferred Replacement</label>
                <input
                  type="text"
                  placeholder="e.g. ApexCloud Data Fabric"
                  value={preferredTerm}
                  onChange={(e) => setPreferredTerm(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Governance Rationale</label>
                <textarea
                  rows={2}
                  placeholder="Why is this required? (Explains issue to creators)"
                  value={ruleRationale}
                  onChange={(e) => setRuleRationale(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-semibold transition shadow-md shadow-sky-600/20 disabled:opacity-50"
              >
                {loading ? 'Adding Rule...' : 'Save Rule to Brand DNA'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 2: ClaimGuard Facts */}
      {activeSubTab === 'facts' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-200">
                ClaimGuard Knowledge Base (Approved Facts & Proof Points)
              </h3>
              <span className="text-xs text-slate-500">{brand?.approved_facts?.length || 0} facts</span>
            </div>
            <p className="text-xs text-slate-400">
              ClaimGuard compares promotional statements against these approved facts. Unsubstantiated claims are
              safely labeled as requiring review rather than dismissed as false.
            </p>

            {(brand?.approved_facts || []).length === 0 ? (
              <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-2xl text-slate-500 text-xs">
                No approved facts yet. Add audited metrics and proof points to enable factual claim verification.
              </div>
            ) : (
              (brand?.approved_facts || []).map((fact) => (
                <div
                  key={fact.id}
                  className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2 relative group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-sky-400 uppercase tracking-wide">
                      {fact.claim_topic}
                    </span>
                    <button
                      onClick={() => handleDeleteFact(fact.id)}
                      className="p-1 text-slate-500 hover:text-rose-400 rounded transition"
                      title="Delete approved fact"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <p className="text-xs text-slate-200 font-medium bg-slate-800/40 p-2.5 rounded-lg border border-slate-700/50">
                    "{fact.approved_text}"
                  </p>

                  {fact.verification_source && (
                    <div className="text-[11px] text-slate-400 flex items-center space-x-1.5">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                      <span>Source: {fact.verification_source}</span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Add Fact Form */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 h-fit space-y-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
              <Plus className="h-4 w-4 text-emerald-400" />
              <span>Add Approved Fact / Claim</span>
            </h4>

            <form onSubmit={handleAddFact} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-medium mb-1">Claim Topic</label>
                <input
                  type="text"
                  placeholder="e.g. SLA & Uptime Guarantee"
                  value={factTopic}
                  onChange={(e) => setFactTopic(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Exact Approved Text / Fact</label>
                <textarea
                  rows={3}
                  placeholder="e.g. ApexCloud guarantees 99.99% monthly uptime SLA backed by financial credits."
                  value={factText}
                  onChange={(e) => setFactText(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-400 font-medium mb-1">Verification Source</label>
                <input
                  type="text"
                  placeholder="e.g. Enterprise SLA Agreement 2024 / SOC 2 Audit"
                  value={factSource}
                  onChange={(e) => setFactSource(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold transition shadow-md shadow-emerald-600/20 disabled:opacity-50"
              >
                {loading ? 'Saving...' : 'Add Fact to ClaimGuard'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 3: Visual Identity */}
      {activeSubTab === 'visual' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-white">Brand Visual Palette & Accessibility Standard</h3>
            <p className="text-xs text-slate-400 mt-1">
              Visual Brand Inspector extracts dominant color clusters from uploaded images using OpenCV and compares
              them against this palette, checking for color distance and WCAG 4.5:1 contrast standards.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div className="space-y-2 p-3 bg-slate-800/60 rounded-xl border border-slate-700/50">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Primary Brand</span>
              <div
                className="h-16 w-full rounded-lg shadow-inner flex items-center justify-center font-mono text-xs font-bold text-white shadow-black/40"
                style={{ backgroundColor: brand?.primary_color || '#1E3A8A' }}
              >
                {brand?.primary_color || '#1E3A8A'}
              </div>
            </div>

            <div className="space-y-2 p-3 bg-slate-800/60 rounded-xl border border-slate-700/50">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Secondary</span>
              <div
                className="h-16 w-full rounded-lg shadow-inner flex items-center justify-center font-mono text-xs font-bold text-white shadow-black/40"
                style={{ backgroundColor: brand?.secondary_color || '#0284C7' }}
              >
                {brand?.secondary_color || '#0284C7'}
              </div>
            </div>

            <div className="space-y-2 p-3 bg-slate-800/60 rounded-xl border border-slate-700/50">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Accent Color</span>
              <div
                className="h-16 w-full rounded-lg shadow-inner flex items-center justify-center font-mono text-xs font-bold text-white shadow-black/40"
                style={{ backgroundColor: brand?.accent_color || '#10B981' }}
              >
                {brand?.accent_color || '#10B981'}
              </div>
            </div>

            <div className="space-y-2 p-3 bg-slate-800/60 rounded-xl border border-slate-700/50">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Background</span>
              <div
                className="h-16 w-full rounded-lg shadow-inner flex items-center justify-center font-mono text-xs font-bold text-slate-900 border border-slate-600"
                style={{ backgroundColor: brand?.background_color || '#FFFFFF' }}
              >
                {brand?.background_color || '#FFFFFF'}
              </div>
            </div>

            <div className="space-y-2 p-3 bg-slate-800/60 rounded-xl border border-slate-700/50">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Body Text</span>
              <div
                className="h-16 w-full rounded-lg shadow-inner flex items-center justify-center font-mono text-xs font-bold text-white shadow-black/40"
                style={{ backgroundColor: brand?.text_color || '#0F172A' }}
              >
                {brand?.text_color || '#0F172A'}
              </div>
            </div>
          </div>

          <div className="p-4 bg-slate-800/40 border border-slate-700/60 rounded-xl flex items-center justify-between text-xs text-slate-300">
            <div>
              <span className="font-semibold text-white">Color Match Tolerance:</span>
              <span className="ml-2 font-mono text-sky-400">{brand?.color_tolerance || 40.0} ΔE</span>
              <span className="ml-3 text-slate-400">(Maximum Euclidean RGB distance allowed for brand alignment)</span>
            </div>
            <div className="text-[11px] text-emerald-400 font-semibold flex items-center space-x-1">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>WCAG AA 4.5:1 Checked</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Guideline Upload & Extraction */}
      {activeSubTab === 'upload' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
              <Sparkles className="h-4 w-4 text-sky-400" />
              <span>Automated Brand Guideline Extraction</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Upload your brand's style guide or PDF handbook. BrandSentinel AI parses text using PyMuPDF and python-docx,
              extracting colors, tone parameters, terminology dos & don'ts, and verified facts into a structured Brand DNA profile.
            </p>
          </div>

          <form onSubmit={handleUploadGuideline} className="space-y-4">
            <div className="border-2 border-dashed border-slate-700 hover:border-sky-500/60 rounded-xl p-8 text-center transition bg-slate-950/40">
              <FileUp className="h-10 w-10 text-sky-400 mx-auto mb-3" />
              <label className="cursor-pointer">
                <span className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-sky-500/30 rounded-xl text-xs font-semibold inline-block transition">
                  Select Brand Guideline Document (.pdf, .docx, .txt)
                </span>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                  onChange={(e) => setUploadFile(e.target.files[0])}
                />
              </label>
              {uploadFile && (
                <p className="text-xs text-emerald-400 mt-3 font-medium">Selected: {uploadFile.name}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={!uploadFile || loading}
              className="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-semibold transition disabled:opacity-50 shadow-md shadow-sky-600/20"
            >
              {loading ? 'Extracting Brand DNA...' : 'Run Automated Extraction'}
            </button>
          </form>

          {/* Extracted Preview */}
          {extractedGuideline && (
            <div className="p-5 bg-slate-800/80 border border-sky-500/30 rounded-xl space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span>Extracted Brand DNA Preview</span>
                </h4>
                <button
                  onClick={handleApplyExtractedBrand}
                  className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition shadow-md shadow-emerald-600/20"
                >
                  Create New Brand Profile from Extraction
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Brand Name</span>
                  <span className="font-bold text-white">{extractedGuideline.name}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Industry</span>
                  <span className="font-bold text-white">{extractedGuideline.industry}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-slate-400 block text-[11px]">Tagline</span>
                  <span className="text-slate-200 italic">{extractedGuideline.tagline}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: Create New Brand */}
      {activeSubTab === 'new_brand' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 max-w-xl">
          <h3 className="text-sm font-semibold text-white">Create New Brand Profile</h3>
          <p className="text-xs text-slate-400">
            For agencies managing multi-brand governance or multi-client accounts.
          </p>

          <form onSubmit={handleCreateBrand} className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-400 font-medium mb-1">Brand Name</label>
              <input
                type="text"
                placeholder="e.g. NovaPay Fintech"
                value={newBrandName}
                onChange={(e) => setNewBrandName(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
                required
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Industry</label>
              <input
                type="text"
                placeholder="e.g. Regulated Financial Services"
                value={newBrandIndustry}
                onChange={(e) => setNewBrandIndustry(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Tagline</label>
              <input
                type="text"
                placeholder="e.g. Next-Generation Compliant Global Payments"
                value={newBrandTagline}
                onChange={(e) => setNewBrandTagline(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-medium mb-1">Primary Brand Color (Hex)</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={newBrandPrimary}
                  onChange={(e) => setNewBrandPrimary(e.target.value)}
                  className="h-8 w-12 rounded cursor-pointer bg-transparent border-0"
                />
                <input
                  type="text"
                  value={newBrandPrimary}
                  onChange={(e) => setNewBrandPrimary(e.target.value)}
                  className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white font-mono text-xs w-28"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-semibold transition shadow-md shadow-sky-600/20 disabled:opacity-50 mt-4"
            >
              {loading ? 'Creating...' : 'Create Brand Profile'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

