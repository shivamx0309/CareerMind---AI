import { AlertTriangle, X } from 'lucide-react'

export default function InterviewConfirmModal({
  isOpen,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  onConfirm,
  onCancel,
}) {
  if (!isOpen) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150"
    >
      <div className="relative w-full max-w-md rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] shadow-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                isDestructive
                  ? 'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                  : 'bg-purple-500/15 text-purple-600 dark:text-purple-400'
              }`}
            >
              <AlertTriangle size={18} />
            </div>
            <h3 className="text-base font-bold text-[var(--text-primary)]">{title}</h3>
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="rounded-xl p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>

        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{message}</p>

        <div className="flex items-center justify-end gap-2.5 pt-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] transition-all"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`rounded-xl px-5 py-2 text-xs font-bold text-white shadow-sm transition-all ${
              isDestructive
                ? 'bg-rose-600 hover:bg-rose-500'
                : 'bg-purple-600 hover:bg-purple-500'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

