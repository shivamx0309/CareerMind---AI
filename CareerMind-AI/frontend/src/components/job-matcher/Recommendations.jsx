import { useState } from 'react'
import {
    Lightbulb,
    Flame,
    Clock,
    CheckSquare2,
    Compass,
    ArrowRight,
    ShieldCheck,
} from 'lucide-react'

function formatPriorityBadge(priority) {
    switch (priority) {
        case 'HIGH':
            return {
                label: 'High Priority',
                badge: 'border-rose-500/30 bg-rose-500/15 text-rose-400',
                border: 'border-l-rose-500',
                icon: Flame,
            }
        case 'MEDIUM':
            return {
                label: 'Medium Priority',
                badge: 'border-amber-500/30 bg-amber-500/15 text-amber-400',
                border: 'border-l-amber-500',
                icon: Compass,
            }
        case 'LOW':
        default:
            return {
                label: 'Low Priority',
                badge: 'border-indigo-500/30 bg-indigo-500/15 text-indigo-400',
                border: 'border-l-indigo-500',
                icon: Clock,
            }
    }
}

function formatCategoryLabel(category) {
    switch (category) {
        case 'required_skill':
            return 'Core Technical Skill'
        case 'preferred_skill':
            return 'Preferred Technology'
        case 'related_skill':
            return 'Skill Gap Bridge'
        case 'experience':
            return 'Experience & Tenure'
        case 'education':
            return 'Education Credential'
        default:
            return category.replace('_', ' ')
    }
}

export default function Recommendations({ recommendations = [] }) {
    const [selectedPriority, setSelectedPriority] = useState('ALL') // 'ALL' | 'HIGH' | 'MEDIUM' | 'LOW'

    if (!recommendations || recommendations.length === 0) {
        return (
            <div className="glass-card rounded-2xl p-6 text-center">
                <span className="text-xs font-semibold text-emerald-400">
                    No Actionable Gaps Detected — Your profile strongly aligns with the target job requirements!
                </span>
            </div>
        )
    }

    const filtered = recommendations.filter((rec) => {
        if (selectedPriority === 'ALL') return true
        return rec.priority === selectedPriority
    })

    const highCount = recommendations.filter((r) => r.priority === 'HIGH').length
    const medCount = recommendations.filter((r) => r.priority === 'MEDIUM').length
    const lowCount = recommendations.filter((r) => r.priority === 'LOW').length

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border)] pb-4">
                <div>
                    <div className="flex items-center gap-2">
                        <Lightbulb size={18} className="text-[var(--accent)]" />
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Prioritized Improvement Roadmap
                        </h3>
                        <span className="rounded-full bg-[var(--accent-soft)] px-2.5 py-0.5 text-xs font-bold text-[var(--accent)]">
                            {recommendations.length}
                        </span>
                    </div>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Defensible, evidence-first learning milestones to systematically bridge verified skill and tenure gaps.
                    </p>
                </div>

                {/* Priority Filter Pills */}
                <div className="flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-1">
                    <button
                        type="button"
                        onClick={() => setSelectedPriority('ALL')}
                        className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                            selectedPriority === 'ALL'
                                ? 'bg-[var(--accent)] text-white shadow-sm'
                                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                        }`}
                    >
                        All ({recommendations.length})
                    </button>
                    {highCount > 0 && (
                        <button
                            type="button"
                            onClick={() => setSelectedPriority('HIGH')}
                            className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                                selectedPriority === 'HIGH'
                                    ? 'bg-rose-500 text-white shadow-sm'
                                    : 'text-rose-400 hover:text-rose-300'
                            }`}
                        >
                            High ({highCount})
                        </button>
                    )}
                    {medCount > 0 && (
                        <button
                            type="button"
                            onClick={() => setSelectedPriority('MEDIUM')}
                            className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                                selectedPriority === 'MEDIUM'
                                    ? 'bg-amber-500 text-white shadow-sm'
                                    : 'text-amber-400 hover:text-amber-300'
                            }`}
                        >
                            Medium ({medCount})
                        </button>
                    )}
                    {lowCount > 0 && (
                        <button
                            type="button"
                            onClick={() => setSelectedPriority('LOW')}
                            className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                                selectedPriority === 'LOW'
                                    ? 'bg-indigo-500 text-white shadow-sm'
                                    : 'text-indigo-400 hover:text-indigo-300'
                            }`}
                        >
                            Low ({lowCount})
                        </button>
                    )}
                </div>
            </div>

            {/* List of Recommendations */}
            <div className="space-y-4">
                {filtered.map((rec) => {
                    const priorityConfig = formatPriorityBadge(rec.priority)
                    const PriorityIcon = priorityConfig.icon

                    return (
                        <div
                            key={rec.recommendation_id}
                            className={`rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/70 p-5 pl-6 border-l-4 ${priorityConfig.border} transition-all hover:bg-[var(--surface-hover)] space-y-3.5`}
                        >
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                                <div className="space-y-1">
                                    <div className="flex flex-wrap items-center gap-2">
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--accent)]">
                                            {formatCategoryLabel(rec.category)}
                                        </span>
                                        {rec.estimated_effort && (
                                            <span className="text-[11px] text-[var(--text-muted)] flex items-center gap-1">
                                                <span>•</span>
                                                <Clock size={11} />
                                                <span>Est. Effort: {rec.estimated_effort}</span>
                                            </span>
                                        )}
                                    </div>
                                    <h4 className="text-base font-bold text-[var(--text-primary)]">
                                        {rec.title}
                                    </h4>
                                </div>

                                <span
                                    className={`inline-flex items-center gap-1.5 self-start rounded-full border px-2.5 py-0.5 text-[11px] font-bold shrink-0 ${priorityConfig.badge}`}
                                >
                                    <PriorityIcon size={12} />
                                    <span>{priorityConfig.label}</span>
                                </span>
                            </div>

                            {/* Description & Direct Reason */}
                            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                                {rec.description}
                            </p>

                            {/* Candidate Evidence Bridge (if present) */}
                            {rec.candidate_evidence && (
                                <div className="rounded-lg bg-[var(--surface-hover)]/70 p-2.5 text-xs text-[var(--text-secondary)] flex items-center gap-2">
                                    <span className="font-semibold text-[var(--text-primary)]">Existing Base:</span>
                                    <span className="font-mono text-amber-400">{rec.candidate_evidence}</span>
                                    <ArrowRight size={13} className="text-[var(--text-muted)]" />
                                    <span className="font-mono text-indigo-400">{rec.related_requirement}</span>
                                </div>
                            )}

                            {/* Suggested Action Items */}
                            {rec.suggested_actions && rec.suggested_actions.length > 0 && (
                                <div className="space-y-1.5 pt-1">
                                    <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-primary)] flex items-center gap-1.5">
                                        <CheckSquare2 size={13} className="text-[var(--accent)]" />
                                        <span>Recommended Practical Steps:</span>
                                    </span>
                                    <ul className="space-y-1 pl-1">
                                        {rec.suggested_actions.map((action, actionIdx) => (
                                            <li
                                                key={actionIdx}
                                                className="text-xs text-[var(--text-secondary)] leading-relaxed flex items-start gap-2"
                                            >
                                                <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-[var(--surface-hover)] text-[10px] font-bold text-[var(--accent)] mt-0.5">
                                                    {actionIdx + 1}
                                                </span>
                                                <span>{action}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>

            {/* Evidence & Integrity Safeguard Note */}
            <div className="flex items-start gap-2.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3.5 text-xs text-[var(--text-muted)]">
                <ShieldCheck size={16} className="mt-0.5 shrink-0 text-[var(--success)]" />
                <span>
                    <strong>CareerMind Integrity Standard:</strong> Recommendations emphasize building demonstrable, hands-on repository projects before listing technologies on your profile. Never fabricate experience or claim proficiency before completing functional deliverables.
                </span>
            </div>
        </div>
    )
}
