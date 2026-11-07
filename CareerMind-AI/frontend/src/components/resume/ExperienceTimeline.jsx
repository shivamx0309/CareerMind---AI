import { Briefcase, Calendar, Building2, Wrench, MapPin } from 'lucide-react'

export default function ExperienceTimeline({ experience }) {
    const entries = Array.isArray(experience) ? experience : []

    return (
        <div className="glass-card p-6 sm:p-8">
            <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <Briefcase size={20} />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Work Experience & Internships
                        </h3>
                        <p className="text-xs text-[var(--text-muted)]">
                            Professional roles and responsibilities
                        </p>
                    </div>
                </div>

                <span className="rounded-full bg-[var(--surface-hover)] px-2.5 py-1 text-xs font-semibold text-[var(--text-secondary)]">
                    {entries.length} {entries.length === 1 ? 'Position' : 'Positions'}
                </span>
            </div>

            {entries.length > 0 ? (
                <div className="relative space-y-6 before:absolute before:top-3 before:bottom-3 before:left-4 before:w-0.5 before:bg-[var(--border)] sm:before:left-5">
                    {entries.map((job, idx) => {
                        const dateRange = [job.start_date, job.end_date].filter(Boolean).join(' – ')
                        const hasTechnologies = Array.isArray(job.technologies) && job.technologies.length > 0

                        return (
                            <div key={idx} className="relative flex items-start gap-4 sm:gap-5">
                                {/* Timeline Dot */}
                                <div className="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border border-[var(--accent)]/30 bg-[var(--surface-solid)] text-[var(--accent)] shadow-sm sm:h-10 sm:w-10">
                                    <Briefcase size={18} />
                                </div>

                                {/* Content Card */}
                                <div className="flex-1 rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 sm:p-5 transition-all hover:border-[var(--accent)]/50 hover:shadow-sm">
                                    <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                                        <div>
                                            <div className="flex flex-wrap items-center gap-2">
                                                <h4 className="text-base font-bold text-[var(--text-primary)]">
                                                    {job.job_title || 'Position / Role'}
                                                </h4>
                                                {job.employment_type && (
                                                    <span className="rounded-md border border-[var(--accent)]/30 bg-[var(--accent-soft)] px-2 py-0.5 text-xs font-semibold text-[var(--accent)]">
                                                        {job.employment_type}
                                                    </span>
                                                )}
                                            </div>

                                            <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
                                                {job.company && (
                                                    <p className="flex items-center gap-1.5 text-sm font-medium text-[var(--text-secondary)]">
                                                        <Building2 size={14} className="text-[var(--accent)]" />
                                                        <span>{job.company}</span>
                                                    </p>
                                                )}

                                                {job.location && (
                                                    <span className="flex items-center gap-1 text-xs font-medium text-[var(--text-muted)]">
                                                        <MapPin size={13} className="text-[var(--accent)]" />
                                                        <span>{job.location}</span>
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        {dateRange && (
                                            <span className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-[var(--text-muted)] sm:mt-0">
                                                <Calendar size={13} />
                                                <span>{dateRange}</span>
                                            </span>
                                        )}
                                    </div>

                                    {/* Description bullets */}
                                    {job.description && (
                                        <div className="mt-3.5 space-y-1.5 text-sm leading-relaxed text-[var(--text-secondary)]">
                                            {job.description.split('\n').map((line, lIdx) => (
                                                <p key={lIdx} className="whitespace-pre-line">
                                                    {line}
                                                </p>
                                            ))}
                                        </div>
                                    )}

                                    {/* Technologies */}
                                    {hasTechnologies && (
                                        <div className="mt-4 pt-3 border-t border-[var(--border)]">
                                            <div className="flex flex-wrap items-center gap-1.5">
                                                <span className="flex items-center gap-1 text-xs font-medium text-[var(--text-muted)] mr-1">
                                                    <Wrench size={12} /> Tech:
                                                </span>
                                                {job.technologies.map((t) => (
                                                    <span
                                                        key={t}
                                                        className="rounded-md border border-[var(--border)] bg-[var(--surface-hover)] px-2 py-0.5 text-xs font-medium text-[var(--text-primary)]"
                                                    >
                                                        {t}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>
            ) : (
                <div className="rounded-xl border border-dashed border-[var(--border)] p-6 text-center text-sm text-[var(--text-muted)]">
                    No work experience or internships detected in this resume.
                </div>
            )}
        </div>
    )
}

