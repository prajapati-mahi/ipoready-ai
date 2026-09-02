# -*- coding: utf-8 -*-
import os

fe_root = r"C:\Users\mahii\.gemini\antigravity\scratch\ipoready-ai\frontend"

audit_code = """'use client';

import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, Terminal, Clock, ShieldCheck, 
  Activity, Layers, FileText, ChevronRight
} from 'lucide-react';
import { api, AuditLog } from '@/lib/api';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const list = await api.getAuditLogs(companies[0].id);
        setLogs(list);
        if (list.length > 0) {
          setSelectedLog(list[0]);
        }
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
          <h1 className="text-xl font-bold text-white tracking-tight">Autonomous Audit Trail & Explainability Inspector</h1>
          <p className="text-xs text-slate-400">Complete immutable record of all document ingestion, agent tool executions, and underwriting steps</p>
        </div>

        <button
          onClick={loadLogs}
          className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2 rounded-lg border border-slate-700 transition-all"
        >
          <RefreshCw className="h-3.5 w-3.5 text-emerald-400" />
          <span>Refresh Logs</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="text-sm font-bold text-white">Execution Logs ({logs.length})</h2>
            <span className="text-[11px] text-slate-400">Chronological Audit Stream</span>
          </div>

          <div className="divide-y divide-slate-800">
            {logs.map((l) => {
              const isSelected = selectedLog?.id === l.id;
              return (
                <div
                  key={l.id}
                  onClick={() => setSelectedLog(l)}
                  className={`p-4 cursor-pointer transition-all ${
                    isSelected ? 'bg-slate-800/60 border-l-4 border-emerald-500' : 'hover:bg-slate-800/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white font-mono">{l.action_type}</span>
                    <span className="text-[10px] text-emerald-400 font-mono">{l.latency_ms}ms</span>
                  </div>
                  <p className="text-[11px] text-slate-400 truncate">{l.query_text || 'Automated Pipeline Action'}</p>
                  <span className="text-[10px] text-slate-500 mt-2 block">
                    {new Date(l.created_at).toLocaleString()}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="lg:col-span-7 bg-slate-900/70 border border-slate-800 rounded-xl p-5 flex flex-col h-[600px] overflow-y-auto">
          {selectedLog ? (
            <div className="space-y-4">
              <div className="border-b border-slate-800 pb-3 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white font-mono">{selectedLog.action_type}</h3>
                  <span className="text-[11px] text-slate-400">Latency: {selectedLog.latency_ms}ms</span>
                </div>
                <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                  VERIFIED AUDIT RECORD
                </span>
              </div>

              <div>
                <span className="text-xs font-bold text-slate-300 block mb-2">Steps Executed:</span>
                <div className="space-y-2">
                  {selectedLog.steps_executed && selectedLog.steps_executed.map((step: any, idx: number) => (
                    <div key={idx} className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-xs font-mono flex items-center justify-between">
                      <span className="text-slate-300">{step.step}</span>
                      <span className="text-emerald-400 font-bold">{step.status}</span>
                    </div>
                  ))}
                </div>
              </div>

              {selectedLog.final_output && (
                <div>
                  <span className="text-xs font-bold text-slate-300 block mb-2">Final Output / Response:</span>
                  <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800 text-xs text-slate-300 font-sans leading-relaxed">
                    {selectedLog.final_output}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-20 text-xs text-slate-500">
              Select an execution log to inspect step-by-step telemetry.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
"""

os.makedirs(os.path.join(fe_root, "app", "audit"), exist_ok=True)
with open(os.path.join(fe_root, "app", "audit", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(audit_code.strip() + "\n")
print("Audit Logs page created.")
