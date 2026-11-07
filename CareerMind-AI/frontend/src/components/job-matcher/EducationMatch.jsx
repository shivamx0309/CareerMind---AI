import {
    GraduationCap,
    CheckCircle2,
    AlertCircle,
    Info,
} from 'lucide-react'

function formatEduStatus(status) {
    switch (status) {
        case 'exact_match':
            return {
                label: 'Exact Degree Match',
                className: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
                icon: CheckCircle2,
            }
        case 'related_match':
            return {
                label: 'Related Field Match',
                className: 'border-sky-500/30 bg-sky-500/10 text-sky-400',
                icon: CheckCircle2,
            }
        case 'missing':
            return {
                label: 'Missing Degree Requirement',
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
                label: 'Degree Level Unspecified',
                className: 'border-slate-500/30 bg-slate-500/10 text-slate-300',
                icon: AlertCircle,
            }
    }
}

export default function EducationMatch({ educationMatch }) {
    if (!educationMatch) return null

    const {
        required_degree,
        required_fields = [],
        candidate_degree,
        candidate_field,
        status,
        explanation,
    } = educationMatch

    const statusBadge = formatEduStatus(status)
    const StatusIcon = statusBadge.icon

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border)] pb-4">
                <div>
                    <div className="flex items-center gap-2">
                        <GraduationCap size={18} className="text-emerald-400" />
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Education Alignment
                        </h3>
                    </div>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Comparison of required degree credentials and acceptable fields of study.
                    </p>
                </div>

                <div
                    className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${statusBadge.className}`}
                >
                    <StatusIcon size={13} />
                    <span>{statusBadge.label}</span>
                </div>
            </div>

            {/* Comparison Grid */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {/* JD Expected Degree */}
                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/60 p-4 space-y-2">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] block">
                        Target JD Requirements
                    </span>
                    <div className="space-y-1">
                        <div className="text-sm font-bold text-[var(--text-primary)]">
                            {required_degree ? `${required_degree} Degree` : 'No Degree Specified'}
                        </div>
                        {required_fields.length > 0 && (
                            <div className="text-xs text-[var(--text-secondary)]">
                                Fields: <span className="font-medium text-[var(--text-primary)]">{required_fields.join(', ')}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Candidate Degree Found */}
                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/60 p-4 space-y-2">
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] block">
                        Verified Candidate Credential
                    </span>
                    <div className="space-y-1">
                        <div className="text-sm font-bold text-emerald-400">
                            {candidate_degree || 'No Degree Detected'}
                        </div>
                        {candidate_field && (
                            <div className="text-xs text-[var(--text-secondary)]">
                                Major/Branch: <span className="font-medium text-[var(--text-primary)]">{candidate_field}</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Narrative Explanation */}
            {explanation && (
                <div className="rounded-xl bg-[var(--surface-hover)]/40 p-4 text-xs text-[var(--text-secondary)] leading-relaxed">
                    <strong className="font-semibold text-[var(--text-primary)] block mb-1">
                        Evaluation:
                    </strong>
                    {explanation}
                </div>
            )}
        </div>
    )
}
