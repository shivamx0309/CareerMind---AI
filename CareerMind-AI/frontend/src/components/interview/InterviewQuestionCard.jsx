import { Tag, Code2, AlertCircle } from 'lucide-react'

export default function InterviewQuestionCard({
  question,
  sequenceOrder = 1,
  totalQuestions = 5,
}) {
  if (!question) {
    return (
      <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-6 text-center text-xs text-[var(--text-muted)]">
        No active question available.
      </div>
    )
  }

  const categoryLabel = question.category
    ? question.category.replace(/_/g, ' ').toUpperCase()
    : 'GENERAL'

  return (
    <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-6 md:p-8 space-y-4 shadow-sm">
      {/* Category & Skill Badges */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="inline-flex items-center gap-1.5 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3 py-1 text-xs font-bold text-purple-700 dark:text-purple-300">
            <Tag size={12} />
            <span>{categoryLabel}</span>
          </span>

          {question.relevant_skill && (
            <span className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] px-3 py-1 text-xs font-semibold text-[var(--text-secondary)]">
              <Code2 size={12} className="text-[var(--accent)]" />
              <span>{question.relevant_skill}</span>
            </span>
          )}
        </div>

        <span className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">
          Question {sequenceOrder} of {totalQuestions}
        </span>
      </div>

      {/* Prominent Question Text */}
      <div className="space-y-2">
        <h3 className="text-lg md:text-xl font-bold text-[var(--text-primary)] leading-snug">
          {question.question_text}
        </h3>
      </div>

      {/* Disclaimer reminder */}
      <div className="pt-2 border-t border-[var(--border)] flex items-center gap-2 text-[11px] text-[var(--text-muted)]">
        <AlertCircle size={13} className="shrink-0 text-purple-500" />
        <span>
          Take your time to articulate trade-offs, architecture, or the STAR structure.
        </span>
      </div>
    </div>
  )
}
