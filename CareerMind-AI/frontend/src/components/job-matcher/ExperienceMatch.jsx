import {
    Briefcase,
    FolderGit2,
    CheckCircle2,
    AlertCircle,
    Info,
    Clock,
    FileQuestion,
} from 'lucide-react'

function formatAssessmentStatus(status) {
    switch (status) {
        case 'exceeds_requirement':
            return {
                label: 'Exceeds Requirement',
                className: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
                icon: CheckCircle2,
            }
        case 'meets_requirement':
            return {
                label: 'Meets Requirement',
                className: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
                icon: CheckCircle2,
            }
        case 'partial':
            return {
                label: 'Partial Match',
                className: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
                icon: AlertCircle,
            }
        case 'below_requirement':
            return {
                label: 'Below Requirement',
                className: 'border-rose-500/30 bg-rose-500/10 text-rose-400',
                icon: AlertCircle,
            }
        case 'not_required':
            return {
                label: 'Not Required by JD',
                className: 'border-slate-600/30 bg-slate-700/20 text-slate-400',
                icon: Info,
            }
        case 'insufficient_data':
        default:
            return {
                label: 'Insufficient Date Data',
                className: 'border-slate-500/30 bg-slate-500/10 text-slate-300',
                icon: FileQuestion,
            }
    }
}

export default function ExperienceMatch({ experienceMatch }) {
    if (!experienceMatch) return null

    const {
        required_years,
        required_level,
        professional_years = 0,
        internship_years = 0,
        internship_entries = [],
        assessment,
        explanation,
        relevant_responsibilities = [],
        project_evidence = [],
        missing_information = [],
    } = experienceMatch

    const statusBadge = formatAssessmentStatus(assessment)
    const StatusIcon = statusBadge.icon

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border)] pb-4">
                <div>
                    <div className="flex items-center gap-2">
                        <Briefcase size={18} className="text-[var(--accent)]" />
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Experience Tenure & Relevance Assessment
                        </h3>
                    </div>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Professional tenure, internship experience, and relevant project evidence verified without assumptions.
                    </p>
                </div>

                {/* Status Badge */}
                <div
                    className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${statusBadge.className}`}
                >
                    <StatusIcon size={13} />
                    <span>{statusBadge.label}</span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                {/* Required Professional Tenure */}
                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/60 p-4">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] block mb-1">
                        Required Experience
                    </span>
                    <div className="text-xl font-bold text-[var(--text-primary)]">
                        {required_years !== null ? `${required_years} years` : 'Not Specified'}
                    </div>
                    {required_level && (
                        <span className="text-xs text-[var(--text-secondary)] mt-0.5 block">
                            Level: {required_level}
                        </span>
                    )}
                </div>

                {/* Verified Candidate Professional Tenure */}
                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/60 p-4">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] block mb-1">
                        Verified Employment
                    </span>
                    <div className="text-xl font-bold text-[var(--text-primary)]">
                        {professional_years > 0 ? `${professional_years.toFixed(1)} years` : '0.0 years'}
                    </div>
                    <span className="text-[11px] text-[var(--text-muted)] mt-0.5 block">
                        Full-time / regular employment
                    </span>
                </div>

                {/* Separate Internship Tenure */}
                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/60 p-4">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] block mb-1">
                        Internship Duration
                    </span>
                    <div className="text-xl font-bold text-[var(--accent)]">
                        {internship_years > 0 ? `${internship_years.toFixed(1)} years` : 'None Recorded'}
                    </div>
                    <span className="text-[11px] text-[var(--text-muted)] mt-0.5 block">
                        Assessed as supplemental portfolio
                    </span>
                </div>
            </div>

            {/* Narrative Explanation */}
            <div className="rounded-xl bg-[var(--surface-hover)]/40 p-4 text-xs text-[var(--text-secondary)] leading-relaxed">
                <strong className="font-semibold text-[var(--text-primary)] block mb-1">
                    Assessment Summary:
                </strong>
                {explanation}
            </div>

            {/* Strict Distinction Assurance */}
            <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-3 text-xs text-indigo-200">
                <span className="font-semibold block mb-0.5">
                    Defensible Evidence Standard:
                </span>
                Internship duration and project portfolios provide valuable evidence of technical competency, but are never combined into or counted as professional employment tenure.
            </div>

            {/* Relevant Responsibilities & Project Evidence */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {/* Responsibilities */}
                {relevant_responsibilities.length > 0 && (
                    <div className="space-y-2">
                        <span className="text-xs font-bold text-[var(--text-primary)] flex items-center gap-1.5">
                            <Clock size={14} className="text-blue-400" />
                            <span>Relevant Work Responsibilities ({relevant_responsibilities.length})</span>
                        </span>
                        <ul className="space-y-1.5">
                            {relevant_responsibilities.map((resp, idx) => (
                                <li
                                    key={idx}
                                    className="rounded-lg border border-[var(--border)] bg-[var(--surface-solid)]/70 p-2.5 text-xs text-[var(--text-secondary)] leading-relaxed"
                                >
                                    {resp}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Project Evidence */}
                {project_evidence.length > 0 && (
                    <div className="space-y-2">
                        <span className="text-xs font-bold text-[var(--text-primary)] flex items-center gap-1.5">
                            <FolderGit2 size={14} className="text-purple-400" />
                            <span>Verified Project Portfolio ({project_evidence.length})</span>
                        </span>
                        <ul className="space-y-2">
                            {project_evidence.map((proj, idx) => {
                                if (typeof proj === 'string') {
                                    return (
                                        <li
                                            key={idx}
                                            className="rounded-lg border border-[var(--border)] bg-[var(--surface-solid)]/70 p-2.5 text-xs text-[var(--text-secondary)] leading-relaxed"
                                        >
                                            {proj}
                                        </li>
                                    )
                                }

                                const name = proj.project_name || `Project ${idx + 1}`
                                const techs = Array.isArray(proj.technologies) ? proj.technologies : []
                                const relevantSkills = Array.isArray(proj.relevant_skills) ? proj.relevant_skills : []

                                return (
                                    <li
                                        key={idx}
                                        className="rounded-lg border border-[var(--border)] bg-[var(--surface-solid)]/70 p-3 text-xs text-[var(--text-secondary)] leading-relaxed space-y-1.5"
                                    >
                                        <div className="flex items-center justify-between gap-2">
                                            <span className="font-bold text-[var(--text-primary)]">
                                                {name}
                                            </span>
                                            <span className="rounded-full border border-purple-500/30 bg-purple-500/10 px-2 py-0.5 text-[10px] font-semibold text-purple-300">
                                                Portfolio Project
                                            </span>
                                        </div>

                                        {proj.relevance && (
                                            <p className="text-[11px] text-[var(--text-muted)]">
                                                {proj.relevance}
                                            </p>
                                        )}

                                        {relevantSkills.length > 0 && (
                                            <div className="flex flex-wrap items-center gap-1 text-[11px] pt-0.5">
                                                <span className="text-[var(--text-muted)]">Skills:</span>
                                                {relevantSkills.map((sk, skIdx) => (
                                                    <span
                                                        key={skIdx}
                                                        className="rounded bg-indigo-500/15 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-indigo-300"
                                                    >
                                                        {sk}
                                                    </span>
                                                ))}
                                            </div>
                                        )}

                                        {techs.length > 0 && (
                                            <div className="text-[10px] text-[var(--text-muted)] truncate" title={techs.join(', ')}>
                                                Stack: {techs.join(', ')}
                                            </div>
                                        )}
                                    </li>
                                )
                            })}
                        </ul>
                    </div>
                )}
            </div>

            {/* Separate Internship Roles (if any) */}
            {internship_entries.length > 0 && (
                <div className="space-y-2 pt-1 border-t border-[var(--border)]">
                    <span className="text-xs font-bold text-[var(--text-primary)] flex items-center gap-1.5">
                        <Briefcase size={14} className="text-indigo-400" />
                        <span>Identified Internship Experience ({internship_entries.length})</span>
                    </span>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                        {internship_entries.map((intern, idx) => (
                            <div
                                key={idx}
                                className="rounded-lg border border-[var(--border)] bg-[var(--surface-solid)]/70 p-2.5 text-xs text-[var(--text-secondary)] flex items-center justify-between"
                            >
                                <div>
                                    <strong className="text-[var(--text-primary)] block">{intern.job_title}</strong>
                                    {intern.company && <span className="text-[11px] text-[var(--text-muted)]">{intern.company}</span>}
                                </div>
                                {intern.duration_months && (
                                    <span className="rounded bg-[var(--surface-hover)] px-2 py-0.5 text-[10px] font-mono text-[var(--accent)] font-semibold">
                                        {intern.duration_months} mos
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Missing Information Callout */}
            {missing_information.length > 0 && (
                <div className="rounded-xl border border-amber-500/25 bg-amber-500/5 p-3.5 text-xs text-amber-200">
                    <span className="font-semibold block mb-1 flex items-center gap-1.5">
                        <AlertCircle size={14} className="text-amber-400" />
                        <span>Data Completeness Notes:</span>
                    </span>
                    <ul className="list-disc list-inside space-y-0.5 text-amber-300/80">
                        {missing_information.map((item, idx) => (
                            <li key={idx}>{item}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}
