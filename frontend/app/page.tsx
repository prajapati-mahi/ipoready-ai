'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Building2, TrendingUp, DollarSign, AlertTriangle, ShieldCheck, 
  ArrowUpRight, ArrowDownRight, Layers, Bot, CheckCircle2, Sparkles
} from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import { api, Company, FinancialMetric, IPOReadiness, FinancialRisk, ConsistencyCheck } from '@/lib/api';

export default function Dashboard() {
  const [company, setCompany] = useState<Company | null>(null);
  const [metrics, setMetrics] = useState<FinancialMetric[]>([]);
  const [readiness, setReadiness] = useState<IPOReadiness | null>(null);
  const [risks, setRisks] = useState<FinancialRisk[]>([]);
  const [inconsistencies, setInconsistencies] = useState<ConsistencyCheck[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const c = companies[0];
        setCompany(c);
        const [mList, rData, rkList, incList] = await Promise.all([
          api.getMetrics(c.id),
          api.getReadiness(c.id),
          api.getRisks(c.id),
          api.getConsistency(c.id)
        ]);
        setMetrics(mList);
        setReadiness(rData);
        setRisks(rkList);
        setInconsistencies(incList);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const revenueChartData = [
    { year: 'FY2022', revenue: 78.0, ebitda: 17.0, pat: 9.5 },
    { year: 'FY2023', revenue: 100.0, ebitda: 24.0, pat: 14.2 },
    { year: 'FY2024', revenue: 125.0, ebitda: 31.25, pat: 18.75 }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-center py-20 bg-slate-900/50 border border-slate-800 rounded-2xl p-8 max-w-xl mx-auto">
        <Sparkles className="h-12 w-12 text-emerald-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">No Company Workspace Active</h2>
        <p className="text-sm text-slate-400 mb-6">Load the pre-configured Acme Technologies synthetic filing dataset to explore the full document intelligence pipeline.</p>
        <button
          onClick={async () => {
            await api.seedDemo();
            window.location.reload();
          }}
          className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm px-5 py-2.5 rounded-lg shadow-lg shadow-emerald-600/20"
        >
          Load Demo Company (Acme Technologies)
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800/80 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <h1 className="text-2xl font-bold text-white tracking-tight">{company.name}</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
              Target IPO: {company.target_ipo_date || 'Q4 FY25'}
            </span>
          </div>
          <p className="text-xs text-slate-400">CIN: {company.cin || 'U72200MH2018PTC308912'} | Sector: {company.sector}</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Link
            href="/chat"
            className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-md shadow-emerald-600/20 transition-all"
          >
            <Bot className="h-4 w-4" />
            <span>Open AI Analyst</span>
          </Link>
          <Link
            href="/readiness"
            className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2 rounded-lg border border-slate-700 transition-all"
          >
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>Score: {readiness?.overall_score || 82.5}/100</span>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Revenue (FY2024)</span>
            <span className="flex items-center text-xs font-bold text-emerald-400">
              <ArrowUpRight className="h-3.5 w-3.5 mr-0.5" /> +25.0% YoY
            </span>
          </div>
          <div className="text-2xl font-bold text-white">₹125.0 Cr</div>
          <p className="text-[11px] text-slate-500 mt-1">Source: Annual Report Page 74</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">EBITDA (FY2024)</span>
            <span className="text-xs font-semibold text-emerald-400">25.0% Margin</span>
          </div>
          <div className="text-2xl font-bold text-white">₹31.25 Cr</div>
          <p className="text-[11px] text-slate-500 mt-1">+30.2% YoY growth from ₹24.0 Cr</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">PAT / Net Profit</span>
            <span className="text-xs font-semibold text-emerald-400">15.0% Margin</span>
          </div>
          <div className="text-2xl font-bold text-white">₹18.75 Cr</div>
          <p className="text-[11px] text-slate-500 mt-1">Net Worth: ₹85.0 Cr</p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-slate-400">Operating Cash Flow</span>
            <span className="flex items-center text-xs font-bold text-rose-400">
              <ArrowDownRight className="h-3.5 w-3.5 mr-0.5" /> -32.0% YoY
            </span>
          </div>
          <div className="text-2xl font-bold text-white">₹27.20 Cr</div>
          <p className="text-[11px] text-rose-400/80 mt-1">Working capital divergence flagged</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/70 border border-slate-800 p-5 rounded-xl flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">Multi-Year Financial Trajectory (FY22 - FY24)</h3>
              <p className="text-xs text-slate-400">Extracted from Audited P&L Statements and Financial Model Spreadsheets</p>
            </div>
            <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2.5 py-1 rounded">
              3-Yr CAGR: 26.6%
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueChartData}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="colorEbitda" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="year" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} tickFormatter={(v) => `₹${v}Cr`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`₹${val} Cr`, '']}
                />
                <Area type="monotone" dataKey="revenue" name="Revenue" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" />
                <Area type="monotone" dataKey="ebitda" name="EBITDA" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#colorEbitda)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white">IPO Readiness Pillar Score</h3>
              <span className="text-xs text-emerald-400 font-semibold">{readiness?.overall_score || 82.5} / 100</span>
            </div>
            <p className="text-xs text-slate-400 mb-4">Internal weighted readiness scorecard for underwriters</p>

            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1 text-slate-300">
                  <span>Financial Completeness</span>
                  <span className="font-semibold">{readiness?.financial_completeness_score || 20.0}/20</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: '100%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1 text-slate-300">
                  <span>Cross-Doc Consistency</span>
                  <span className="font-semibold text-amber-400">{readiness?.financial_consistency_score || 16.0}/20</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-amber-400 h-full rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1 text-slate-300">
                  <span>Profitability & Margins</span>
                  <span className="font-semibold">{readiness?.profitability_score || 12.0}/15</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1 text-slate-300">
                  <span>Cash Flow Health</span>
                  <span className="font-semibold text-amber-400">{readiness?.cashflow_score || 10.0}/15</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-amber-400 h-full rounded-full" style={{ width: '66%' }}></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs mb-1 text-slate-300">
                  <span>Debt Health (D/E &lt; 1.5x)</span>
                  <span className="font-semibold">{readiness?.debt_health_score || 8.0}/10</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: '80%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <Link
            href="/readiness"
            className="mt-4 block text-center text-xs font-semibold text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 py-2 rounded-lg transition-all"
          >
            View Full 7-Pillar Breakdown →
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/70 border border-amber-500/30 p-5 rounded-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white">Consistency Auditor Alert</h3>
            </div>
            <span className="text-[10px] uppercase font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded">
              Needs Human Review
            </span>
          </div>

          <p className="text-xs text-slate-300 mb-3">
            A variance of <strong className="text-amber-300">2.4%</strong> was detected for <strong className="text-white">Revenue (FY2024)</strong> between two separate filings:
          </p>

          <div className="grid grid-cols-2 gap-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-xs mb-4">
            <div>
              <span className="text-slate-400 block text-[11px]">Source A: Annual Report (Page 74)</span>
              <span className="font-bold text-white text-sm">₹125.00 Cr</span>
              <span className="text-[10px] text-slate-400 block">Audited Statutory Filing</span>
            </div>
            <div className="border-l border-slate-800 pl-3">
              <span className="text-slate-400 block text-[11px]">Source B: Investor Presentation</span>
              <span className="font-bold text-amber-300 text-sm">₹128.00 Cr</span>
              <span className="text-[10px] text-slate-400 block">Includes unbilled retainers</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400">Resolution: Added to Human Review Queue</span>
            <Link
              href="/consistency"
              className="text-xs font-semibold text-amber-400 hover:underline"
            >
              Resolve in Consistency Matrix →
            </Link>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-800 p-5 rounded-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Risk Intelligence Feed</h3>
            </div>
            <span className="text-xs text-slate-400">{risks.length} Triggers Evaluated</span>
          </div>

          <div className="space-y-3">
            {risks.slice(0, 2).map((rk) => (
              <div key={rk.id} className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-slate-200">{rk.title}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    rk.severity === 'HIGH' || rk.severity === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {rk.severity}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1">{rk.evidence}</p>
              </div>
            ))}
          </div>

          <Link
            href="/risks"
            className="mt-3 block text-center text-xs font-semibold text-slate-300 hover:text-white pt-2 border-t border-slate-800"
          >
            Explore All Identified Risks in Risk Center →
          </Link>
        </div>
      </div>
    </div>
  );
}
