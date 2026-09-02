'use client';

import React, { useState, useEffect } from 'react';
import { 
  ClipboardList, CheckCircle2, XCircle, Edit3, 
  AlertTriangle, ShieldCheck, Clock, UserCheck
} from 'lucide-react';
import { api, ReviewItem } from '@/lib/api';

export default function ReviewQueuePage() {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState<number | null>(null);

  useEffect(() => {
    loadReviews();
  }, []);

  const loadReviews = async () => {
    try {
      const companies = await api.getCompanies();
      if (companies.length > 0) {
        const list = await api.getReviews(companies[0].id);
        setItems(list);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (id: number, action: 'APPROVE' | 'REJECT' | 'MODIFY') => {
    setActionInProgress(id);
    try {
      await api.actionReview(id, action, `Actioned by underwriter: ${action}`);
      await loadReviews();
    } catch (e) {
      console.error(e);
    } finally {
      setActionInProgress(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Human Review Queue & Approval Workflow</h1>
          <p className="text-xs text-slate-400">Merchant banker sign-off for flagged cross-document variances and high-uncertainty extractions</p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400">Queue Items:</span>
          <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {items.filter(i => i.review_status === 'PENDING').length} Pending Review
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-amber-400" />
                <h3 className="text-sm font-bold text-white">{item.reason}</h3>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase border ${
                item.review_status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              }`}>
                {item.review_status}
              </span>
            </div>

            <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 text-xs space-y-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                Discrepancy Details & Underwriter Context
              </span>
              <p className="text-slate-300">
                Annual Report lists Revenue as ₹125.0 Cr whereas Investor Presentation lists ₹128.0 Cr (2.4% variance).
              </p>
              <div className="text-[11px] text-slate-400 font-mono">
                Payload: {JSON.stringify(item.original_payload)}
              </div>
            </div>

            {item.review_status === 'PENDING' ? (
              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  onClick={() => handleAction(item.id, 'REJECT')}
                  disabled={actionInProgress === item.id}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold px-4 py-2 rounded-lg border border-slate-700 transition-all"
                >
                  Reject & Exclude
                </button>
                <button
                  onClick={() => handleAction(item.id, 'APPROVE')}
                  disabled={actionInProgress === item.id}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-md shadow-emerald-600/20 transition-all flex items-center space-x-1.5"
                >
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Approve Audited Value (₹125 Cr)</span>
                </button>
              </div>
            ) : (
              <div className="text-right text-xs text-emerald-400 font-semibold pt-2">
                ✓ Resolution Applied & Logged in Audit Trail
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
