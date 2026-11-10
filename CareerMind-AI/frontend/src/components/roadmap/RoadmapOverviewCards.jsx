import {
    Briefcase,
    Calendar,
    Clock,
    Target,
    Compass,
    CheckCircle2,
    Sparkles,
    FileText,
} from 'lucide-react'

export default function RoadmapOverviewCards({
    roadmap,
    progress,
    resumeName = 'Active Resume',
}) {
    if (!roadmap) return null

    const progressPct = progress?.progress_percentage ?? roadmap.progress_percentage ?? 0
    const totalTopics = progress?.total_topics ?? roadmap.total_topics_count ?? 0
    const completedTopics = progress?.completed_topics ?? roadmap.completed_topics_count ?? 0
    const remainingHours = progress?.estimated_hours_remaining ?? 0
    const nextTopic = progress?.next_recommended_topic

    return (
        <div className="space-y-4">
            {/* Top Stat Grid */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {/* 1. Target Role & Resume */}
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-card)] p-5 shadow-sm transition-all hover:border-[var(--accent)]/30">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                            Target Career Role
                        </span>
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
                            <Briefcase size={18} />
                        </div>
                    </div>
                    <div className="mt-2.5">
                        <h4 className="text-base font-bold text-[var(--text-primary)] truncate">
                            {roadmap.role_title || roadmap.target_role}
                        </h4>
                        <div className="mt-1 flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
                            <FileText size={12} className="text-[var(--text-muted)]" />
                            <span className="truncate">{resumeName}</span>
                        </div>
                    </div>
                </div>

                {/* 2. Overall Progress */}
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-card)] p-5 shadow-sm transition-all hover:border-[var(--accent)]/30">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                            Overall Completion
                        </span>
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                            <Target size={18} />
                        </div>
                    </div>
                    <div className="mt-2.5">
                        <div className="flex items-baseline justify-between">
                            <h4 className="text-2xl font-black text-[var(--text-primary)]">
                                {progressPct}%
                            </h4>
                            <span className="text-xs text-[var(--text-secondary)] font-medium">
                                {completedTopics} / {totalTopics} Topics
                            </span>
                        </div>
                        {/* Progress Bar */}
                        <div className="mt-2.5 h-2 w-full overflow-hidden rounded-full bg-[var(--surface-hover)]">
                            <div
                                className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-[var(--accent)] transition-all duration-500"
                                style={{ width: `${Math.min(100, Math.max(0, progressPct))}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* 3. Study Commitment & Duration */}
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-card)] p-5 shadow-sm transition-all hover:border-[var(--accent)]/30">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                            Study Commitment
                        </span>
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
                            <Calendar size={18} />
                        </div>
                    </div>
                    <div className="mt-2.5">
                        <div className="flex items-baseline gap-1.5">
                            <h4 className="text-2xl font-black text-[var(--text-primary)]">
                                {roadmap.weekly_study_hours}
                            </h4>
                            <span className="text-xs text-[var(--text-secondary)] font-medium">
                                hrs / week
                            </span>
                        </div>
                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                            Paced across <span className="font-bold text-[var(--text-primary)]">{roadmap.total_weeks} weeks</span> ({roadmap.total_estimated_hours}h total)
                        </p>
                    </div>
                </div>

                {/* 4. Remaining Hours */}
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-card)] p-5 shadow-sm transition-all hover:border-[var(--accent)]/30">
                    <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                            Remaining Learning
                        </span>
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
                            <Clock size={18} />
                        </div>
                    </div>
                    <div className="mt-2.5">
                        <div className="flex items-baseline gap-1.5">
                            <h4 className="text-2xl font-black text-[var(--text-primary)]">
                                {remainingHours}
                            </h4>
                            <span className="text-xs text-[var(--text-secondary)] font-medium">
                                hrs left
                            </span>
                        </div>
                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                            {totalTopics - completedTopics} topics remaining
                        </p>
                    </div>
                </div>
            </div>

            {/* Next Recommended Topic Callout Banner */}
            {nextTopic && progressPct < 100 && (
                <div className="rounded-2xl border border-[var(--accent)]/30 bg-gradient-to-r from-[var(--accent-soft)] via-[var(--surface-card)] to-[var(--surface-card)] p-4 shadow-sm">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--accent)] text-white shadow-md shadow-purple-600/20">
                                <Compass size={20} />
                            </div>
                            <div>
                                <div className="flex items-center gap-2">
                                    <span className="rounded-full bg-[var(--accent)]/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[var(--accent)]">
                                        Next Recommended Focus
                                    </span>
                                    <span className="text-xs font-medium text-[var(--text-secondary)]">
                                        {nextTopic.skill_name} ({nextTopic.estimated_hours}h)
                                    </span>
                                </div>
                                <h4 className="text-sm font-bold text-[var(--text-primary)]">
                                    {nextTopic.topic_name}
                                </h4>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 self-end sm:self-center">
                            <span className="inline-flex items-center gap-1 text-xs font-semibold text-[var(--accent)]">
                                <Sparkles size={13} />
                                Step into next lesson below
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Completed Congratulatory Banner */}
            {progressPct === 100 && (
                <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-emerald-800 dark:text-emerald-200">
                    <div className="flex items-center gap-3">
                        <CheckCircle2 size={24} className="text-emerald-500" />
                        <div>
                            <h4 className="text-sm font-bold">Curriculum Fully Mastered!</h4>
                            <p className="text-xs text-emerald-700 dark:text-emerald-300">
                                You have completed all scheduled lessons, practical deliverables, and verified milestones for {roadmap.role_title}.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

