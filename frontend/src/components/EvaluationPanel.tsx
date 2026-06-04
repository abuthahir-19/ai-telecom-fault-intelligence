import React, { useState } from 'react';
import { BarChart2, AlertCircle, CheckCircle2, Loader2, ChevronDown, Info } from 'lucide-react';
import type { EvaluationResult } from '../types';

interface Props {
  result: EvaluationResult | null;
  loading: boolean;
}

// ── Static descriptions for each metric (explain what is measured) ─────────
const METRIC_DOCS: Record<string, { what: string; high: string; low: string }> = {
  Faithfulness: {
    what:
      'Measures whether every claim made in the generated root-cause analysis and ' +
      'recommendations is directly supported by the retrieved incident evidence. ' +
      'It checks that the model is not hallucinating or introducing information that ' +
      'cannot be traced back to the retrieved context.',
    high: 'All claims are grounded in retrieved incidents. The analysis is fully trustworthy.',
    low:  'Some claims are unsupported. Review the analysis carefully for hallucinations.',
  },
  'Answer Relevancy': {
    what:
      'Measures how directly and completely the generated analysis addresses the original ' +
      'fault query. It evaluates whether the root-cause identification and recommendations ' +
      'are on-topic and cover all key aspects the user asked about.',
    high: 'The analysis fully addresses the query with no off-topic content.',
    low:  'Parts of the query may be unanswered or the response drifts off-topic.',
  },
  'Context Precision': {
    what:
      'Measures the fraction of retrieved incidents that are genuinely relevant to the ' +
      'fault query. A high score indicates that the hybrid RAG retrieval (ChromaDB + BM25 ' +
      'RRF fusion) is returning highly targeted incidents rather than loosely related noise.',
    high: 'Most retrieved incidents are relevant — the RAG pipeline is well-calibrated.',
    low:  'Many retrieved incidents are irrelevant — consider refining the query or filters.',
  },
};

// ── Single expandable metric card ─────────────────────────────────────────────
const MetricCard: React.FC<{
  label:       string;
  score:       number;
  assessment:  string;
  issues?:     string[];
  missing?:    string[];
}> = ({ label, score, assessment, issues = [], missing = [] }) => {
  const [open, setOpen] = useState(false);

  const pct       = Math.round(score * 100);
  const barColor  = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-yellow-500' : 'bg-red-500';
  const textColor = pct >= 70 ? 'text-emerald-400' : pct >= 40 ? 'text-yellow-400' : 'text-red-400';
  const badgeBg   = pct >= 70
    ? 'bg-emerald-900/30 border-emerald-700/40'
    : pct >= 40
    ? 'bg-yellow-900/30 border-yellow-700/40'
    : 'bg-red-900/30 border-red-700/40';

  const doc    = METRIC_DOCS[label];
  const hasExtra = issues.length > 0 || missing.length > 0 || !!doc;

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">

      {/* ── Always-visible section ── */}
      <div className="p-4 space-y-3">

        {/* Label + badge */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-200 tracking-wide uppercase">
            {label}
          </span>
          <span className={`text-sm font-bold tabular-nums px-2.5 py-0.5 rounded-full border ${badgeBg} ${textColor}`}>
            {pct}%
          </span>
        </div>

        {/* Score bar */}
        <div className="h-2 rounded-full bg-slate-700 overflow-hidden">
          <div
            className={`h-full rounded-full ${barColor} transition-all duration-700`}
            style={{ width: `${pct}%` }}
          />
        </div>

        {/* Full assessment — no truncation */}
        {assessment && (
          <p className="text-xs text-slate-400 leading-relaxed">{assessment}</p>
        )}
      </div>

      {/* ── Expand / collapse toggle ── */}
      {hasExtra && (
        <button
          onClick={() => setOpen(v => !v)}
          className="w-full flex items-center justify-between px-4 py-2.5 border-t border-slate-700/60
                     text-[11px] font-semibold text-slate-500 hover:text-slate-300
                     hover:bg-slate-700/30 transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <Info size={11} />
            {open ? 'Hide details' : 'View full details'}
          </span>
          <ChevronDown
            size={13}
            className={`transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
          />
        </button>
      )}

      {/* ── Expanded detail panel ── */}
      {open && hasExtra && (
        <div className="px-4 pb-4 pt-3 border-t border-slate-700/40 space-y-4 bg-slate-900/30">

          {/* What this metric measures */}
          {doc && (
            <div className="space-y-1.5">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                What this measures
              </p>
              <p className="text-xs text-slate-300 leading-relaxed">{doc.what}</p>
            </div>
          )}

          {/* Score interpretation */}
          {doc && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div className="bg-emerald-900/20 border border-emerald-800/30 rounded-lg px-3 py-2">
                <p className="text-[10px] font-bold text-emerald-500 uppercase tracking-wide mb-0.5">
                  High score means
                </p>
                <p className="text-[11px] text-emerald-300 leading-snug">{doc.high}</p>
              </div>
              <div className="bg-red-900/20 border border-red-800/30 rounded-lg px-3 py-2">
                <p className="text-[10px] font-bold text-red-500 uppercase tracking-wide mb-0.5">
                  Low score means
                </p>
                <p className="text-[11px] text-red-300 leading-snug">{doc.low}</p>
              </div>
            </div>
          )}

          {/* Issues */}
          {issues.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                Faithfulness issues detected
              </p>
              {issues.map((iss, i) => (
                <div key={i}
                  className="flex items-start gap-2 bg-red-900/10 border border-red-800/25 rounded-lg px-3 py-1.5">
                  <AlertCircle size={11} className="text-red-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-red-300 leading-relaxed">{iss}</p>
                </div>
              ))}
            </div>
          )}

          {/* Missing aspects */}
          {missing.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                Missing aspects in the answer
              </p>
              {missing.map((asp, i) => (
                <div key={i}
                  className="flex items-start gap-2 bg-yellow-900/10 border border-yellow-800/25 rounded-lg px-3 py-1.5">
                  <AlertCircle size={11} className="text-yellow-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-yellow-300 leading-relaxed">{asp}</p>
                </div>
              ))}
            </div>
          )}

          {/* Clean bill */}
          {issues.length === 0 && missing.length === 0 && (
            <div className="flex items-center gap-2 text-xs text-emerald-400
                            bg-emerald-900/10 border border-emerald-800/25 rounded-lg px-3 py-2">
              <CheckCircle2 size={13} />
              No issues or missing aspects detected for this metric.
            </div>
          )}
        </div>
      )}
    </div>
  );
};


// ── Main panel ────────────────────────────────────────────────────────────────
const EvaluationPanel: React.FC<Props> = ({ result, loading }) => {
  if (loading) {
    return (
      <div className="bg-slate-900/50 border border-slate-700 rounded-2xl p-5 flex items-center gap-3">
        <Loader2 size={16} className="text-violet-400 animate-spin shrink-0" />
        <div>
          <p className="text-sm text-slate-300 font-medium">Running evaluation metrics…</p>
          <p className="text-xs text-slate-500 mt-0.5">
            Faithfulness · Answer Relevancy · Context Precision
          </p>
        </div>
      </div>
    );
  }
  if (!result) return null;

  const overallPct   = Math.round(result.overall_score * 100);
  const overallColor = overallPct >= 70
    ? 'text-emerald-400 border-emerald-700/50 bg-emerald-900/20'
    : overallPct >= 40
    ? 'text-yellow-400 border-yellow-700/50 bg-yellow-900/20'
    : 'text-red-400 border-red-700/50 bg-red-900/20';

  return (
    <div className="bg-slate-900/50 border border-slate-700 rounded-2xl p-5 space-y-5">

      {/* ── Panel header ── */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <BarChart2 size={15} className="text-violet-400" />
          <h3 className="text-sm font-semibold text-slate-200">RAG Evaluation</h3>
          <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
            DeepEval · LLM-as-Judge
          </span>
        </div>
        <span className={`text-sm font-bold px-3 py-1 rounded-full border ${overallColor}`}>
          Overall {overallPct}%
        </span>
      </div>

      {/* ── Metric cards (stacked for detail, use View details to expand) ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          label="Faithfulness"
          score={result.faithfulness.faithfulness_score}
          assessment={result.faithfulness.grounding_assessment}
          issues={result.faithfulness.issues}
        />
        <MetricCard
          label="Answer Relevancy"
          score={result.answer_relevance.relevance_score}
          assessment={result.answer_relevance.relevance_assessment}
          missing={result.answer_relevance.missing_aspects}
        />
        <MetricCard
          label="Context Precision"
          score={result.context_precision.context_precision_score}
          assessment={result.context_precision.precision_assessment}
        />
      </div>

      {/* ── Summary bar ── */}
      {result.evaluation_summary && (
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-3">
          <p className="text-xs leading-relaxed text-slate-300">
            <span className="font-semibold text-slate-200">Summary: </span>
            {result.evaluation_summary}
          </p>
        </div>
      )}

      {/* ── Weights note ── */}
      <p className="text-[11px] text-slate-600 text-right">
        Weighted: Faithfulness ×0.40 · Answer Relevancy ×0.35 · Context Precision ×0.25
      </p>
    </div>
  );
};

export default EvaluationPanel;
