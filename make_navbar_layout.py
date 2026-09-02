# -*- coding: utf-8 -*-
import os

fe_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\frontend"

def write_f(rel_path, code):
    p = os.path.join(fe_root, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")
    print(f"Created: {rel_path}")

# 1. components/Navbar.tsx
write_f("components/Navbar.tsx", """
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Building2, FileText, BarChart3, Bot, ShieldAlert, 
  Layers, CheckCircle2, ClipboardList, Activity, Sparkles,
  ChevronRight, RefreshCw, AlertCircle
} from 'lucide-react';
import { api, Company } from '@/lib/api';

export default function Navbar() {
  const pathname = usePathname();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [isSeeding, setIsSeeding] = useState(false);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const list = await api.getCompanies();
      setCompanies(list);
      if (list.length > 0) {
        setSelectedCompany(list[0]);
        localStorage.setItem('active_company_id', list[0].id.toString());
      }
    } catch (e) {
      console.error('Error fetching companies:', e);
    }
  };

  const handleSeedDemo = async () => {
    setIsSeeding(true);
    try {
      const comp = await api.seedDemo();
      await loadCompanies();
      setSelectedCompany(comp);
      localStorage.setItem('active_company_id', comp.id.toString());
      window.location.reload();
    } catch (e) {
      console.error('Seed error:', e);
    } finally {
      setIsSeeding(false);
    }
  };

  const navLinks = [
    { href: '/', label: 'Overview', icon: BarChart3 },
    { href: '/documents', label: 'Documents', icon: FileText },
    { href: '/metrics', label: 'Financials', icon: Layers },
    { href: '/chat', label: 'AI Analyst', icon: Bot },
    { href: '/readiness', label: 'IPO Readiness', icon: CheckCircle2 },
    { href: '/consistency', label: 'Consistency', icon: AlertCircle },
    { href: '/risks', label: 'Risk Center', icon: ShieldAlert },
    { href: '/reviews', label: 'Review Queue', icon: ClipboardList },
    { href: '/evaluation', label: 'AI Evaluation', icon: Activity },
    { href: '/audit', label: 'Audit Trail', icon: RefreshCw },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#0F172A]/90 backdrop-blur-md border-b border-slate-800">
      {/* Top Header Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Logo */}
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 p-0.5 shadow-lg shadow-emerald-500/20">
            <div className="h-full w-full bg-slate-900 rounded-[10px] flex items-center justify-center">
              <Bot className="h-5 w-5 text-emerald-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">IPOReady <span className="text-emerald-400">AI</span></span>
              <span className="px-2 py-0.5 text-[10px] uppercase font-semibold tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
                Superjoin Grade
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Intelligent Document Intelligence & Readiness Platform</p>
          </div>
        </div>

        {/* Company Workspace Switcher & Demo Seeder */}
        <div className="flex items-center space-x-3">
          {companies.length > 0 ? (
            <div className="flex items-center space-x-2 bg-slate-800/80 border border-slate-700/80 px-3 py-1.5 rounded-lg">
              <Building2 className="h-4 w-4 text-emerald-400" />
              <span className="text-xs font-medium text-slate-200">{selectedCompany?.name || companies[0].name}</span>
              <span className="text-[10px] bg-slate-700 px-1.5 py-0.5 rounded text-slate-300">
                {selectedCompany?.sector || 'SaaS'}
              </span>
            </div>
          ) : (
            <span className="text-xs text-slate-400">No company workspace loaded</span>
          )}

          <button
            onClick={handleSeedDemo}
            disabled={isSeeding}
            className="flex items-center space-x-1.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-md shadow-emerald-600/20 transition-all disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>{isSeeding ? 'Seeding...' : 'Load Demo Company'}</span>
          </button>
        </div>
      </div>

      {/* Sub-Navigation Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-slate-800/50 flex space-x-1 overflow-x-auto py-1">
        {navLinks.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium rounded-md whitespace-nowrap transition-all ${
                isActive
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Icon className={`h-3.5 w-3.5 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
              <span>{link.label}</span>
            </Link>
          );
        })}
      </div>
    </header>
  );
}
""")

# 2. app/layout.tsx
write_f("app/layout.tsx", """
import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata = {
  title: 'IPOReady AI - Intelligent IPO Readiness & Financial Document Intelligence',
  description: 'Enterprise financial document analysis, multi-format extraction, RAG, and AI agent platform for merchant bankers and IPO underwriters.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-800/80 bg-[#0F172A] py-4 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>IPOReady AI - Autonomous Financial Document Intelligence Platform</span>
            <div className="flex items-center space-x-4 text-slate-400">
              <span>Deterministic Financial Math</span>
              <span>100% Citation Traceability</span>
              <span>Synthetic Enterprise Dataset</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
""")

print("Navbar and Layout created.")
