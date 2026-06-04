import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX, CheckCircle2, AlertTriangle, XCircle, MinusCircle } from 'lucide-react';
import type { GuardrailResult } from '../types';

interface Props {
  result: GuardrailResult;
}

type CheckStatus = 'pass' | 'warn' | 'fail' | 'skip';

interface Check {
  name: string;
  desc: string;
  status: CheckStatus;
}

function inferChecks(result: GuardrailResult): Check[] {
  const isLengthError =
    result.error?.includes('empty') ||
    result.error?.includes('short') ||
    result.error?.includes('long');
  const isInjectionError = result.error?.includes('disallowed');

  return [
    {
      name: 'Input Validation',
      desc: 'Length · format · empty-check',
      status: isLengthError ? 'fail' : 'pass',
    },
    {
      name: 'Injection Detection',
      desc: 'Prompt injection · SQL · script patterns',
      status: isLengthError ? 'skip' : isInjectionError ? 'fail' : 'pass',
    },
    {
      name: 'Telecom Relevance',
      desc: 'Domain keyword presence',
      status:
        isLengthError || isInjectionError
          ? 'skip'
          : result.warnings.length > 0
          ? 'warn'
          : 'pass',
    },
  ];
}

const STATUS_ICON: Record<CheckStatus, React.ReactNode> = {
  pass: <CheckCircle2 size={14} className="text-emerald-400 shrink-0" />,
  warn: <AlertTriangle size={14} className="text-yellow-400 shrink-0" />,
  fail: <XCircle size={14} className="text-red-400 shrink-0" />,
  skip: <MinusCircle size={14} className="text-slate-600 shrink-0" />,
};

const STATUS_LABEL: Record<CheckStatus, string> = {
  pass: 'Passed',
  warn: 'Warning',
  fail: 'Failed',
  skip: 'Skipped',
};

const STATUS_TEXT: Record<CheckStatus, string> = {
  pass: 'text-emerald-400',
  warn: 'text-yellow-400',
  fail: 'text-red-400',
  skip: 'text-slate-500',
};

const GuardrailPanel: React.FC<Props> = ({ result }) => {
  const checks = inferChecks(result);
  const hasWarnings = result.warnings.length > 0;
  const isBlocked = !result.valid;

  const overallStatus = isBlocked ? 'blocked' : hasWarnings ? 'warned' : 'passed';

  const bannerStyles = {
    passed: 'bg-emerald-900/20 border-emerald-800/50 text-emerald-400',
    warned:  'bg-yellow-900/20 border-yellow-800/50 text-yellow-400',
    blocked: 'bg-red-900/20 border-red-800/50 text-red-400',
  };

  const bannerIcon = {
    passed:  <ShieldCheck  size={16} className="text-emerald-400 shrink-0" />,
    warned:  <ShieldAlert  size={16} className="text-yellow-400 shrink-0" />,
    blocked: <ShieldX      size={16} className="text-red-400 shrink-0" />,
  };

  const bannerLabel = {
    passed:  'All guardrail checks passed',
    warned:  'Passed with warnings',
    blocked: 'Query blocked by guardrail',
  };

  return (
    <div className="bg-slate-900/50 border border-slate-700 rounded-2xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <ShieldCheck size={15} className="text-slate-400" />
        <h3 className="text-sm font-semibold text-slate-200">Guardrail Validation</h3>
        <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full ml-1">
          3 checks
        </span>
      </div>

      {/* Status banner */}
      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-semibold ${bannerStyles[overallStatus]}`}>
        {bannerIcon[overallStatus]}
        {bannerLabel[overallStatus]}
      </div>

      {/* Individual checks grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {checks.map((chk) => (
          <div
            key={chk.name}
            className="flex items-start gap-2.5 bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2.5"
          >
            <div className="mt-0.5">{STATUS_ICON[chk.status]}</div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-200 leading-tight">{chk.name}</p>
              <p className="text-[11px] text-slate-500 leading-snug mt-0.5">{chk.desc}</p>
              <p className={`text-[11px] font-medium mt-1 ${STATUS_TEXT[chk.status]}`}>
                {STATUS_LABEL[chk.status]}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Warnings */}
      {hasWarnings && (
        <div className="space-y-1.5">
          {result.warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2 bg-yellow-900/10 border border-yellow-800/30 rounded-lg px-3 py-2">
              <AlertTriangle size={12} className="text-yellow-400 shrink-0 mt-0.5" />
              <p className="text-xs text-yellow-300 leading-relaxed">{w}</p>
            </div>
          ))}
        </div>
      )}

      {/* Blocked error */}
      {isBlocked && result.error && (
        <div className="flex items-start gap-2 bg-red-900/10 border border-red-800/30 rounded-lg px-3 py-2">
          <XCircle size={12} className="text-red-400 shrink-0 mt-0.5" />
          <p className="text-xs text-red-300 leading-relaxed">{result.error}</p>
        </div>
      )}
    </div>
  );
};

export default GuardrailPanel;
