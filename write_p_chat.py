# -*- coding: utf-8 -*-
import os

fe_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\frontend"

chat_code = """'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, Send, Sparkles, Terminal, FileText, Calculator, 
  ExternalLink, CheckCircle2, AlertCircle, Shield, ChevronDown, ChevronUp
} from 'lucide-react';
import { api, ChatResponse } from '@/lib/api';

interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  data?: ChatResponse;
  timestamp: string;
}

export default function ChatAnalystPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [companyId, setCompanyId] = useState<number | null>(null);
  const [expandedTools, setExpandedTools] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initChat();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const initChat = async () => {
    const companies = await api.getCompanies();
    if (companies.length > 0) {
      setCompanyId(companies[0].id);
      setMessages([
        {
          id: 'welcome',
          sender: 'agent',
          text: 'Hello! I am your **Autonomous IPO Analyst Agent**. I perform deterministic financial calculations (YoY growth, 3-year CAGR, margins, ratios) and retrieve verified metrics with exact page and spreadsheet cell citations.\\n\\nAsk me anything about Acme Technologies\\' filings or choose a prompt below.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  };

  const handleSend = async (qText?: string) => {
    const query = qText || inputQuery;
    if (!query.trim() || !companyId || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const resp = await api.chat(companyId, query);
      const agentMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: resp.answer,
        data: resp,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, agentMsg]);
    } catch (e) {
      console.error(e);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: 'Error contacting AI Analyst service. Ensure the backend server is running.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleTools = (msgId: string) => {
    setExpandedTools(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const suggestedPrompts = [
    'What was the 3-year revenue CAGR from FY2022 to FY2024?',
    'Calculate EBITDA margin for FY2024 with full formula.',
    'Is there a revenue discrepancy between the Annual Report and Investor Presentation?',
    'What was the cell reference for FY2024 Revenue in the spreadsheet?',
    'What is the company\\'s Debt-to-Equity ratio in FY2024?'
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white">Autonomous IPO Analyst Studio</h1>
            <p className="text-[11px] text-slate-400">Deterministic Tool Calling & Multi-Filing Citation Deep-Linking</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-[11px] text-slate-400">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Deterministic Guardrails Active</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          const isToolsOpen = expandedTools[m.id];

          return (
            <div key={m.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
                isUser 
                  ? 'bg-emerald-600 text-white rounded-br-none shadow-md shadow-emerald-600/20' 
                  : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-bl-none shadow-xl'
              }`}>
                <div className="whitespace-pre-wrap font-sans">
                  {m.text}
                </div>

                {m.data?.calculations && m.data.calculations.length > 0 && (
                  <div className="mt-3 bg-slate-950/80 border border-emerald-500/30 p-3 rounded-lg">
                    <div className="flex items-center space-x-1.5 text-emerald-400 font-bold text-[11px] mb-1.5">
                      <Calculator className="h-3.5 w-3.5" />
                      <span>Deterministic Math Verification</span>
                    </div>
                    {m.data.calculations.map((calc, idx) => (
                      <div key={idx} className="space-y-1 font-mono text-[11px]">
                        <div className="text-slate-400">Formula: <span className="text-slate-200">{calc.formula}</span></div>
                        <div className="text-emerald-400 font-bold">Result: {calc.result}</div>
                      </div>
                    ))}
                  </div>
                )}

                {m.data?.sources && m.data.sources.length > 0 && (
                  <div className="mt-3 border-t border-slate-800/80 pt-2.5">
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1.5">
                      Verified Document Citations ({m.data.sources.length})
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.data.sources.map((src, idx) => (
                        <div key={idx} className="flex items-center space-x-1.5 bg-slate-800/80 border border-slate-700/80 px-2.5 py-1 rounded-md text-[11px] text-slate-300">
                          <FileText className="h-3 w-3 text-emerald-400" />
                          <span className="font-semibold text-white">{src.source_document}</span>
                          {src.page_number && <span className="text-slate-400 font-mono">P.{src.page_number}</span>}
                          {src.cell_reference && <span className="text-blue-400 font-mono">{src.cell_reference}</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {m.data?.tools_executed && m.data.tools_executed.length > 0 && (
                  <div className="mt-3 border-t border-slate-800/80 pt-2">
                    <button 
                      onClick={() => toggleTools(m.id)}
                      className="flex items-center justify-between w-full text-[10px] text-slate-400 hover:text-slate-200"
                    >
                      <div className="flex items-center space-x-1 font-mono">
                        <Terminal className="h-3 w-3 text-purple-400" />
                        <span>Tool Execution Steps ({m.data.tools_executed.length})</span>
                      </div>
                      {isToolsOpen ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                    </button>

                    {isToolsOpen && (
                      <div className="mt-2 space-y-2 bg-slate-950/90 p-2.5 rounded-lg border border-slate-800 font-mono text-[10px]">
                        {m.data.tools_executed.map((t, idx) => (
                          <div key={idx} className="border-b border-slate-800/50 pb-1.5 last:border-none last:pb-0">
                            <div className="flex justify-between text-purple-400">
                              <span>tool: {t.tool_name}</span>
                              <span className="text-slate-500">{t.execution_time_ms}ms</span>
                            </div>
                            <div className="text-slate-400 mt-0.5">args: {JSON.stringify(t.arguments)}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className={`text-[9px] mt-2 text-right ${isUser ? 'text-emerald-200' : 'text-slate-500'}`}>
                  {m.timestamp} {m.data?.latency_ms ? `• ${m.data.latency_ms}ms` : ''}
                </div>
              </div>
            </div>
          );
        })}
        {loading && (
          <div className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-900/60 p-3 rounded-xl max-w-xs border border-slate-800">
            <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-emerald-400"></div>
            <span>Executing deterministic tool calling & RAG...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="space-y-2">
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-[11px]">
          <span className="text-slate-500 whitespace-nowrap">Suggested:</span>
          {suggestedPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p)}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 px-2.5 py-1 rounded-full whitespace-nowrap transition-all"
            >
              {p}
            </button>
          ))}
        </div>

        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
          <input
            type="text"
            placeholder="Ask anything about financial metrics, YoY growth, margins, ratios, or citations..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-800 px-4 py-2.5 rounded-xl text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-emerald-500 transition-all shadow-inner"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md shadow-emerald-600/20 transition-all flex items-center space-x-1.5"
          >
            <Send className="h-3.5 w-3.5" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}
"""

os.makedirs(os.path.join(fe_root, "app", "chat"), exist_ok=True)
with open(os.path.join(fe_root, "app", "chat", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(chat_code.strip() + "\n")
print("AI Analyst Studio page created.")
