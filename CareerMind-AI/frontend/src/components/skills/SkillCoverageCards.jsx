import { Sparkles } from 'lucide-react'

export default function SkillCoverageCards({ report }) {
    if (!report) return null

    const {
        required_coverage_percentage,
        preferred_coverage_percentage,
        total_required_skills,
        matched_required_skills_count,
        related_required_skills_count,
        missing_required_skills_count,
        total_preferred_skills,
        matched_preferred_skills_count,
        related_preferred_skills_count,
        missing_preferred_skills_count,
    } = report

    return (
        <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 1. Required Skills Coverage Card */}
                <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-4 border-l-4 border-l-[var(--accent)]">
                    <div className="flex items-start justify-between">
                        <div>
                            <span className="text-xs font-bold uppercase tracking-wider text-[var(--accent)]">
                                Baseline Mandatory
                            </span>
                            <h3 className="text-lg font-bold text-[var(--text-primary)]">
                                Required Skills Coverage
                            </h3>
                        </div>
                        <div className="text-right">
                            <span className="text-2xl font-black text-[var(--text-primary)]">
                                {required_coverage_percentage !== null && required_coverage_percentage !== undefined
                                    ? `${required_coverage_percentage}%`
                                    : 'N/A'}
                            </span>
                            <div className="text-[11px] text-[var(--text-muted)]">
                                Direct Match Rate
                            </div>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--surface-hover)]">
                        <div
                            className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] transition-all duration-500"
                            style={{
                                width: `${Math.min(Math.max(required_coverage_percentage || 0, 0), 100)}%`,
                            }}
                        />
                    </div>

                    {/* Breakdown Counts */}
                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--border)]/60 text-center">
                        <div className="p-2 rounded-xl bg-[var(--surface-solid)]">
                            <div className="text-sm font-bold text-[var(--success)]">
                                {matched_required_skills_count}
                            </div>
                            <div className="text-[10px] text-[var(--text-muted)] font-medium">
                                Matched (1.0x)
                            </div>
                        </div>

                        <div className="p-2 rounded-xl bg-[var(--surface-solid)]">
                            <div className="text-sm font-bold text-amber-500 dark:text-amber-400">
                                {related_required_skills_count}
                            </div>
                            <div className="text-[10px] text-[var(--text-muted)] font-medium">
                                Related (0.6x)
                            </div>
                        </div>

                        <div className="p-2 rounded-xl bg-[var(--surface-solid)]">
                            <div className="text-sm font-bold text-rose-500 dark:text-rose-400">
                                {missing_required_skills_count}
                            </div>
                            <div className="text-[10px] text-[var(--text-muted)] font-medium">
                                Missing of {total_required_skills}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. Preferred Skills Coverage Card */}
                <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-4 border-l-4 border-l-purple-400 dark:border-l-purple-500">
                    <div className="flex items-start justify-between">
                        <div>
                            <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                                High-Value Addition
                            </span>
                            <h3 className="text-lg font-bold text-[var(--text-primary)]">
                                Preferred Skills Coverage
                            </h3>
                        </div>
                        <div className="text-right">
                            <span className="text-2xl font-black text-[var(--text-primary)]">
                                {preferred_coverage_percentage !== null && preferred_coverage_percentage !== undefined
                                    ? `${preferred_coverage_percentage}%`
                                    : '100%'}
                            </span>
                            <div className="text-[11px] text-[var(--text-muted)]">
                                Bonus Weight Rate
                            </div>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--surface-hover)]">
                        <div
                            className="h-full rounded-full bg-gradient-to-r from-purple-500 to-indigo-400 transition-all duration-500"
                            style={{
                                width: `${Math.min(Math.max(preferred_coverage_percentage || 0, 0), 100)}%`,
                            }}
                        />
                    </div>

                    {/* Breakdown Counts */}
                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--border)]/60 text-center">
                        <div className="p-2 rounded-xl bg-[var(--surface-solid)]">
                            <div className="text-sm font-bold text-[var(--success)]">
                                {matched_preferred_skills_count}
                            </div>
                            <div className="text-[10px] text-[var(--text-muted)] font-medium">
                                Matched (1.0x)
                            </div>
                        </div>

                        <div className="p-2 rounded-xl bg-[var(--surface-solid)]">
                            <div className="text-sm font-bold text-amber-500 dark:text-amber-400">
                                {related_preferred_skills_count}
                            </div>
                            <div className="text-[10px] text-[var(--text-muted)] font-medium">
                                Related (0.6x)
                            </div>
                        </div>

                        <div className="p-2 rounded-xl bg-[var(--surface-solid)]">
                            <div className="text-sm font-bold text-rose-500 dark:text-rose-400">
                                {missing_preferred_skills_count}
                            </div>
                            <div className="text-[10px] text-[var(--text-muted)] font-medium">
                                Missing of {total_preferred_skills}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Informative Partial Credit Pill */}
            <div className="flex items-center gap-2 rounded-xl bg-[var(--surface-solid)] border border-[var(--border)] px-4 py-2.5 text-xs text-[var(--text-secondary)]">
                <Sparkles size={14} className="text-[var(--accent)] shrink-0" />
                <span>
                    <strong>Scoring Weight Policy:</strong> Required skills carry full weight (1.0). Preferred skills carry half weight (0.5). Semantically related skills from the same competency cluster earn 60% partial credit (0.6x).
                </span>
            </div>
        </div>
    )
}
