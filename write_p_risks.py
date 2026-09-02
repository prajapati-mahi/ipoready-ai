# -*- coding: utf-8 -*-
import os

fe_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\frontend"

risks_code = """'use client';

import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, AlertTriangle, AlertOctagon, Info, CheckCircle2, 
  ArrowRight, Activity, Filter, Calculator
} from 'lucide-react';
import { api, FinancialRisk } from '@/lib/api';

export default function RisksPage() {
  const [risks, setRisks] = useState<FinancialRisk[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRisks();
  }, []);

  const loadRisks = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const list = await api.getRisks(companies[0].id);
        setRisks(list);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filteredRisks = risks.filter(r => 
    selectedSeverity === 'ALL' || r.severity === selectedSeverity
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Financial Risk Intelligence Center</h1>
          <p className="text-xs text-slate-400">Rule-based risk triggers with mathematical evidence cards and underwriting recommendations</p>
        </div>

        <div className="flex items-center space-x-2">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
            <button
              key={s}
              onClick={() => setSelectedSeverity(s)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-all ${
                selectedSeverity === s ? 'bg-slate-800 border-emerald-500 text-emerald-400' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredRisks.map((r) => {
          const isHigh = r.severity === 'HIGH' || r.severity === 'CRITICAL';
          return (
            <div key={r.id} className={`bg-slate-900/80 border rounded-2xl p-5 shadow-xl flex flex-col justify-between ${
              isHigh ? 'border-rose-500/30' : 'border-amber-500/30'
            }`}>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                    isHigh ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>
                    {r.severity} SEVERITY
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">{r.risk_type}</span>
                </div>

                <h3 className="text-sm font-bold text-white">{r.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                  {r.evidence}
                </p>

                {r.formula_used && (
                  <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono bg-slate-950/40 px-3 py-1.5 rounded-lg">
                    <Calculator className="h-3 w-3 text-purple-400" />
                    <span>Formula: {r.formula_used}</span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
                <div className="text-[11px] text-emerald-400 font-semibold">
                  Recommended Action:
                </div>
                <p className="text-xs text-slate-300">
                  {r.recommended_action}
                </p>
                <div className="text-[10px] text-slate-500 mt-2">
                  Citation: {r.source_citation}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
"""

os.makedirs(os.path.join(fe_root, "app", "risks"), exist_ok=True)
with open(os.path.join(fe_root, "app", "risks", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(risks_code.strip() + "\n")
print("Risks Center page created.")
