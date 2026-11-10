import { useState } from 'react'
import { History, Eye, Trash2, Calendar } from 'lucide-react'

export default function SkillAnalysisHistory({
    reports = [],
    onSelectReport,
    onDeleteReport,
    activeReportId = null,
    isLoading = false,
}) {
    const [deletingId, setDeletingId] = useState(null)
    const [confirmDeleteId, setConfirmDeleteId] = useState(null)

    const handleDeleteClick = async (reportId, e) => {
        e.stopPropagation()
        if (confirmDeleteId !== reportId) {
            setConfirmDeleteId(reportId)
            return
        }

        try {
            setDeletingId(reportId)
            await onDeleteReport(reportId)
            setConfirmDeleteId(null)
        } finally {
            setDeletingId(null)
        }
    }

    if (isLoading) {
        return (
            <div className="glass-card rounded-2xl p-6 space-y-4">
                <div className="h-4 w-40 bg-[var(--surface-hover)] rounded animate-pulse" />
                <div className="space-y-2">
                    {[1, 2, 3].map((i) => (
                        <div
                            key={i}
                            className="h-16 rounded-xl bg-[var(--surface-hover)] animate-pulse"
                        />
                    ))}
                </div>
            </div>
        )
    }

    if (!reports || reports.length === 0) {
        return null // Don't show clutter if user hasn't run any analysis yet
    }

    return (
        <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <History size={18} className="text-[var(--accent)]" />
                    <h3 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                        Analysis History ({reports.length})
                    </h3>
                </div>
                <span className="text-xs text-[var(--text-muted)]">
                    Saved assessments
                </span>
            </div>

            <div className="divide-y divide-[var(--border)]/60 max-h-96 overflow-y-auto pr-1">
                {reports.map((report) => {
                    const isActive = activeReportId === report.id
                    const isConfirming = confirmDeleteId === report.id
                    const isDeleting = deletingId === report.id

                    const formattedDate = report.created_at
                        ? new Date(report.created_at).toLocaleDateString(undefined, {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                          })
                        : 'Recent'

                    return (
                        <div
                            key={report.id}
                            className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 py-3 px-2 rounded-xl transition-all ${
                                isActive
                                    ? 'bg-[var(--accent-soft)] ring-1 ring-[var(--accent)]'
                                    : 'hover:bg-[var(--surface-hover)]'
                            }`}
                        >
                            <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                    <h4 className="text-sm font-bold text-[var(--text-primary)]">
                                        {report.role_title || report.target_role}
                                    </h4>
                                    {isActive && (
                                        <span className="rounded bg-[var(--accent)] px-1.5 py-0.2 text-[10px] font-bold text-white">
                                            Viewing
                                        </span>
                                    )}
                                </div>

                                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[var(--text-muted)]">
                                    <span className="inline-flex items-center gap-1">
                                        <Calendar size={12} />
                                        <span>{formattedDate}</span>
                                    </span>
                                    <span>•</span>
                                    <span className="font-semibold text-emerald-500">
                                        Score: {report.overall_score !== null && report.overall_score !== undefined ? `${report.overall_score}%` : 'N/A'}
                                    </span>
                                    {report.required_coverage_percentage !== null && (
                                        <>
                                            <span>•</span>
                                            <span>Required Cov: {report.required_coverage_percentage}%</span>
                                        </>
                                    )}
                                </div>
                            </div>

                            <div className="flex items-center gap-2 self-end sm:self-center">
                                <button
                                    type="button"
                                    onClick={() => onSelectReport(report.id)}
                                    className="inline-flex items-center gap-1 rounded-lg border border-[var(--border)] bg-[var(--surface-solid)] px-2.5 py-1.5 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--accent)] hover:text-white transition-all cursor-pointer"
                                    title="Open full report"
                                >
                                    <Eye size={13} />
                                    <span>View</span>
                                </button>

                                <button
                                    type="button"
                                    onClick={(e) => handleDeleteClick(report.id, e)}
                                    disabled={isDeleting}
                                    className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                                        isConfirming
                                            ? 'bg-rose-500 text-white animate-pulse'
                                            : 'border border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-muted)] hover:text-rose-500 hover:border-rose-500/40'
                                    }`}
                                    title={isConfirming ? 'Click again to confirm deletion' : 'Delete report'}
                                >
                                    <Trash2 size={13} />
                                    <span>{isConfirming ? 'Confirm Delete' : 'Delete'}</span>
                                </button>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
