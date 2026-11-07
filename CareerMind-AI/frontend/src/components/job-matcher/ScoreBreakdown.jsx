import {
    Code2,
    Star,
    Briefcase,
    GraduationCap,
    FileSearch,
    CheckCircle,
    MinusCircle,
    AlertCircle,
} from 'lucide-react'

const COMPONENT_METADATA = {
    required_skills: {
        label: 'Required Skills',
        defaultBaseWeight: '40%',
        icon: Code2,
        accentColor: 'text-indigo-400',
        barColor: 'bg-indigo-500',
    },
    preferred_skills: {
        label: 'Preferred Skills',
        defaultBaseWeight: '15%',
        icon: Star,
        accentColor: 'text-amber-400',
        barColor: 'bg-amber-500',
    },
    experience: {
        label: 'Experience Relevance',
        defaultBaseWeight: '25%',
        icon: Briefcase,
        accentColor: 'text-blue-400',
        barColor: 'bg-blue-500',
    },
    education: {
        label: 'Education Alignment',
        defaultBaseWeight: '10%',
        icon: GraduationCap,
        accentColor: 'text-emerald-400',
        barColor: 'bg-emerald-500',
    },
    lexical_relevance: {
        label: 'Lexical Relevance',
        defaultBaseWeight: '10%',
        icon: FileSearch,
        accentColor: 'text-purple-400',
        barColor: 'bg-purple-500',
    },
}

export default function ScoreBreakdown({ components = {} }) {
    const componentEntries = [
        'required_skills',
        'preferred_skills',
        'experience',
        'education',
        'lexical_relevance',
    ]

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col gap-1 border-b border-[var(--border)] pb-4">
                <h3 className="text-lg font-bold text-[var(--text-primary)]">
                    Scoring Dimensions & Explainable Weights
                </h3>
                <p className="text-xs text-[var(--text-secondary)]">
                    Transparent breakdown across all 5 evaluation dimensions with deterministic weight normalization.
                </p>
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                {componentEntries.map((key) => {
                    const comp = components[key]
                    const meta = COMPONENT_METADATA[key]
                    const Icon = meta.icon

                    if (!comp) {
                        return null
                    }

                    const isAvailable = comp.availability === 'available'
                    const isInsufficient = comp.availability === 'insufficient_data'
                    const rawScore = comp.raw_score
                    const baseWeightPercent = Math.round(comp.base_weight * 100)
                    const normWeightPercent = Math.round((comp.normalized_weight || 0) * 100)
                    const contribution = comp.weighted_contribution || 0

                    return (
                        <div
                            key={key}
                            className={`rounded-xl border p-4.5 transition-all flex flex-col justify-between ${
                                isAvailable
                                    ? 'border-[var(--border)] bg-[var(--surface-solid)]/60'
                                    : 'border-slate-800 bg-slate-900/30 opacity-75'
                            }`}
                        >
                            <div>
                                {/* Header: Icon, Label, and Availability Badge */}
                                <div className="flex items-center justify-between gap-3">
                                    <div className="flex items-center gap-2.5">
                                        <div
                                            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--accent-soft)] ${meta.accentColor}`}
                                        >
                                            <Icon size={16} />
                                        </div>
                                        <div>
                                            <h4 className="text-sm font-semibold text-[var(--text-primary)]">
                                                {meta.label}
                                            </h4>
                                            <span className="text-[11px] text-[var(--text-muted)]">
                                                Base Weight: {baseWeightPercent}%
                                                {comp.normalized_weight > 0 &&
                                                    normWeightPercent !== baseWeightPercent && (
                                                        <span className="text-purple-400 font-medium ml-1">
                                                            (Normalized: {normWeightPercent}%)
                                                        </span>
                                                    )}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Availability Status Badge */}
                                    <div>
                                        {isAvailable ? (
                                            <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-400">
                                                <CheckCircle size={11} />
                                                <span>Available</span>
                                            </span>
                                        ) : isInsufficient ? (
                                            <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-0.5 text-[11px] font-semibold text-amber-400">
                                                <AlertCircle size={11} />
                                                <span>Insufficient Data</span>
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center gap-1 rounded-full border border-slate-600/40 bg-slate-700/20 px-2.5 py-0.5 text-[11px] font-semibold text-slate-400">
                                                <MinusCircle size={11} />
                                                <span>Not Required</span>
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Score & Contribution Indicators */}
                                {isAvailable && rawScore !== null ? (
                                    <div className="mt-4 space-y-2">
                                        <div className="flex items-baseline justify-between text-xs">
                                            <span className="font-semibold text-[var(--text-primary)]">
                                                Raw Score: {Math.round(rawScore)}%
                                            </span>
                                            <span className="font-semibold text-[var(--accent)] font-mono">
                                                +{contribution.toFixed(1)} pts
                                            </span>
                                        </div>

                                        {/* Progress bar */}
                                        <div className="h-1.5 w-full rounded-full bg-[var(--surface-hover)] overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-700 ${meta.barColor}`}
                                                style={{ width: `${Math.min(100, Math.max(0, rawScore))}%` }}
                                            />
                                        </div>
                                    </div>
                                ) : (
                                    <div className="mt-3 rounded-lg bg-[var(--surface-hover)]/40 p-2.5 text-xs text-[var(--text-muted)] italic">
                                        Component unassessed. Excluded from calculation without score penalty.
                                    </div>
                                )}

                                {/* Explanation Reason */}
                                {comp.reason && (
                                    <p className="mt-3 text-xs text-[var(--text-secondary)] leading-relaxed">
                                        {comp.reason}
                                    </p>
                                )}
                            </div>

                            {/* Evidence List */}
                            {comp.evidence && comp.evidence.length > 0 && (
                                <div className="mt-3 border-t border-[var(--border)] pt-2.5">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] block mb-1">
                                        Evidence:
                                    </span>
                                    <ul className="space-y-1">
                                        {comp.evidence.slice(0, 2).map((ev, idx) => {
                                            const text = typeof ev === 'string' ? ev : (ev?.explanation || ev?.project_name || JSON.stringify(ev))
                                            return (
                                                <li
                                                    key={idx}
                                                    className="text-[11px] text-[var(--text-secondary)] truncate font-mono bg-[var(--surface-hover)]/30 rounded px-1.5 py-0.5"
                                                    title={text}
                                                >
                                                    {text}
                                                </li>
                                            )
                                        })}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

