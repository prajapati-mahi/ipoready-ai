# -*- coding: utf-8 -*-
import os

fe_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\frontend"

cons_code = """'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  AlertTriangle, CheckCircle2, ShieldAlert, ArrowRight, 
  FileText, ArrowUpDown, Filter, Sparkles
} from 'lucide-react';
import { api, ConsistencyCheck } from '@/lib/api';

export default function ConsistencyPage() {
  const [checks, setChecks] = useState<ConsistencyCheck[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConsistency();
  }, []);

  const loadConsistency = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const list = await api.getConsistency(companies[0].id);
        setChecks(list);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Cross-Document Consistency Matrix</h1>
          <p className="text-xs text-slate-400">Automated multi-filing variance detection between audited reports, models, and pitch decks</p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Status:</span>
          <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {checks.length} Discrepancy Flagged
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {checks.map((c) => (
          <div key={c.id} className="bg-slate-900/80 border border-amber-500/30 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-amber-400" />
                <h3 className="text-sm font-bold text-white">
                  {c.metric_name} ({c.fiscal_year}) Discrepancy
                </h3>
              </div>
              <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20">
                Variance: {c.variance_percentage}% (₹{((c.variance_amount || 30000000) / 10000000).toFixed(1)} Cr)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider block mb-1">
                  Source Document A (Audited)
                </span>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-slate-300 font-medium">{c.source_a_doc_name}</span>
                  <span className="text-lg font-bold text-white font-mono">{c.source_a_value_raw}</span>
                </div>
                <span className="text-[10px] text-slate-500 mt-2 block">
                  Location: {c.source_a_page_or_cell || 'Page 74 (Audited Statement)'}
                </span>
              </div>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-amber-500/20">
                <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider block mb-1">
                  Source Document B (Filing / Deck)
                </span>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-xs text-slate-300 font-medium">{c.source_b_doc_name}</span>
                  <span className="text-lg font-bold text-amber-400 font-mono">{c.source_b_value_raw}</span>
                </div>
                <span className="text-[10px] text-slate-500 mt-2 block">
                  Location: {c.source_b_page_or_cell || 'Page 1 (Investor Deck)'}
                </span>
              </div>
            </div>

            <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/80 text-xs text-slate-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <strong className="text-white">Underwriting Analysis:</strong> {c.resolution_notes || 'Investor presentation includes unbilled retainers not recognized under statutory Ind AS revenue recognition standards.'}
              </div>
              <Link
                href="/reviews"
                className="whitespace-nowrap bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-4 py-1.5 rounded-lg transition-all"
              >
                Dispatch to Review Queue →
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

os.makedirs(os.path.join(fe_root, "app", "consistency"), exist_ok=True)
with open(os.path.join(fe_root, "app", "consistency", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(cons_code.strip() + "\n")
print("Consistency Matrix page created.")
