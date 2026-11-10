import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    History,
    Calendar,
    Trash2,
    ArrowRight,
    X,
    Sparkles,
    Briefcase,
} from 'lucide-react'
import ConfirmModal from './ConfirmModal'

export default function RoadmapHistoryModal({
    isOpen,
    onClose,
    roadmaps = [],
    activeRoadmapId,
    onSelectRoadmap,
    onDeleteRoadmap,
    onOpenGenerator,
}) {
    const [confirmDeleteId, setConfirmDeleteId] = useState(null)
    const [isDeleting, setIsDeleting] = useState(false)

    if (!isOpen) return null

    const roadmapToDelete = roadmaps.find((r) => r.id === confirmDeleteId)

    const handleDelete = async () => {
        if (!confirmDeleteId) return
        setIsDeleting(true)
        try {
            await onDeleteRoadmap(confirmDeleteId)
        } finally {
            setIsDeleting(false)
            setConfirmDeleteId(null)
        }
    }

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />

                {/* Modal Window */}
                <motion.div
                    initial={{ scale: 0.95, opacity: 0, y: 10 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 10 }}
                    className="relative w-full max-w-xl rounded-3xl border border-[var(--border)] bg-[var(--surface-card)] p-6 sm:p-7 shadow-2xl overflow-hidden max-h-[85vh] flex flex-col"
                >
                    {/* Header */}
                    <div className="flex items-start justify-between pb-4 border-b border-[var(--border)]">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/20">
                                <History size={18} />
                            </div>
                            <div>
                                <h3 className="text-base font-bold text-[var(--text-primary)]">
                                    Roadmap History
                                </h3>
                                <p className="text-xs text-[var(--text-secondary)]">
                                    Switch between your active and completed learning paths
                                </p>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={onClose}
                            className="rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                        >
                            <X size={15} />
                        </button>
                    </div>

                    {/* Roadmaps List */}
                    <div className="mt-4 flex-1 overflow-y-auto space-y-3 pr-1">
                        {roadmaps.length === 0 ? (
                            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-8 text-center">
                                <p className="text-xs font-semibold text-[var(--text-secondary)]">
                                    No historical roadmaps found.
                                </p>
                            </div>
                        ) : (
                            roadmaps.map((rm) => {
                                const isActive = rm.id === activeRoadmapId
                                const isCompleted = rm.status === 'completed'

                                return (
                                    <div
                                        key={rm.id}
                                        className={`rounded-2xl border p-4 transition-all ${
                                            isActive
                                                ? 'border-[var(--accent)] bg-[var(--accent-soft)]/20 shadow-sm'
                                                : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--border-hover)]'
                                        }`}
                                    >
                                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                                            <div className="min-w-0 flex-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs font-bold text-[var(--text-primary)] truncate">
                                                        {rm.title || rm.role_title}
                                                    </span>
                                                    {isActive && (
                                                        <span className="rounded-full bg-[var(--accent)]/15 px-2 py-0.5 text-[9px] font-bold text-[var(--accent)]">
                                                            Active Now
                                                        </span>
                                                    )}
                                                    <span
                                                        className={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${
                                                            isCompleted
                                                                ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                                                                : 'bg-amber-500/15 text-amber-700 dark:text-amber-300'
                                                        }`}
                                                    >
                                                        {rm.status}
                                                    </span>
                                                </div>

                                                <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-[var(--text-secondary)]">
                                                    <span className="inline-flex items-center gap-1">
                                                        <Briefcase size={11} className="text-[var(--text-muted)]" />
                                                        {rm.role_title}
                                                    </span>
                                                    <span>•</span>
                                                    <span className="inline-flex items-center gap-1">
                                                        <Calendar size={11} className="text-[var(--text-muted)]" />
                                                        {rm.total_weeks} weeks ({rm.weekly_study_hours}h/wk)
                                                    </span>
                                                    <span>•</span>
                                                    <span>Created {new Date(rm.created_at).toLocaleDateString()}</span>
                                                </div>

                                                {/* Progress Mini Bar */}
                                                <div className="mt-2.5 flex items-center gap-2">
                                                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-[var(--surface-hover)]">
                                                        <div
                                                            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-[var(--accent)]"
                                                            style={{ width: `${Math.min(100, Math.max(0, rm.progress_percentage || 0))}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-[10px] font-mono font-bold text-[var(--text-primary)]">
                                                        {Math.round(rm.progress_percentage || 0)}%
                                                    </span>
                                                </div>
                                            </div>

                                            {/* Action Buttons */}
                                            <div className="flex items-center gap-2 self-end sm:self-center">
                                                {!isActive && (
                                                    <button
                                                        type="button"
                                                        onClick={() => {
                                                            onSelectRoadmap(rm.id)
                                                            onClose()
                                                        }}
                                                        className="inline-flex items-center gap-1 rounded-xl bg-[var(--surface-hover)] px-3 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--accent-soft)] hover:text-[var(--accent)] transition-all cursor-pointer"
                                                    >
                                                        Switch To
                                                        <ArrowRight size={12} />
                                                    </button>
                                                )}
                                                <button
                                                    type="button"
                                                    onClick={() => setConfirmDeleteId(rm.id)}
                                                    className="flex h-7 w-7 items-center justify-center rounded-lg text-rose-500 hover:bg-rose-500/10 transition-all cursor-pointer"
                                                    title="Delete this roadmap"
                                                >
                                                    <Trash2 size={13} />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })
                        )}
                    </div>

                    {/* Footer Actions */}
                    <div className="mt-4 flex items-center justify-between pt-3 border-t border-[var(--border)]">
                        <button
                            type="button"
                            onClick={() => {
                                onClose()
                                if (onOpenGenerator) onOpenGenerator()
                            }}
                            className="inline-flex items-center gap-1.5 text-xs font-bold text-[var(--accent)] hover:opacity-80 transition-all cursor-pointer"
                        >
                            <Sparkles size={14} />
                            Generate New Roadmap
                        </button>
                        <button
                            type="button"
                            onClick={onClose}
                            className="rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] px-4 py-1.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] cursor-pointer"
                        >
                            Close
                        </button>
                    </div>
                </motion.div>
            </div>

            {/* Confirmation Modal for Delete */}
            <ConfirmModal
                isOpen={Boolean(confirmDeleteId)}
                title="Delete Learning Roadmap?"
                message={`Are you sure you want to permanently delete "${roadmapToDelete?.title || roadmapToDelete?.role_title}"? All scheduled milestones, lesson progress, and completion states will be removed.`}
                confirmText="Delete Roadmap"
                confirmVariant="danger"
                isLoading={isDeleting}
                onConfirm={handleDelete}
                onCancel={() => setConfirmDeleteId(null)}
            />
        </AnimatePresence>
    )
}
