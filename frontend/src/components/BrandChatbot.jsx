import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Sparkles, Minimize2, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { sendChatMessage } from '../services/api';

export default function BrandChatbot({ currentBrand }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I'm your Sentinel AI Copilot. I'm connected to **${currentBrand?.name || 'your brand'}**'s brand governance guidelines, tone rules, and approved ClaimGuard facts. Ask me to verify a claim or rewrite marketing copy!`,
      model: 'AI Copilot'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  // Update greeting when brand changes
  useEffect(() => {
    if (currentBrand) {
      setMessages([
        {
          role: 'assistant',
          content: `Switched brand context to **${currentBrand.name}**. I'm ready to assist with compliance checking against its tone and ClaimGuard facts!`,
          model: 'AI Copilot'
        }
      ]);
    }
  }, [currentBrand?.id]);

  async function handleSend(textToSend) {
    const text = textToSend || input;
    if (!text.trim() || loading || !currentBrand) return;

    const userMsg = { role: 'user', content: text };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const historyPayload = newMessages.map(m => ({ role: m.role, content: m.content }));
      const res = await sendChatMessage(currentBrand.id, text, historyPayload);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          model: res.model_used || 'AI Copilot'
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'I encountered an issue processing that query. Please try again.',
          model: 'System'
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  const quickPrompts = [
    "What is our verified uptime SLA?",
    "What words are strictly forbidden?",
    "Rewrite: 'our cheap firewall guarantees zero bugs'"
  ];

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center space-x-2.5 px-4 py-3 bg-gradient-to-r from-sky-600 via-indigo-600 to-purple-600 hover:from-sky-500 hover:to-purple-500 text-white rounded-full shadow-2xl shadow-indigo-600/40 border border-white/20 transition-all hover:scale-105 group"
        >
          <div className="relative">
            <Bot className="h-5 w-5" />
            <span className="absolute -top-0.5 -right-0.5 h-2 w-2 bg-emerald-400 rounded-full animate-pulse" />
          </div>
          <span className="text-xs font-bold tracking-wide">Sentinel Copilot</span>
          <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono uppercase">AI Assistant</span>
        </button>
      )}

      {isOpen && (
        <div className="w-88 sm:w-96 h-[520px] bg-slate-900/95 backdrop-blur-xl border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          {/* Header */}
          <div className="px-4 py-3 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-sky-600 to-purple-600 flex items-center justify-center text-white shadow-md">
                <Bot className="h-4 w-4" />
              </div>
              <div>
                <div className="flex items-center space-x-1.5">
                  <h4 className="text-xs font-bold text-white">Sentinel Copilot</h4>
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                </div>
                <div className="flex items-center space-x-1 text-[10px] text-slate-400">
                  <ShieldCheck className="h-3 w-3 text-emerald-400" />
                  <span>Brand Policy Intelligence • {currentBrand?.name}</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
            >
              <Minimize2 className="h-4 w-4" />
            </button>
          </div>

          {/* Quick Prompts */}
          <div className="px-3 py-2 bg-slate-950/40 border-b border-slate-800/60 flex items-center gap-1.5 overflow-x-auto text-[10px]">
            {quickPrompts.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                disabled={loading}
                className="whitespace-nowrap px-2.5 py-1 bg-slate-800/80 hover:bg-slate-700 text-slate-300 rounded-full border border-slate-700 transition shrink-0"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Messages list */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3.5 text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex items-start space-x-2 ${
                  m.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div
                  className={`h-6 w-6 rounded-md flex items-center justify-center shrink-0 mt-0.5 ${
                    m.role === 'user'
                      ? 'bg-sky-600 text-white'
                      : 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                  }`}
                >
                  {m.role === 'user' ? <User className="h-3.5 w-3.5" /> : <Bot className="h-3.5 w-3.5" />}
                </div>

                <div
                  className={`max-w-[82%] px-3.5 py-2.5 rounded-2xl leading-relaxed whitespace-pre-wrap ${
                    m.role === 'user'
                      ? 'bg-sky-600 text-white rounded-tr-none'
                      : 'bg-slate-800/90 text-slate-200 border border-slate-700/60 rounded-tl-none'
                  }`}
                >
                  {m.content}
                  {m.model && m.role === 'assistant' && (
                    <div className="mt-1 text-[9px] text-slate-400 font-mono flex items-center space-x-1">
                      <span>•</span>
                      <span>{m.model}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2 text-slate-400 text-xs pl-2">
                <div className="h-4 w-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                <span className="text-[11px] font-mono">Analyzing context & verifying brand rules...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-3 bg-slate-950/90 border-t border-slate-800 flex items-center space-x-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Ask anything about ${currentBrand?.name || 'brand rules'}...`}
              disabled={loading}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-normal"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 disabled:opacity-40 text-white rounded-xl transition shadow-md"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
