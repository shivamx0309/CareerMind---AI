import { ArrowRight, Sparkles, Tag, Info } from 'lucide-react'
import { getCategoryMeta } from '../../utils/skillCategoryConfig'

export default function RelatedSkillsPanel({ relatedSkills = [] }) {
    if (!relatedSkills || relatedSkills.length === 0) {
        return (
            <div className="glass-card rounded-2xl p-6 text-center space-y-2">
                <Sparkles size={28} className="mx-auto text-[var(--text-muted)]" />
                <h4 className="text-base font-bold text-[var(--text-primary)]">
                    No Semantically Related Skills
                </h4>
                <p className="text-xs text-[var(--text-muted)] max-w-sm mx-auto">
                    All skills detected in the candidate profile were either directly matched or outside the benchmark clusters.
                </p>
            </div>
        )
    }

    return (
        <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                        <Sparkles size={18} className="text-amber-500 dark:text-amber-400" />
                        <h3 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                            Semantically Related Skills ({relatedSkills.length})
                        </h3>
                    </div>
                    <p className="text-xs text-[var(--text-muted)]">
                        Competencies within the same skill cluster that earn 60% partial credit
                    </p>
                </div>

                <span className="self-start sm:self-auto rounded-full bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 text-[11px] font-semibold text-amber-500 dark:text-amber-400">
                    60% Partial Credit
                </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                {relatedSkills.map((item, idx) => {
                    const meta = getCategoryMeta(item.category)
                    const Icon = meta.icon

                    return (
                        <div
                            key={`${item.skill_name}-${idx}`}
                            className="rounded-xl border border-amber-500/20 bg-amber-500/5 dark:bg-amber-500/5 p-4 space-y-3"
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex items-center gap-2">
                                    <Icon size={16} style={{ color: meta.color }} />
                                    <span className="text-xs font-semibold text-[var(--text-muted)]">
                                        {meta.label}
                                    </span>
                                </div>
                                <span className="text-[10px] uppercase font-bold tracking-wider text-[var(--text-muted)]">
                                    {item.importance}
                                </span>
                            </div>

                            {/* Relationship Mapping: Candidate Skill -> Benchmark Skill */}
                            <div className="flex items-center gap-2 p-2.5 rounded-lg bg-[var(--surface-solid)] border border-[var(--border)]">
                                <div className="flex-1">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-500 block">
                                        Detected in Resume
                                    </span>
                                    <span className="text-xs sm:text-sm font-bold text-[var(--text-primary)]">
                                        {item.matched_skill || 'Related Competency'}
                                    </span>
                                </div>

                                <ArrowRight size={14} className="text-amber-400 shrink-0" />

                                <div className="flex-1 text-right">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--accent)] block">
                                        Benchmark Target
                                    </span>
                                    <span className="text-xs sm:text-sm font-bold text-[var(--text-primary)]">
                                        {item.skill_name}
                                    </span>
                                </div>
                            </div>

                            {/* Footnote / Context */}
                            <div className="flex items-center justify-between text-[11px] text-[var(--text-muted)]">
                                <span>Weight credit: 0.6x</span>
                                {item.evidence_source && (
                                    <span className="inline-flex items-center gap-1 font-medium text-[var(--text-secondary)]">
                                        <Tag size={10} />
                                        <span>Source: {item.evidence_source}</span>
                                    </span>
                                )}
                            </div>
                        </div>
                    )
                })}
            </div>

            <div className="flex items-start gap-2 rounded-xl bg-[var(--surface-solid)] border border-[var(--border)] p-3 text-xs text-[var(--text-secondary)]">
                <Info size={14} className="text-amber-400 mt-0.5 shrink-0" />
                <span>
                    Related skills indicate transferable capability (e.g. Django experience transitioning to FastAPI, or React to Vue). They demonstrate foundational readiness and reduce ramp-up time.
                </span>
            </div>
        </div>
    )
}

