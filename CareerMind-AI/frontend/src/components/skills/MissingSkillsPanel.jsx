import { AlertOctagon, HelpCircle } from 'lucide-react'

export default function MissingSkillsPanel({
    missingRequired = [],
    missingPreferred = [],
}) {
    const hasRequired = missingRequired && missingRequired.length > 0
    const hasPreferred = missingPreferred && missingPreferred.length > 0

    if (!hasRequired && !hasPreferred) {
        return (
            <div className="glass-card rounded-2xl p-6 text-center space-y-2">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500">
                    <AlertOctagon size={22} />
                </div>
                <h4 className="text-base font-bold text-[var(--text-primary)]">
                    Zero Benchmark Skill Gaps!
                </h4>
                <p className="text-xs text-[var(--text-muted)] max-w-sm mx-auto">
                    Your candidate profile demonstrates all required and preferred skills specified by this role benchmark.
                </p>
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Missing Required Skills */}
            <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-4 border-l-4 border-l-rose-500">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-1.5">
                            <AlertOctagon size={18} className="text-rose-500 shrink-0" />
                            <h3 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                                Missing Required Skills ({missingRequired.length})
                            </h3>
                        </div>
                        <p className="text-xs text-[var(--text-muted)] pt-0.5">
                            Core baseline gaps that carry full weight in benchmark evaluation
                        </p>
                    </div>
                </div>

                {hasRequired ? (
                    <div className="flex flex-wrap gap-2 pt-1">
                        {missingRequired.map((skill, idx) => (
                            <span
                                key={`${skill}-${idx}`}
                                className="inline-flex items-center gap-1 rounded-xl border border-rose-500/30 bg-rose-500/10 px-3 py-1.5 text-xs font-semibold text-rose-600 dark:text-rose-300"
                            >
                                <span>{skill}</span>
                            </span>
                        ))}
                    </div>
                ) : (
                    <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-3 text-xs text-emerald-400 font-medium">
                        ✓ All required core skills are present in candidate profile!
                    </div>
                )}
            </div>

            {/* Missing Preferred Skills */}
            <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-4 border-l-4 border-l-purple-500/60">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-1.5">
                            <HelpCircle size={18} className="text-purple-400 shrink-0" />
                            <h3 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                                Missing Preferred Skills ({missingPreferred.length})
                            </h3>
                        </div>
                        <p className="text-xs text-[var(--text-muted)] pt-0.5">
                            Secondary skills and bonus technologies for targeted upskilling
                        </p>
                    </div>
                </div>

                {hasPreferred ? (
                    <div className="flex flex-wrap gap-2 pt-1">
                        {missingPreferred.map((skill, idx) => (
                            <span
                                key={`${skill}-${idx}`}
                                className="inline-flex items-center gap-1 rounded-xl border border-purple-500/20 bg-purple-500/10 px-3 py-1.5 text-xs font-semibold text-purple-700 dark:text-purple-300"
                            >
                                <span>{skill}</span>
                            </span>
                        ))}
                    </div>
                ) : (
                    <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-3 text-xs text-emerald-400 font-medium">
                        ✓ All preferred bonus skills are present!
                    </div>
                )}
            </div>
        </div>
    )
}
