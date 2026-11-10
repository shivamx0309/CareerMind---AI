import { AlertTriangle, RotateCcw } from 'lucide-react'

export default function InterviewErrorState({ message, onRetry }) {
  return (
    <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-6 md:p-8 text-center max-w-lg mx-auto space-y-3 shadow-xs">
      <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-600 dark:text-rose-400 mx-auto flex items-center justify-center">
        <AlertTriangle size={24} />
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-bold text-[var(--text-primary)]">
          Interview System Notice
        </h3>
        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
          {message || 'An unexpected error occurred while communicating with the interview service.'}
        </p>
      </div>

      {onRetry && (
        <div className="pt-2">
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
          >
            <RotateCcw size={13} />
            <span>Retry Operation</span>
          </button>
        </div>
      )}
    </div>
  )
}

