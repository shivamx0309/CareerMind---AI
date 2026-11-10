import { useState, useMemo } from 'react'
import { Send, Trash2, AlertTriangle } from 'lucide-react'

export default function InterviewAnswerEditor({
  onSubmit,
  isSubmitting = false,
  interviewType = 'technical',
  disabled = false,
}) {
  const [answerText, setAnswerText] = useState('')

  // Word count computation
  const wordCount = useMemo(() => {
    const trimmed = answerText.trim()
    if (!trimmed) return 0
    return trimmed.split(/\s+/).filter(Boolean).length
  }, [answerText])

  const characterCount = answerText.length

  const handleClear = () => {
    if (answerText.trim() && window.confirm('Clear your current answer draft?')) {
      setAnswerText('')
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    // Even empty answers are valid to submit per backend specs (evaluates to 0),
    // but warn user if completely empty to avoid accidental miss-clicks
    if (!answerText.trim()) {
      if (
        !window.confirm(
          'Your response is empty. Submitting a blank answer will award 0 points for this question. Do you wish to continue?'
        )
      ) {
        return
      }
    }

    onSubmit(answerText)
  }

  const placeholderText =
    interviewType === 'behavioral'
      ? 'Structure your response using the STAR method:\n• Situation: What was the context or challenge?\n• Task: What was your specific goal or responsibility?\n• Action: What steps did you take and why?\n• Result: What was the quantifiable outcome or learning?'
      : 'Type your explanation here. Detail mechanisms, architectural trade-offs, edge cases, and concrete examples (e.g. caching strategies, indexing, concurrency, memory complexity)...'

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="relative rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 md:p-5 space-y-3 shadow-xs">
        <div className="flex items-center justify-between text-xs text-[var(--text-secondary)]">
          <label htmlFor="interview-answer-input" className="font-bold uppercase tracking-wider">
            Your Response
          </label>
          <div className="flex items-center gap-3 font-mono text-[11px]">
            <span>{characterCount} chars</span>
            <span>•</span>
            <span
              className={`font-semibold ${
                wordCount < 10
                  ? 'text-amber-600 dark:text-amber-400'
                  : 'text-emerald-600 dark:text-emerald-400'
              }`}
            >
              {wordCount} {wordCount === 1 ? 'word' : 'words'}
            </span>
          </div>
        </div>

        <textarea
          id="interview-answer-input"
          value={answerText}
          onChange={(e) => setAnswerText(e.target.value)}
          disabled={disabled || isSubmitting}
          rows={7}
          placeholder={placeholderText}
          className="w-full resize-y rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] transition-all leading-relaxed"
        />

        {/* Footer Toolbar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-[var(--border)]">
          <div className="text-[11px] text-[var(--text-muted)] self-start sm:self-auto">
            {wordCount < 15 && wordCount > 0 ? (
              <span className="text-amber-600 dark:text-amber-400 flex items-center gap-1">
                <AlertTriangle size={12} /> Target at least 25-35 words for comprehensive depth
              </span>
            ) : (
              <span>Explainable deterministic rubric analysis</span>
            )}
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            {answerText.length > 0 && (
              <button
                type="button"
                onClick={handleClear}
                disabled={disabled || isSubmitting}
                className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-2.5 text-xs text-[var(--text-muted)] hover:text-rose-600 hover:border-rose-500/30 transition-all"
                title="Clear draft"
              >
                <Trash2 size={15} />
              </button>
            )}

            <button
              type="submit"
              disabled={disabled || isSubmitting}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-md hover:from-purple-500 hover:to-indigo-500 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 w-full sm:w-auto"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Evaluating Answer...</span>
                </>
              ) : (
                <>
                  <Send size={14} />
                  <span>Submit Answer</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </form>
  )
}
