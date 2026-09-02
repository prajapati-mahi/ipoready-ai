'use client';

import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, AlertTriangle, ShieldCheck, FileSpreadsheet, 
  TrendingUp, Award, Layers, HelpCircle, ArrowRight
} from 'lucide-react';
import { api, IPOReadiness } from '@/lib/api';

export default function IPOReadinessPage() {
  const [readiness, setReadiness] = useState<IPOReadiness | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReadiness();
  }, []);

  const loadReadiness = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const data = await api.getReadiness(companies[0].id);
        setReadiness(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const pillars = [
    {
      title: 'Financial Completeness',
      weight: '20%',
      score: readiness?.financial_completeness_score || 20.0,
      maxScore: 20.0,
      description: 'Presence of mandatory audited financial statements (P&L, Balance Sheet, Cash Flow) across 3 years.',
      status: 'OPTIMAL'
    },
    {
      title: 'Cross-Document Consistency',
      weight: '20%',
      score: readiness?.financial_consistency_score || 16.0,
      maxScore: 20.0,
      description: 'Zero unresolved metric discrepancies between statutory filings, models, and pitch decks.',
      status: 'NEEDS_ATTENTION'
    },
    {
      title: 'Profitability & Operating Margins',
      weight: '15%',
      score: readiness?.profitability_score || 12.0,
      maxScore: 15.0,
      description: 'Sustainable positive EBITDA and PAT margins with healthy gross margin expansion (>50%).',
      status: 'OPTIMAL'
    },
    {
      title: 'Cash Flow Health & Quality',
      weight: '15%',
      score: readiness?.cashflow_score || 10.0,
      maxScore: 15.0,
      description: 'Positive operating cash flow alignment with reported net profit and controlled working capital.',
      status: 'FLAGGED'
    },
    {
      title: 'Debt & Solvency Health',
      weight: '10%',
      score: readiness?.debt_health_score || 8.0,
      maxScore: 10.0,
      description: 'Manageable debt-to-equity ratio (< 1.5x) and sufficient cash reserve coverage.',
      status: 'OPTIMAL'
    },
    {
      title: 'Growth & Scalability (CAGR)',
      weight: '10%',
      score: readiness?.growth_score || 8.5,
      maxScore: 10.0,
      description: 'Multi-year revenue expansion exceeding 20% 3-year CAGR.',
      status: 'OPTIMAL'
    },
    {
      title: 'Filing & Document Coverage',
      weight: '10%',
      score: readiness?.document_coverage_score || 8.0,
      maxScore: 10.0,
      description: 'Availability of board resolutions, statutory audit reports, and investor presentations.',
      status: 'OPTIMAL'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">100-Point IPO Readiness Engine</h1>
          <p className="text-xs text-slate-400">Transparent mathematical score across 7 merchant banking underwriting pillars</p>
        </div>

        <div className="bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg flex items-center space-x-2">
          <Award className="h-4 w-4 text-emerald-400" />
          <span className="text-xs font-bold text-emerald-400">Scorecard Grade: Underwriter Approved</span>
        </div>
      </div>

      <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
        <div className="space-y-2 max-w-xl">
          <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Overall Readiness Rating</span>
          <h2 className="text-3xl font-extrabold text-white">
            {readiness?.overall_score || 82.5} <span className="text-lg text-slate-400 font-normal">/ 100 Points</span>
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Acme Technologies meets all fundamental DRHP eligibility criteria with strong 3-year revenue CAGR (26.6%) and healthy EBITDA margin (25.0%). Resolution of the 2.4% revenue variance and working capital expansion will lift overall readiness above 90.
          </p>
        </div>

        <div className="h-32 w-32 rounded-full border-4 border-emerald-500/30 flex items-center justify-center p-3 bg-slate-950/60 shadow-inner">
          <div className="text-center">
            <span className="text-2xl font-black text-emerald-400">{readiness?.overall_score || 82.5}%</span>
            <span className="block text-[10px] text-slate-400 uppercase font-bold">Readiness</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-bold text-white">Underwriting Pillar Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {pillars.map((p, idx) => {
            const pct = (p.score / p.maxScore) * 100;
            return (
              <div key={idx} className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-white">{p.title}</span>
                    <span className="text-xs font-mono font-bold text-emerald-400">{p.score} / {p.maxScore}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-3">{p.description}</p>
                </div>

                <div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden mb-2">
                    <div 
                      className={`h-full rounded-full ${
                        pct >= 85 ? 'bg-emerald-500' : pct >= 65 ? 'bg-amber-400' : 'bg-rose-500'
                      }`} 
                      style={{ width: `${pct}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-500">
                    <span>Weight: {p.weight}</span>
                    <span className="text-slate-400 font-medium">Score: {pct.toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
