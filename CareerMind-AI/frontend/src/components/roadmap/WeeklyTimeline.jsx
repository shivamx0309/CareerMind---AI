import { useState, useMemo } from 'react'
import {
    Clock,
    CheckCircle2,
    ChevronDown,
    ChevronUp,
    ListTodo,
    Sparkles,
} from 'lucide-react'
import ConfirmModal from './ConfirmModal'
import RoadmapPagination from './RoadmapPagination'

const WEEKS_PER_PAGE = 3

export default function WeeklyTimeline({
    milestones = [],
    weeklySchedule = [],
    currentWeek = 1,
    onUpdateMilestoneStatus,
    updatingMilestoneId = null,
}) {
    const [collapsedWeeks, setCollapsedWeeks] = useState({})
    const [confirmMilestone, setConfirmMilestone] = useState(null)
    const [userSelectedPage, setUserSelectedPage] = useState(null)

    const totalWeeks = milestones.length
    const totalPages = Math.max(1, Math.ceil(totalWeeks / WEEKS_PER_PAGE))

    // Calculate initial page based on active week
    const activeWeekPage = useMemo(() => {
        if (!currentWeek || totalWeeks === 0) return 1
        const weekIndex = milestones.findIndex((m) => m.week_number === currentWeek)
        if (weekIndex >= 0) {
            return Math.floor(weekIndex / WEEKS_PER_PAGE) + 1
        }
        return 1
    }, [currentWeek, totalWeeks, milestones])

    // Derive active page safely without setState in effect
    const currentPage = Math.min(totalPages, Math.max(1, userSelectedPage || activeWeekPage))

    const startIndex = (currentPage - 1) * WEEKS_PER_PAGE
    const paginatedMilestones = useMemo(() => {
        return milestones.slice(startIndex, startIndex + WEEKS_PER_PAGE)
    }, [milestones, startIndex])

    const toggleWeek = (weekNum) => {
        setCollapsedWeeks((prev) => ({
            ...prev,
            [weekNum]: !prev[weekNum],
        }))
    }

    const handleConfirmMilestone = async () => {
        if (!confirmMilestone) return
        try {
            await onUpdateMilestoneStatus(confirmMilestone.id, 'completed')
        } finally {
            setConfirmMilestone(null)
        }
    }

    // Merge milestones with weekly_schedule by week_number
    const scheduleByWeek = (weeklySchedule || []).reduce((acc, item) => {
        acc[item.week_number] = item
        return acc
    }, {})

    return (
        <div id="weekly-timeline-section" className="space-y-6">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)]">
                        Weekly Learning Schedule & Milestones
                    </h3>
                    <p className="text-xs text-[var(--text-secondary)]">
                        Paced weekly milestones designed to fit your study hours without cognitive overload
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-[var(--accent)]/30 bg-[var(--accent-soft)] px-3 py-1 text-xs font-bold text-[var(--accent)]">
                        <Sparkles size={13} />
                        Active Week: Week {currentWeek}
                    </span>
                </div>
            </div>

            {milestones.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface-card)] p-8 text-center">
                    <p className="text-sm font-semibold text-[var(--text-secondary)]">
                        No weekly milestones scheduled yet.
                    </p>
                </div>
            ) : (
                <div className="relative pl-6 sm:pl-8 space-y-5 before:absolute before:left-3 before:top-4 before:bottom-4 before:w-0.5 before:bg-[var(--border)]">
                    {paginatedMilestones.map((ms) => {
                        const weekNum = ms.week_number
                        const schedule = scheduleByWeek[weekNum] || {}
                        const isCurrent = weekNum === currentWeek
                        const isCompleted = ms.status === 'completed'
                        const isInProgress = ms.status === 'in_progress' || isCurrent
                        const isCollapsed = Boolean(collapsedWeeks[weekNum])

                        return (
                            <div key={ms.id} className="relative group">
                                {/* Timeline Node Icon */}
                                <div
                                    className={`absolute -left-6 sm:-left-8 top-4 flex h-6 w-6 -translate-x-1/2 items-center justify-center rounded-full border-2 bg-[var(--surface-card)] transition-transform group-hover:scale-110 ${
                                        isCompleted
                                            ? 'border-emerald-500 text-emerald-500'
                                            : isInProgress
                                            ? 'border-[var(--accent)] text-[var(--accent)] animate-pulse'
                                            : 'border-[var(--border)] text-[var(--text-muted)]'
                                    }`}
                                >
                                    {isCompleted ? (
                                        <CheckCircle2 size={14} className="fill-emerald-500 text-white" />
                                    ) : (
                                        <div
                                            className={`h-2 w-2 rounded-full ${
                                                isInProgress ? 'bg-[var(--accent)]' : 'bg-[var(--text-muted)]'
                                            }`}
                                        />
                                    )}
                                </div>

                                {/* Milestone Card */}
                                <div
                                    className={`rounded-2xl border transition-all ${
                                        isCompleted
                                            ? 'border-emerald-500/25 bg-emerald-500/[0.02]'
                                            : isInProgress
                                            ? 'border-[var(--accent)]/40 bg-[var(--accent-soft)]/20 shadow-md shadow-purple-500/5'
                                            : 'border-[var(--border)] bg-[var(--surface-card)]'
                                    }`}
                                >
                                    <div className="p-5">
                                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                                            <div className="flex items-start gap-3">
                                                <span
                                                    className={`rounded-xl px-2.5 py-1 text-xs font-mono font-bold ${
                                                        isCompleted
                                                            ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                                                            : isInProgress
                                                            ? 'bg-[var(--accent)] text-white'
                                                            : 'bg-[var(--surface-hover)] text-[var(--text-secondary)]'
                                                    }`}
                                                >
                                                    Week {weekNum}
                                                </span>
                                                <div>
                                                    <h4 className="text-base font-bold text-[var(--text-primary)]">
                                                        {ms.title}
                                                    </h4>
                                                    <p className="mt-0.5 text-xs text-[var(--text-secondary)] leading-relaxed">
                                                        {ms.description}
                                                    </p>
                                                </div>
                                            </div>

                                            {/* Milestone Status & Action */}
                                            <div className="flex items-center gap-2 self-end sm:self-center">
                                                {/* Status Badge */}
                                                <span
                                                    className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                                                        isCompleted
                                                            ? 'border border-emerald-500/30 bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                                                            : isInProgress
                                                            ? 'border border-amber-500/30 bg-amber-500/15 text-amber-700 dark:text-amber-300'
                                                            : 'border border-[var(--border)] bg-[var(--surface-hover)] text-[var(--text-secondary)]'
                                                    }`}
                                                >
                                                    {ms.status.replace('_', ' ')}
                                                </span>

                                                {/* Mark Completed Button */}
                                                {!isCompleted && (
                                                    <button
                                                        type="button"
                                                        onClick={() => setConfirmMilestone(ms)}
                                                        disabled={updatingMilestoneId === ms.id}
                                                        className="inline-flex items-center gap-1 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/20 transition-all cursor-pointer disabled:opacity-50"
                                                    >
                                                        <CheckCircle2 size={13} />
                                                        Complete Week
                                                    </button>
                                                )}

                                                {/* Collapse Toggle */}
                                                <button
                                                    type="button"
                                                    onClick={() => toggleWeek(weekNum)}
                                                    className="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                                                    aria-label={isCollapsed ? 'Expand week' : 'Collapse week'}
                                                >
                                                    {isCollapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
                                                </button>
                                            </div>
                                        </div>

                                        {/* Collapsible Details */}
                                        {!isCollapsed && (
                                            <div className="mt-4 pt-4 border-t border-[var(--border)] space-y-3">
                                                {/* Skills Covered in this week */}
                                                {schedule.skills && schedule.skills.length > 0 && (
                                                    <div className="flex flex-wrap items-center gap-1.5 text-xs">
                                                        <span className="font-semibold text-[var(--text-muted)]">Core Focus:</span>
                                                        {schedule.skills.map((sk) => (
                                                            <span
                                                                key={sk}
                                                                className="rounded-md border border-[var(--border)] bg-[var(--surface)] px-2 py-0.5 text-xs font-semibold text-[var(--accent)]"
                                                            >
                                                                {sk}
                                                            </span>
                                                        ))}
                                                        {schedule.estimated_hours && (
                                                            <span className="ml-auto inline-flex items-center gap-1 text-[11px] font-medium text-[var(--text-secondary)]">
                                                                <Clock size={12} />
                                                                {schedule.estimated_hours}h scheduled
                                                            </span>
                                                        )}
                                                    </div>
                                                )}

                                                {/* Topics List */}
                                                {schedule.topics && schedule.topics.length > 0 && (
                                                    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3">
                                                        <div className="mb-2 flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                                                            <ListTodo size={13} className="text-[var(--accent)]" />
                                                            Weekly Study Topics ({schedule.topics.length})
                                                        </div>
                                                        <ul className="grid grid-cols-1 gap-1.5 sm:grid-cols-2 text-xs text-[var(--text-primary)]">
                                                            {schedule.topics.map((t, idx) => (
                                                                <li key={idx} className="flex items-center gap-2">
                                                                    <div className="h-1.5 w-1.5 rounded-full bg-[var(--accent)] shrink-0" />
                                                                    <span className="truncate">{t}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

            {/* Pagination for Weekly Timeline */}
            <RoadmapPagination
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={totalWeeks}
                itemsPerPage={WEEKS_PER_PAGE}
                onPageChange={(page) => {
                    setUserSelectedPage(page)
                    const el = document.getElementById('weekly-timeline-section')
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
                }}
                itemName="weeks"
            />

            {/* Confirmation Dialog for Milestone Completion */}
            <ConfirmModal
                isOpen={Boolean(confirmMilestone)}
                title="Mark Weekly Milestone Complete?"
                message={`Are you sure you want to mark "Week ${confirmMilestone?.week_number}: ${confirmMilestone?.title}" as complete?`}
                confirmText="Yes, Complete Week"
                confirmVariant="primary"
                isLoading={updatingMilestoneId === confirmMilestone?.id}
                onConfirm={handleConfirmMilestone}
                onCancel={() => setConfirmMilestone(null)}
            />
        </div>
    )
}
