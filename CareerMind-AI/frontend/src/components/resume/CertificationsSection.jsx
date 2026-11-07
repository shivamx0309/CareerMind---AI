import { Award, ExternalLink, Calendar, Building, CheckCircle, Trophy, Sparkles } from 'lucide-react'

export default function CertificationsSection({ certifications = [], achievements = [] }) {
    const certsList = Array.isArray(certifications) ? certifications : []
    const achList = Array.isArray(achievements) ? achievements : []
    const totalCount = certsList.length + achList.length

    return (
        <div className="glass-card p-6 sm:p-8">
            <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <Award size={20} />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Certifications & Achievements
                        </h3>
                        <p className="text-xs text-[var(--text-muted)]">
                            Accredited programs, awards, competitions, and milestones
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {certsList.length > 0 && (
                        <span className="rounded-full bg-[var(--surface-hover)] px-2.5 py-1 text-xs font-semibold text-[var(--text-secondary)]">
                            {certsList.length} {certsList.length === 1 ? 'Cert' : 'Certs'}
                        </span>
                    )}
                    {achList.length > 0 && (
                        <span className="rounded-full bg-[var(--accent-soft)] px-2.5 py-1 text-xs font-semibold text-[var(--accent)]">
                            {achList.length} {achList.length === 1 ? 'Achievement' : 'Achievements'}
                        </span>
                    )}
                </div>
            </div>

            {totalCount > 0 ? (
                <div className="space-y-6">
                    {/* Certifications & Job Simulations */}
                    {certsList.length > 0 && (
                        <div>
                            {achList.length > 0 && (
                                <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">
                                    Accredited Programs & Certifications
                                </h4>
                            )}
                            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                {certsList.map((cert, idx) => (
                                    <div
                                        key={idx}
                                        className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 sm:p-5 transition-all hover:border-[var(--accent)]/50 hover:shadow-sm"
                                    >
                                        <div className="flex items-start gap-3">
                                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--accent-soft)] text-[var(--accent)]">
                                                <CheckCircle size={16} />
                                            </div>
                                            <div className="min-w-0 flex-1">
                                                <h4 className="text-sm font-bold text-[var(--text-primary)] leading-snug">
                                                    {cert.certification_name || 'Certification'}
                                                </h4>

                                                <div className="mt-2 flex flex-wrap items-center gap-2">
                                                    {cert.issuing_organization && (
                                                        <span className="inline-flex items-center gap-1 rounded-md border border-[var(--accent)]/30 bg-[var(--accent-soft)] px-2 py-0.5 text-xs font-semibold text-[var(--accent)]">
                                                            <Building size={11} />
                                                            <span>{cert.issuing_organization}</span>
                                                        </span>
                                                    )}

                                                    {cert.issue_date && (
                                                        <span className="inline-flex items-center gap-1 text-xs text-[var(--text-muted)]">
                                                            <Calendar size={11} />
                                                            <span>{cert.issue_date}</span>
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>

                                        {cert.credential_url && (
                                            <div className="mt-4 pt-3 border-t border-[var(--border)] flex justify-end">
                                                <a
                                                    href={cert.credential_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center gap-1.5 text-xs font-medium text-[var(--accent)] hover:underline"
                                                >
                                                    <span>Verify Credential</span>
                                                    <ExternalLink size={12} />
                                                </a>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Honors, Awards & Coding Milestones */}
                    {achList.length > 0 && (
                        <div>
                            {certsList.length > 0 && (
                                <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">
                                    Honors, Awards & Milestones
                                </h4>
                            )}
                            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                                {achList.map((ach, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-start gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 transition-all hover:border-[var(--accent)]/40 hover:shadow-sm"
                                    >
                                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-500/10 text-amber-500">
                                            {ach.category === 'Award / Recognition' ? (
                                                <Trophy size={16} />
                                            ) : (
                                                <Sparkles size={16} />
                                            )}
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <p className="text-sm font-semibold text-[var(--text-primary)] leading-snug">
                                                {ach.title}
                                            </p>
                                            <div className="mt-2 flex flex-wrap items-center gap-2">
                                                {ach.category && (
                                                    <span className="rounded-md border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-400">
                                                        {ach.category}
                                                    </span>
                                                )}
                                                {ach.organization && (
                                                    <span className="inline-flex items-center gap-1 text-xs font-medium text-[var(--text-muted)]">
                                                        <Building size={11} />
                                                        <span>{ach.organization}</span>
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <div className="rounded-xl border border-dashed border-[var(--border)] p-6 text-center text-sm text-[var(--text-muted)]">
                    No certifications or achievement credentials detected in this resume.
                </div>
            )}
        </div>
    )
}
