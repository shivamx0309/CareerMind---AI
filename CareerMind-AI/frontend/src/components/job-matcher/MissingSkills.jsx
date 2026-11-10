import {
    AlertOctagon,
    Flame,
    Bookmark,
} from 'lucide-react'

export default function MissingSkills({
    missingRequired = [],
    missingPreferred = [],
}) {
    const totalMissing = missingRequired.length + missingPreferred.length

    if (totalMissing === 0) {
        return (
            <div className="glass-card rounded-2xl p-6 text-center">
                <span className="text-xs font-semibold text-emerald-400">
                    No Missing Skills Identified — Candidate profile covers all parsed skill requirements!
                </span>
            </div>
        )
    }

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col gap-1 border-b border-[var(--border)] pb-4">
                <div className="flex items-center gap-2">
                    <AlertOctagon size={18} className="text-rose-600 dark:text-rose-400" />
                    <h3 className="text-lg font-bold text-[var(--text-primary)]">
                        Identified Skill Gaps
                    </h3>
                    <span className="rounded-full border border-rose-500/30 bg-rose-500/15 px-2.5 py-0.5 text-xs font-bold text-rose-700 dark:text-rose-300">
                        {totalMissing}
                    </span>
                </div>
                <p className="text-xs text-[var(--text-secondary)]">
                    Target job requirements without defensible evidence in the candidate's resume or project repository.
                </p>
            </div>

            {/* Section 1: Missing Required Skills (High Priority) */}
            {missingRequired.length > 0 && (
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <Flame size={15} className="text-rose-500" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400">
                            Missing Mandatory Skills ({missingRequired.length})
                        </h4>
                    </div>

                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                        {missingRequired.map((item, idx) => {
                            const skillName = typeof item === 'string' ? item : item.skill || 'Skill'
                            const jdPhrase = typeof item === 'object' ? item.original_jd_phrase : null

                            return (
                                <div
                                    key={`${skillName}-${idx}`}
                                    className="rounded-xl border border-rose-500/25 bg-rose-500/5 p-4 transition-all hover:border-rose-500/40"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <h5 className="text-sm font-bold text-[var(--text-primary)]">
                                            {skillName}
                                        </h5>
                                        <span className="rounded-full border border-rose-500/30 bg-rose-500/10 px-2 py-0.5 text-[10px] font-bold text-rose-700 dark:text-rose-400 shrink-0">
                                            Required
                                        </span>
                                    </div>

                                    <p className="mt-2 text-xs text-rose-800/80 dark:text-rose-300/80 leading-relaxed">
                                        No direct mentions or verifiable project demonstrations detected in profile.
                                    </p>

                                    {jdPhrase && (
                                        <div className="mt-2 text-[11px] text-[var(--text-muted)] italic truncate" title={jdPhrase}>
                                            JD: "{jdPhrase}"
                                        </div>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Section 2: Missing Preferred Skills (Secondary Priority) */}
            {missingPreferred.length > 0 && (
                <div className="space-y-3 pt-2">
                    <div className="flex items-center gap-2">
                        <Bookmark size={15} className="text-amber-500" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
                            Missing Preferred Qualifications ({missingPreferred.length})
                        </h4>
                    </div>

                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                        {missingPreferred.map((item, idx) => {
                            const skillName = typeof item === 'string' ? item : item.skill || 'Skill'
                            const jdPhrase = typeof item === 'object' ? item.original_jd_phrase : null

                            return (
                                <div
                                    key={`${skillName}-${idx}`}
                                    className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 transition-all hover:border-amber-500/35"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <h5 className="text-sm font-bold text-[var(--text-primary)]">
                                            {skillName}
                                        </h5>
                                        <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[10px] font-medium text-amber-800 dark:text-amber-400 shrink-0">
                                            Preferred
                                        </span>
                                    </div>

                                    <p className="mt-2 text-xs text-amber-800/80 dark:text-amber-300/80 leading-relaxed">
                                        Nice-to-have skill not currently evidenced in candidate history.
                                    </p>

                                    {jdPhrase && (
                                        <div className="mt-2 text-[11px] text-[var(--text-muted)] italic truncate" title={jdPhrase}>
                                            JD: "{jdPhrase}"
                                        </div>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    )
}
