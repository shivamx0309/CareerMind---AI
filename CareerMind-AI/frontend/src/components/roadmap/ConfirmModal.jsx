import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, Check, X } from 'lucide-react'

export default function ConfirmModal({
    isOpen,
    title,
    message,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    confirmVariant = 'primary', // 'primary' | 'danger'
    isLoading = false,
    onConfirm,
    onCancel,
}) {
    if (!isOpen) return null

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onCancel}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />

                {/* Modal Window */}
                <motion.div
                    initial={{ scale: 0.95, opacity: 0, y: 10 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 10 }}
                    className="relative w-full max-w-md rounded-2xl border border-purple-200/90 dark:border-purple-800/40 bg-white dark:bg-[#191333] p-6 shadow-2xl"
                >
                    <div className="flex items-start gap-4">
                        <div
                            className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${
                                confirmVariant === 'danger'
                                    ? 'bg-rose-500/15 text-rose-500 border border-rose-500/25'
                                    : 'bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/20'
                            }`}
                        >
                            <AlertTriangle size={22} />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-bold text-[var(--text-primary)]">
                                {title}
                            </h3>
                            <p className="mt-1.5 text-sm leading-relaxed text-[var(--text-secondary)]">
                                {message}
                            </p>
                        </div>
                    </div>

                    <div className="mt-6 flex items-center justify-end gap-3 pt-4 border-t border-[var(--border)]">
                        <button
                            type="button"
                            onClick={onCancel}
                            disabled={isLoading}
                            className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] px-4 py-2 text-sm font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer disabled:opacity-50"
                        >
                            <X size={15} />
                            {cancelText}
                        </button>
                        <button
                            type="button"
                            onClick={onConfirm}
                            disabled={isLoading}
                            className={`inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-sm font-semibold text-white shadow-md transition-all cursor-pointer disabled:opacity-50 ${
                                confirmVariant === 'danger'
                                    ? 'bg-rose-600 hover:bg-rose-500 shadow-rose-600/20'
                                    : 'bg-[var(--primary-purple)] hover:opacity-90 shadow-purple-600/20'
                            }`}
                        >
                            {isLoading ? (
                                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                            ) : (
                                <Check size={15} />
                            )}
                            {confirmText}
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    )
}

