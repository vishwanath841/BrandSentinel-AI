import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ContentSubmitter from './components/ContentSubmitter';
import InspectionReport from './components/InspectionReport';
import BrandDNAEditor from './components/BrandDNAEditor';
import BrandDriftDashboard from './components/BrandDriftDashboard';
import HistoryList from './components/HistoryList';
import HumanReviewModal from './components/HumanReviewModal';
import SettingsModal from './components/SettingsModal';
import BrandChatbot from './components/BrandChatbot';
import { ArrowLeft, PlusCircle, CheckCircle2, ShieldCheck } from 'lucide-react';
import {
  fetchBrands,
  fetchBrandDetail,
  fetchSubmissions,
  fetchSubmissionDetail,
  fetchSettings,
  reinspectSubmission
} from './services/api';

export default function App() {
  const [brands, setBrands] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [brandDetail, setBrandDetail] = useState(null);
  const [activeTab, setActiveTab] = useState('workspace'); // workspace, dna, analytics, history
  const [workspaceView, setWorkspaceView] = useState('submit'); // 'submit' or 'report'
  const [currentSubmission, setCurrentSubmission] = useState(null);
  const [settings, setSettings] = useState(null);

  // Modals
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

  // Loading & Error States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    initApp();
  }, []);

  async function initApp() {
    setLoading(true);
    setError(null);
    try {
      const [brandList, settingsData] = await Promise.all([
        fetchBrands(),
        fetchSettings()
      ]);
      setBrands(brandList);
      setSettings(settingsData);

      if (brandList.length > 0) {
        const initialBrand = brandList[0];
        setSelectedBrand(initialBrand);
        await loadBrandDetail(initialBrand.id);
        await loadLatestSubmission(initialBrand.id);
      }
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to initialize BrandSentinel AI');
    } finally {
      setLoading(false);
    }
  }

  async function loadBrandDetail(brandId) {
    try {
      const detail = await fetchBrandDetail(brandId);
      setBrandDetail(detail);
    } catch (err) {
      console.error(err);
    }
  }

  async function loadLatestSubmission(brandId) {
    try {
      const subs = await fetchSubmissions(brandId);
      if (subs.length > 0) {
        const detailed = await fetchSubmissionDetail(subs[0].id);
        setCurrentSubmission(detailed);
      } else {
        setCurrentSubmission(null);
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function handleSelectBrand(brand) {
    setSelectedBrand(brand);
    setWorkspaceView('submit');
    await loadBrandDetail(brand.id);
    await loadLatestSubmission(brand.id);
  }

  async function handleSubmissionCreated(submission) {
    setCurrentSubmission(submission);
    setWorkspaceView('report');
    setActiveTab('workspace');
  }

  async function handleReinspect(submissionId) {
    try {
      const updated = await reinspectSubmission(submissionId);
      setCurrentSubmission(updated);
    } catch (err) {
      alert(`Re-inspection error: ${err.message}`);
    }
  }

  async function handleRefreshCurrentSubmission() {
    if (!currentSubmission) return;
    try {
      const updated = await fetchSubmissionDetail(currentSubmission.id);
      setCurrentSubmission(updated);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleBrandCreated(newBrand) {
    const brandList = await fetchBrands();
    setBrands(brandList);
    setSelectedBrand(newBrand);
    await loadBrandDetail(newBrand.id);
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-300">
        <div className="h-10 w-10 border-3 border-sky-400 border-t-transparent rounded-full animate-spin mb-4" />
        <h1 className="text-lg font-bold text-white tracking-tight">BrandSentinel AI</h1>
        <p className="text-xs text-slate-500 mt-1">Initializing Brand Governance Engine...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans text-slate-100">
      <Navbar
        brands={brands}
        selectedBrand={selectedBrand}
        onSelectBrand={handleSelectBrand}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        settings={settings}
        onOpenSettings={() => setIsSettingsModalOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 text-rose-300 rounded-2xl text-xs flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={initApp}
              className="px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 rounded-lg font-semibold"
            >
              Retry
            </button>
          </div>
        )}

        {/* TAB: Review Workspace */}
        {activeTab === 'workspace' && (
          <div className="space-y-6">
            {workspaceView === 'submit' || !currentSubmission ? (
              <div className="space-y-4">
                {currentSubmission && (
                  <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2 text-slate-300">
                      <ShieldCheck className="h-4 w-4 text-sky-400" />
                      <span>Previous audit available: <strong className="text-white">{currentSubmission.title}</strong> ({currentSubmission.report?.overall_score || 0}/100)</span>
                    </div>
                    <button
                      onClick={() => setWorkspaceView('report')}
                      className="px-3 py-1 bg-sky-600/20 hover:bg-sky-600/30 text-sky-300 border border-sky-500/30 rounded-lg font-semibold transition"
                    >
                      View Audit Result →
                    </button>
                  </div>
                )}
                <ContentSubmitter
                  brand={selectedBrand}
                  onSubmissionCreated={handleSubmissionCreated}
                />
              </div>
            ) : (
              <div className="space-y-4">
                {/* Dedicated Top Action Bar for Audit Result Page */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-slate-900 border border-slate-800 rounded-2xl">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => setWorkspaceView('submit')}
                      className="flex items-center space-x-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 rounded-xl text-xs font-bold transition shadow-sm"
                    >
                      <ArrowLeft className="h-4 w-4" />
                      <span>Submit New Content</span>
                    </button>
                    <div>
                      <span className="text-xs font-bold text-white block">Audit Result: {currentSubmission.title}</span>
                      <span className="text-[11px] text-slate-400">Viewing executive briefing & findings</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] text-slate-400">Status:</span>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                      {currentSubmission.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                <InspectionReport
                  submission={currentSubmission}
                  onOpenReviewModal={() => setIsReviewModalOpen(true)}
                  onReinspect={handleReinspect}
                />
              </div>
            )}
          </div>
        )}

        {/* TAB: Brand DNA Engine */}
        {activeTab === 'dna' && (
          <BrandDNAEditor
            brand={brandDetail || selectedBrand}
            onRefreshBrand={() => loadBrandDetail(selectedBrand.id)}
            onBrandCreated={handleBrandCreated}
          />
        )}

        {/* TAB: Brand Drift Analytics */}
        {activeTab === 'analytics' && (
          <BrandDriftDashboard brand={selectedBrand} />
        )}

        {/* TAB: History & Audit */}
        {activeTab === 'history' && (
          <HistoryList
            brand={selectedBrand}
            onSelectSubmission={(sub) => {
              setCurrentSubmission(sub);
              setWorkspaceView('report');
              setActiveTab('workspace');
            }}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>BrandSentinel AI • Intelligent Brand Governance Platform</span>
          <span>Lead Developer: <strong>Vishwanath S A</strong> (GM Institute of Technology)</span>
          <span className="font-mono text-[11px] text-slate-600">Built with React, FastAPI, SQLite & NVIDIA Nemotron</span>
        </div>
      </footer>

      {/* Floating AI Copilot Chatbot */}
      <BrandChatbot currentBrand={brandDetail || selectedBrand} />

      {/* Human Review Modal */}
      {isReviewModalOpen && currentSubmission && (
        <HumanReviewModal
          submission={currentSubmission}
          onClose={() => setIsReviewModalOpen(false)}
          onReviewComplete={handleRefreshCurrentSubmission}
        />
      )}

      {/* Settings Modal */}
      {isSettingsModalOpen && (
        <SettingsModal
          settings={settings}
          onClose={() => setIsSettingsModalOpen(false)}
          onSettingsUpdated={setSettings}
        />
      )}
    </div>
  );
}

