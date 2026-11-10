import { Target, BookOpen, FileCheck2, AlignLeft } from 'lucide-react'

export default function EvaluationScoreBreakdown({
  overallScore = 0,
  relevanceScore = 0,
  conceptCoverageScore = 0,
  completenessScore = 0,
  structureScore = 0,
}) {
  const getScoreColor = (score) => {
    if (score >= 75) return 'text-emerald-600 dark:text-emerald-400'
    if (score >= 50) return 'text-amber-600 dark:text-amber-400'
    return 'text-rose-600 dark:text-rose-400'
  }

  const getScoreBg = (score) => {
    if (score >= 75) return 'bg-emerald-500'
    if (score >= 50) return 'bg-amber-500'
    return 'bg-rose-500'
  }

  const metrics = [
    {
      label: 'Concept Coverage',
      weight: '40% weight',
      score: conceptCoverageScore,
      icon: BookOpen,
      desc: 'Technical terms, algorithms & core domain concepts',
    },
    {
      label: 'Relevance',
      weight: '25% weight',
      score: relevanceScore,
      icon: Target,
      desc: 'Topical alignment with question domain',
    },
    {
      label: 'Completeness',
      weight: '20% weight',
      score: completenessScore,
      icon: FileCheck2,
      desc: 'Sufficient depth without unnecessary fluff',
    },
    {
      label: 'Structure & Clarity',
      weight: '15% weight',
      score: structureScore,
      icon: AlignLeft,
      desc: 'Logical flow, transitions & STAR methodology',
    },
  ]

  return (
    <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 md:p-6 space-y-6 shadow-xs">
      {/* Top Banner: Composite Score */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[var(--border)]">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
            Answer Evaluation
          </span>
          <h4 className="text-base font-bold text-[var(--text-primary)]">
            Deterministic Rubric Performance
          </h4>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className={`text-3xl font-black ${getScoreColor(overallScore)}`}>
              {Math.round(overallScore)}
              <span className="text-sm font-semibold text-[var(--text-muted)]">/100</span>
            </div>
            <div className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
              Overall Score
            </div>
          </div>
        </div>
      </div>

      {/* 4 Rubric Bars */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {metrics.map((m) => (
          <div
            key={m.label}
            className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-3.5 space-y-2"
          >
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 font-bold text-[var(--text-primary)]">
                <m.icon size={14} className="text-[var(--accent)]" />
                <span>{m.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-[var(--text-muted)] font-mono">{m.weight}</span>
                <span className={`font-mono font-bold ${getScoreColor(m.score)}`}>
                  {Math.round(m.score)}%
                </span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="h-1.5 w-full rounded-full bg-[var(--surface-hover)] overflow-hidden">
              <div
                className={`h-full ${getScoreBg(m.score)} transition-all duration-500`}
                style={{ width: `${Math.min(100, Math.max(0, m.score))}%` }}
              />
            </div>

            <div className="text-[10px] text-[var(--text-muted)] line-clamp-1">{m.desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
