import { useState } from 'react'
import {
    CheckCircle2,
    Circle,
    PlayCircle,
    Clock,
    ExternalLink,
    BookOpen,
    Sparkles,
} from 'lucide-react'

export default function TopicCard({
    topic,
    onStatusChange,
    isUpdating = false,
}) {
    const [localStatus, setLocalStatus] = useState(topic.status || 'not_started')

    const statusOptions = [
        { key: 'not_started', label: 'Not Started', icon: Circle, color: 'text-slate-400 hover:text-slate-300' },
        { key: 'in_progress', label: 'In Progress', icon: PlayCircle, color: 'text-amber-500 hover:text-amber-400' },
        { key: 'completed', label: 'Completed', icon: CheckCircle2, color: 'text-emerald-500 hover:text-emerald-400' },
    ]

    const handleSelectStatus = async (newStatus) => {
        if (newStatus === localStatus || isUpdating) return
        setLocalStatus(newStatus)
        try {
            await onStatusChange(topic.id, newStatus)
        } catch (err) {
            console.error('Failed to update topic status:', err)
            setLocalStatus(topic.status) // revert on failure
        }
    }

    const isCompleted = (topic.status || localStatus) === 'completed'
    const isInProgress = (topic.status || localStatus) === 'in_progress'

    return (
        <div
            className={`group rounded-xl border p-4 transition-all ${
                isCompleted
                    ? 'border-emerald-500/20 bg-emerald-500/[0.03] dark:bg-emerald-500/[0.04]'
                    : isInProgress
                    ? 'border-amber-500/25 bg-amber-500/[0.03] dark:bg-amber-500/[0.04]'
                    : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--accent)]/30'
            }`}
        >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                {/* Topic Info */}
                <div className="flex-1">
                    <div className="flex items-start gap-2.5">
                        <span
                            className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg text-xs font-mono font-bold ${
                                isCompleted
                                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
                                    : isInProgress
                                    ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
                                    : 'bg-[var(--surface-hover)] text-[var(--text-secondary)]'
                            }`}
                        >
                            {topic.sequence_order}
                        </span>
                        <div>
                            <h5
                                className={`text-sm font-semibold transition-colors ${
                                    isCompleted
                                        ? 'line-through text-[var(--text-secondary)] opacity-85'
                                        : 'text-[var(--text-primary)]'
                                }`}
                            >
                                {topic.topic_name}
                            </h5>
                            <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-[var(--text-secondary)]">
                                <span className="inline-flex items-center gap-1">
                                    <Clock size={12} className="text-[var(--text-muted)]" />
                                    {topic.estimated_hours}h estimated
                                </span>
                                {topic.completed_at && (
                                    <>
                                        <span>•</span>
                                        <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                                            Finished on {new Date(topic.completed_at).toLocaleDateString()}
                                        </span>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Status Toggle / Select */}
                <div className="flex items-center gap-1 self-start rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] p-1">
                    {statusOptions.map((opt) => {
                        const Icon = opt.icon
                        const active = (topic.status || localStatus) === opt.key
                        return (
                            <button
                                key={opt.key}
                                type="button"
                                disabled={isUpdating}
                                onClick={() => handleSelectStatus(opt.key)}
                                title={`Mark as ${opt.label}`}
                                className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium transition-all cursor-pointer disabled:opacity-50 ${
                                    active
                                        ? opt.key === 'completed'
                                            ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 shadow-sm font-bold'
                                            : opt.key === 'in_progress'
                                            ? 'bg-amber-500/15 text-amber-700 dark:text-amber-300 shadow-sm font-bold'
                                            : 'bg-[var(--surface)] text-[var(--text-primary)] shadow-sm font-bold'
                                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                                }`}
                            >
                                <Icon size={13} className={opt.color} />
                                <span className="hidden sm:inline">{opt.label}</span>
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Verified Learning Resources */}
            {topic.resources && topic.resources.length > 0 ? (
                <div className="mt-3.5 pt-3 border-t border-[var(--border)]">
                    <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                        <BookOpen size={12} className="text-[var(--accent)]" />
                        Verified Free Resources ({topic.resources.length})
                    </div>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                        {topic.resources.map((res) => (
                            <a
                                key={res.id || res.url}
                                href={res.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="group/link flex items-center justify-between gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface-hover)] px-3 py-2 text-xs transition-all hover:border-[var(--accent)] hover:bg-[var(--accent-soft)]"
                            >
                                <div className="min-w-0 flex-1">
                                    <div className="truncate font-semibold text-[var(--text-primary)] group-hover/link:text-[var(--accent)]">
                                        {res.title}
                                    </div>
                                    <div className="mt-0.5 flex items-center gap-2 text-[10px] text-[var(--text-secondary)]">
                                        <span className="font-medium text-[var(--text-primary)]">
                                            {res.provider}
                                        </span>
                                        <span>•</span>
                                        <span className="capitalize">{res.resource_type}</span>
                                        <span>•</span>
                                        <span className="capitalize">{res.difficulty}</span>
                                    </div>
                                </div>
                                <div className="flex shrink-0 items-center gap-1.5">
                                    <span className="rounded-full bg-emerald-500/10 px-1.5 py-0.5 text-[9px] font-bold text-emerald-600 dark:text-emerald-400">
                                        Free
                                    </span>
                                    <ExternalLink
                                        size={13}
                                        className="text-[var(--text-muted)] transition-transform group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 group-hover/link:text-[var(--accent)]"
                                    />
                                </div>
                            </a>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="mt-2.5 flex items-center gap-1.5 text-xs text-[var(--text-secondary)] italic">
                    <Sparkles size={12} className="text-[var(--accent)]" />
                    Hands-on practical exploration recommended for this topic.
                </div>
            )}
        </div>
    )
}
