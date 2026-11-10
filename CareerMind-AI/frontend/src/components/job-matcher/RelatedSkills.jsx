import {
    GitFork,
    ArrowRight,
    ShieldAlert,
} from 'lucide-react'

export default function RelatedSkills({ relatedSkills = [] }) {
    if (!relatedSkills || relatedSkills.length === 0) {
        return null
    }

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-6 border-l-4 border-l-amber-500">
            <div className="flex flex-col gap-2 border-b border-[var(--border)] pb-4">
                <div className="flex items-center gap-2">
                    <GitFork size={18} className="text-amber-600 dark:text-amber-400" />
                    <h3 className="text-lg font-bold text-[var(--text-primary)]">
                        Semantically Related Technologies
                    </h3>
                    <span className="rounded-full border border-amber-500/30 bg-amber-500/15 px-2.5 py-0.5 text-xs font-bold text-amber-800 dark:text-amber-300">
                        {relatedSkills.length}
                    </span>
                </div>

                {/* Critical Boundary Notice */}
                <div className="flex items-start gap-2.5 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-900 dark:text-amber-200">
                    <ShieldAlert size={16} className="mt-0.5 shrink-0 text-amber-600 dark:text-amber-400" />
                    <div>
                        <strong className="font-semibold block mb-0.5">
                            Conceptual Similarity ≠ Direct Interchangeability
                        </strong>
                        <span>
                            These technologies share architectural patterns with target requirements, but represent distinct tools.
                            Candidates receive partial credit for conceptual familiarity, not direct requirement satisfaction.
                        </span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {relatedSkills.map((item, idx) => (
                    <div
                        key={`${item.skill}-${idx}`}
                        className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/60 p-4 transition-all hover:border-amber-500/40"
                    >
                        <div className="flex items-start justify-between gap-2">
                            <div>
                                <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                                    Target Requirement
                                </span>
                                <h4 className="text-base font-bold text-[var(--text-primary)]">
                                    {item.skill}
                                </h4>
                            </div>

                            <span className="rounded-full border border-amber-500/30 bg-amber-500/15 px-2.5 py-0.5 text-[11px] font-semibold text-amber-800 dark:text-amber-300">
                                Partial Credit ({Math.round((item.match_confidence ?? item.confidence ?? 0.6) * 100)}%)
                            </span>
                        </div>

                        {/* Bridge relationship arrow */}
                        <div className="my-3 flex items-center gap-2 rounded-lg bg-[var(--surface-hover)]/70 p-2.5 text-xs">
                            <span className="text-xs font-medium text-[var(--text-secondary)]">
                                Resume Has:
                            </span>
                            <span className="font-mono font-bold text-amber-700 dark:text-amber-400">
                                {item.candidate_evidence || 'Related Tool'}
                            </span>
                            <ArrowRight size={13} className="text-[var(--text-muted)]" />
                            <span className="font-mono font-bold text-indigo-700 dark:text-indigo-400">
                                {item.skill}
                            </span>
                        </div>

                        {/* Relationship Explanation */}
                        {item.relationship_explanation && (
                            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                                {item.relationship_explanation}
                            </p>
                        )}

                        {/* Original JD Phrase */}
                        {item.original_jd_phrase && (
                            <div className="mt-2 text-[11px] text-[var(--text-muted)] italic truncate" title={item.original_jd_phrase}>
                                JD: "{item.original_jd_phrase}"
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    )
}
