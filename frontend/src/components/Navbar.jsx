import React from 'react';
import { ShieldCheck, Sparkles, Settings, BarChart3, BookOpen, Clock, FileCheck } from 'lucide-react';

export default function Navbar({
  brands,
  selectedBrand,
  onSelectBrand,
  activeTab,
  onSelectTab,
  settings,
  onOpenSettings
}) {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Title */}
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
              <ShieldCheck className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-sky-400 bg-clip-text text-transparent">
                  BrandSentinel AI
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Enterprise v1.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Intelligent Pre-Publication Brand Governance</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => onSelectTab('workspace')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'workspace'
                  ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <FileCheck className="h-4 w-4" />
              <span>Review Workspace</span>
            </button>

            <button
              onClick={() => onSelectTab('dna')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'dna'
                  ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <BookOpen className="h-4 w-4" />
              <span>Brand DNA Engine</span>
            </button>

            <button
              onClick={() => onSelectTab('analytics')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'analytics'
                  ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              <span>Brand Drift Analytics</span>
            </button>

            <button
              onClick={() => onSelectTab('history')}
              className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'history'
                  ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Clock className="h-4 w-4" />
              <span>Audit & History</span>
            </button>
          </nav>

          {/* Right Section: Brand Selector & Engine Badge & Settings */}
          <div className="flex items-center space-x-3">
            {/* Brand Switcher */}
            <div className="relative">
              <select
                aria-label="Select Brand Profile"
                value={selectedBrand?.id || ''}
                onChange={(e) => {
                  const b = brands.find((x) => x.id === parseInt(e.target.value));
                  if (b) onSelectBrand(b);
                }}
                className="bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent cursor-pointer"
              >
                {brands.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name} ({b.rules_count || 0} rules)
                  </option>
                ))}
              </select>
            </div>

            {/* AI Engine Status */}
            <div
              className={`hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
                settings?.gemini_api_key_configured
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
              }`}
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>{settings?.gemini_api_key_configured ? 'Gemini 2.5 Hybrid' : 'Deterministic Engine'}</span>
            </div>

            {/* Settings Trigger */}
            <button
              onClick={onOpenSettings}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              title="Platform Settings & Gemini API Key"
            >
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

