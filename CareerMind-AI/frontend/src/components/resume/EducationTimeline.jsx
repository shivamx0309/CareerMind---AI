import { GraduationCap, Calendar, Award, BookOpen } from 'lucide-react'

export default function EducationTimeline({ education }) {
    const entries = Array.isArray(education) ? education : []

    return (
        <div className="glass-card p-6 sm:p-8">
            <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <GraduationCap size={20} />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Education & Qualifications
                        </h3>
                        <p className="text-xs text-[var(--text-muted)]">
                            Academic history and degree credentials
                        </p>
                    </div>
                </div>

                <span className="rounded-full bg-[var(--surface-hover)] px-2.5 py-1 text-xs font-semibold text-[var(--text-secondary)]">
                    {entries.length} {entries.length === 1 ? 'Credential' : 'Credentials'}
                </span>
            </div>

            {entries.length > 0 ? (
                <div className="relative space-y-6 before:absolute before:top-3 before:bottom-3 before:left-4 before:w-0.5 before:bg-[var(--border)] sm:before:left-5">
                    {entries.map((edu, idx) => {
                        const years = [edu.start_year, edu.end_year].filter(Boolean).join(' – ')
                        return (
                            <div key={idx} className="relative flex items-start gap-4 sm:gap-5">
                                {/* Timeline Dot */}
                                <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-[var(--accent)]/30 bg-[var(--surface-solid)] text-[var(--accent)] shadow-sm sm:h-10 sm:w-10">
                                    <GraduationCap size={18} />
                                </div>

                                {/* Content Card */}
                                <div className="flex-1 rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 sm:p-5 transition-all hover:border-[var(--accent)]/50 hover:shadow-sm">
                                    <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                                        <div>
                                            <h4 className="text-base font-bold text-[var(--text-primary)]">
                                                {edu.degree || 'Degree Qualification'}
                                            </h4>
                                            {edu.specialization && (
                                                <p className="flex items-center gap-1.5 text-sm font-medium text-[var(--accent)]">
                                                    <BookOpen size={14} />
                                                    <span>{edu.specialization}</span>
                                                </p>
                                            )}
                                        </div>

                                        {years && (
                                            <span className="inline-flex items-center gap-1 text-xs font-medium text-[var(--text-muted)]">
                                                <Calendar size={13} />
                                                <span>{years}</span>
                                            </span>
                                        )}
                                    </div>

                                    {edu.institution && (
                                        <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                            {edu.institution}
                                        </p>
                                    )}

                                    {edu.grade_or_cgpa && (
                                        <div className="mt-3">
                                            <span className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--success)]/25 bg-[var(--success)]/10 px-2.5 py-1 text-xs font-semibold text-[var(--success)]">
                                                <Award size={13} />
                                                <span>Score: {edu.grade_or_cgpa}</span>
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>
            ) : (
                <div className="rounded-xl border border-dashed border-[var(--border)] p-6 text-center text-sm text-[var(--text-muted)]">
                    No educational history detected in this resume.
                </div>
            )}
        </div>
    )
}

