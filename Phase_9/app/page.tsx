"use client";

import React, { useState, useEffect, useRef } from 'react';
import { schemes } from '../data/schemes';
import QuestionCategories from '../components/QuestionCategories';

// --- Types ---
interface Message {
    role: 'user' | 'assistant';
    content: string;
    documents?: string[];
}

// --- Icons (Simple SVG Components) ---
const IndLogo = () => (
    <div className="flex items-center gap-2">
        <div className="bg-[#00d09c] p-1.5 rounded-lg">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" />
                <path d="M2 17L12 22L22 17" opacity="0.5" stroke="white" strokeWidth="2" strokeLinecap="round" />
                <path d="M2 12L12 17L22 12" opacity="0.8" stroke="white" strokeWidth="2" strokeLinecap="round" />
            </svg>
        </div>
        <span className="text-xl font-bold tracking-tight text-[#1a1a1a]">INDMoney <span className="text-gray-400 font-medium mx-1">•</span> Mutual Fund Facts Assistant</span>
    </div>
);

const SendIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
    </svg>
);

export default function INDMoneyChatbot() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [selectedScheme, setSelectedScheme] = useState<string>("");
    const [lastUpdated, setLastUpdated] = useState<string>("");
    const scrollRef = useRef<HTMLDivElement>(null);

    // Fetch metadata
    useEffect(() => {
        fetch('http://localhost:8000/metadata')
            .then(res => res.json())
            .then(data => setLastUpdated(data.data_last_updated))
            .catch(() => setLastUpdated("05-03-2026")); // Fallback
    }, []);

    const supportedSchemes = schemes.map(s => s.name);

    // Auto-scroll logic
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isLoading]);

    const handleSend = async (text: string = input) => {
        if (!text.trim()) return;

        const userMessage: Message = { role: 'user', content: text };
        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: text,
                    scheme: selectedScheme || undefined
                }),
            });

            if (!response.ok) throw new Error("API request failed");

            const data = await response.json();
            const assistantMessage: Message = {
                role: 'assistant',
                content: data.answer,
                documents: data.documents
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I'm sorry, I'm having trouble connecting to the facts database. Please ensure the backend is running."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#f1f3f6] font-sans selection:bg-[#00d09c]/30">

            {/* Top Navigation */}
            <nav className="fixed top-0 w-full h-16 bg-white border-b border-gray-200 z-50 px-8 flex items-center justify-between shadow-sm">
                <div className="flex items-center">
                    <IndLogo />
                </div>
                <div className="flex flex-col items-end">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest leading-none">Data sourced from official AMC / SEBI / AMFI documents</span>
                    {lastUpdated && (
                        <span className="text-[10px] font-bold text-[#00d09c] mt-1">Last updated: {lastUpdated}</span>
                    )}
                </div>
            </nav>

            <div className="max-w-[1400px] mx-auto pt-24 px-8 grid grid-cols-12 gap-8 items-start">

                {/* Left Sidebar */}
                <aside className="col-span-3 space-y-6 hidden lg:block sticky top-24">
                    <div id="facts-info" className="bg-white rounded-3xl p-6 shadow-sm border border-gray-100 scroll-mt-24">
                        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-6">FACTUAL MUTUAL FUND INFORMATION</h3>
                        <ul className="space-y-5">
                            {[
                                { label: 'Expense ratios', icon: '💰' },
                                { label: 'Exit load rules', icon: '⚡' },
                                { label: 'Minimum SIP amount', icon: '📈' },
                                { label: 'ELSS lock-in period', icon: '🔒' },
                                { label: 'Riskometer meaning', icon: '🛡️' },
                                { label: 'Benchmark information', icon: '📊' }
                            ].map((item, i) => (
                                <li key={i} className="flex items-center gap-4 text-sm font-semibold text-gray-700 group cursor-default">
                                    <span className="w-8 h-8 flex items-center justify-center bg-gray-50 rounded-lg group-hover:bg-[#00d09c]/10 transition-colors">{item.icon}</span>
                                    {item.label}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div id="verified-data" className="bg-[#e9fbf6] rounded-3xl p-6 border border-[#c3f1e5] scroll-mt-24">
                        <div className="flex items-center gap-2 mb-3 text-[#008d6a]">
                            <span className="text-lg">✅</span>
                            <h4 className="font-bold text-sm">Verified Data</h4>
                        </div>
                        <p className="text-xs leading-relaxed text-[#006a50] opacity-80">
                            Information is sourced directly from official AMC, SEBI, and AMFI documents including Scheme Information Documents (SID), Key Information Memorandums (KIM), and scheme factsheets.
                        </p>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="col-span-12 lg:col-span-9 space-y-8">

                    {/* Hero Section */}
                    <div className="bg-[#ebf8f5] rounded-[40px] p-10 relative overflow-hidden">
                        <div className="relative z-10">
                            <h1 className="text-4xl font-extrabold text-[#1a1a1a] mb-4">Mutual Fund Facts Assistant</h1>
                            <p className="text-gray-600 max-w-2xl leading-relaxed mb-4">
                                Ask factual questions about mutual funds using verified AMC, SEBI, and AMFI sources.
                            </p>
                            <div className="text-xs text-gray-500 font-medium">
                                Try asking:
                                <ul className="mt-1 space-y-1">
                                    <li>• What is the exit load of SBI Small Cap Fund?</li>
                                    <li>• What is the lock-in period for ELSS funds?</li>
                                    <li>• What does the riskometer indicate?</li>
                                </ul>
                            </div>
                        </div>
                        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-[#00d09c]/20 to-transparent rounded-full blur-3xl -mr-20 -mt-20"></div>
                    </div>

                    {/* What Can I Ask? Section */}
                    <div id="what-can-i-ask" className="scroll-mt-24">
                        <QuestionCategories onSelectQuestion={(q) => setInput(q)} />
                    </div>

                    {/* Covered Mutual Funds Section */}
                    <div id="covered-funds" className="scroll-mt-24">
                        <div className="flex flex-col mb-4 px-2">
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Covered Mutual Funds</h4>
                            <p className="text-[10px] text-gray-500 font-medium mt-1">All fund data is sourced exclusively from official AMC documents.</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {schemes.map((scheme, i) => (
                                <div key={i} className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm flex items-center justify-between group">
                                    <div className="space-y-2">
                                        <h5 className="text-sm font-bold text-gray-800">{scheme.name}</h5>
                                        <span className="inline-block px-3 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold rounded-full uppercase tracking-wider">{scheme.category}</span>
                                    </div>
                                    <a
                                        href={scheme.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-[#00d09c] text-xs font-bold hover:underline flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity"
                                    >
                                        View Official Page
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                                            <line x1="5" y1="12" x2="19" y2="12"></line>
                                            <polyline points="12 5 19 12 12 19"></polyline>
                                        </svg>
                                    </a>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Chat Interface */}
                    <div className="bg-white rounded-[40px] shadow-xl shadow-gray-200/50 border border-gray-100 flex flex-col h-[600px] overflow-hidden">
                        {/* Scrollable Messages */}
                        <div ref={scrollRef} className="flex-1 overflow-y-auto p-10 space-y-8 custom-scrollbar">
                            {messages.length === 0 && (
                                <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
                                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">💬</div>
                                    <p className="text-sm font-medium">Start a conversation with the assistant</p>
                                </div>
                            )}
                            {messages.map((msg, i) => (
                                <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                    <div className={`
                    max-w-[80%] px-6 py-4 rounded-3xl text-[15px] leading-relaxed relative
                    ${msg.role === 'user'
                                            ? 'bg-[#00d09c] text-white rounded-tr-none font-medium'
                                            : 'bg-[#f1f3f6] text-gray-800 rounded-tl-none border border-gray-100 shadow-sm'
                                        }
                  `}>
                                        {msg.role === 'assistant' && msg.documents && msg.documents.length > 0 && (
                                            <div className="mb-4 pb-2 border-b border-gray-100 flex flex-col gap-2">
                                                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Retrieved from verified documents:</span>
                                                <div className="flex flex-wrap gap-2">
                                                    {msg.documents.map((doc, idx) => (
                                                        <span key={idx} className="px-2 py-1 bg-white border border-gray-200 rounded-lg text-[10px] font-semibold text-gray-600 shadow-sm">
                                                            📄 {doc}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                        {msg.content.split('\n').map((line, idx) => {
                                            if (line.toLowerCase().startsWith('source:')) {
                                                const urlMatch = line.match(/https?:\/\/[^\s]+/);
                                                if (urlMatch) {
                                                    const url = urlMatch[0];
                                                    return (
                                                        <div key={idx} className="mt-4 pt-4 border-t border-gray-100">
                                                            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#00d09c]/10 text-[#008d6a] rounded-lg border border-[#00d09c]/20 shadow-sm">
                                                                <span className="text-[10px] font-bold uppercase tracking-widest">Verified Source</span>
                                                                <a href={url} target="_blank" rel="noopener noreferrer" className="text-[11px] font-bold hover:underline truncate max-w-[200px]">
                                                                    Official AMC Page →
                                                                </a>
                                                            </div>
                                                            <div className="mt-2 text-[9px] text-gray-400 font-medium truncate opacity-60">
                                                                {url}
                                                            </div>
                                                        </div>
                                                    );
                                                }
                                            }
                                            if (!line.trim()) return <br key={idx} />;
                                            return <p key={idx}>{line}</p>;
                                        })}
                                        {msg.role === 'assistant' && (
                                            <div className="mt-4 pt-4 border-t border-gray-200">
                                                <p className="text-[10px] font-bold text-gray-500 italic uppercase tracking-wider mb-1">
                                                    Last updated from sources: Official AMC / SEBI / AMFI documents.
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                    <span className="mt-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest px-2">
                                        {msg.role === 'user' ? 'You • Just Now' : 'Assistant • Just Now'}
                                    </span>
                                </div>
                            ))}
                            {isLoading && (
                                <div className="flex flex-col items-start gap-2">
                                    <div className="bg-[#f1f3f6] px-6 py-4 rounded-3xl rounded-tl-none flex flex-col gap-3 min-w-[200px]">
                                        <div className="flex items-center gap-3">
                                            <div className="flex gap-1.5">
                                                <div className="w-1.5 h-1.5 bg-[#00d09c] rounded-full animate-bounce"></div>
                                                <div className="w-1.5 h-1.5 bg-[#00d09c] rounded-full animate-bounce delay-75"></div>
                                                <div className="w-1.5 h-1.5 bg-[#00d09c] rounded-full animate-bounce delay-150"></div>
                                            </div>
                                            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-widest animate-pulse">Searching verified sources...</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input Box */}
                        <div className="p-6 bg-white border-t border-gray-100 relative">
                            {/* Context Indicator */}
                            <div className="absolute -top-10 left-6 right-6 flex items-center gap-2">
                                <div className={`
                                    px-3 py-1.5 rounded-t-xl text-[10px] font-bold uppercase tracking-widest flex items-center gap-2 transition-all duration-300
                                    ${selectedScheme ? 'bg-[#00d09c] text-white' : 'bg-gray-200 text-gray-500'}
                                `}>
                                    <span className="opacity-70">📍 Context:</span>
                                    <span>{selectedScheme || 'All Schemes'}</span>
                                </div>
                            </div>

                            {/* Scheme Selector */}
                            <div className="mb-4 flex items-center gap-3">
                                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Filter by Scheme:</label>
                                <select
                                    value={selectedScheme}
                                    onChange={(e) => setSelectedScheme(e.target.value)}
                                    className="bg-[#f1f3f6] border-none outline-none text-xs font-bold text-gray-600 rounded-lg px-3 py-1.5 cursor-pointer hover:bg-gray-200 transition-colors"
                                >
                                    <option value="">All Schemes</option>
                                    {supportedSchemes.map(s => (
                                        <option key={s} value={s}>{s}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex items-center gap-3 bg-[#f1f3f6] rounded-2xl p-2 pl-6 focus-within:ring-2 ring-[#00d09c]/30 transition-all">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="Ask about expense ratio, exit load, SIP limits, or ELSS lock-in..."
                                    className="flex-1 bg-transparent border-none outline-none text-sm font-medium py-2 text-black placeholder-gray-400"
                                />
                                <button
                                    onClick={() => handleSend()}
                                    disabled={isLoading || !input.trim()}
                                    className="bg-[#00d09c] text-white p-3 rounded-xl disabled:opacity-50 disabled:scale-100 hover:scale-105 active:scale-95 transition-all shadow-lg shadow-[#00d09c]/20"
                                >
                                    <SendIcon />
                                </button>
                            </div>
                            <p className="text-center text-[10px] font-bold text-gray-400 mt-4 tracking-wider uppercase">
                                Facts-only assistant. No investment advice. Information is sourced from official AMC, SEBI, and AMFI websites.
                            </p>
                        </div>
                    </div>

                    {/* Assistant Limitations Section */}
                    <div id="assistant-limitations" className="scroll-mt-24">
                        <div className="bg-amber-50 rounded-[40px] p-10 border border-amber-100 shadow-sm relative overflow-hidden">
                            <div className="relative z-10">
                                <div className="flex items-center gap-3 mb-6">
                                    <span className="text-2xl">⚠️</span>
                                    <h2 className="text-xl font-bold text-amber-900 tracking-tight">What This Assistant Cannot Do</h2>
                                </div>

                                <ul className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                                    {[
                                        "Provide investment advice or recommendations",
                                        "Compare funds or suggest which fund is better",
                                        "Predict returns or calculate CAGR",
                                        "Process personal information such as PAN, Aadhaar, phone numbers, or emails"
                                    ].map((limit, idx) => (
                                        <li key={idx} className="flex items-start gap-3 text-sm font-medium text-amber-800 opacity-90 leading-relaxed">
                                            <span className="mt-1.5 w-1.5 h-1.5 bg-amber-400 rounded-full shrink-0"></span>
                                            {limit}
                                        </li>
                                    ))}
                                </ul>

                                <div className="pt-6 border-t border-amber-200/50">
                                    <p className="text-xs font-bold text-amber-700 uppercase tracking-widest">
                                        This assistant provides factual information only based on official AMC, SEBI, and AMFI documents.
                                    </p>
                                </div>
                            </div>
                            {/* Decorative background element */}
                            <div className="absolute -bottom-10 -right-10 w-48 h-48 bg-amber-200/20 rounded-full blur-3xl"></div>
                        </div>
                    </div>

                </main>
            </div>

            <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        body {
          font-family: 'Inter', sans-serif;
        }

        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #e1e4eb;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #d1d4db;
        }
      `}</style>
        </div>
    );
}
