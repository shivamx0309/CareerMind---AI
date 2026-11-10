import { Award, Calendar, FileText, AlertTriangle, Info } from 'lucide-react'

export default function OverallSkillScore({ report }) {
    if (!report) return null

    const {
        overall_score,
        analysis_status,
        role_title,
        target_role,
        benchmark_version,
        resume_name,
        created_at,
    } = report

    // Format creation date
    const formattedDate = created_at
        ? new Date(created_at).toLocaleDateString(undefined, {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
          })
        : 'Recent'

    // Status message & colors
    let scoreDisplay = overall_score !== null && overall_score !== undefined ? `${overall_score}%` : 'N/A'
    let statusLabel = 'Analysis Complete'
    let statusBadgeClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'

    if (analysis_status === 'no_candidate_skills') {
        scoreDisplay = '0.0%'
        statusLabel = 'No Candidate Skills Evidenced'
        statusBadgeClass = 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    } else if (analysis_status === 'insufficient_benchmark') {
        scoreDisplay = 'N/A'
        statusLabel = 'Insufficient Benchmark Skills'
        statusBadgeClass = 'bg-slate-500/10 text-slate-400 border-slate-500/20'
    }

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-7 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="space-y-1.5">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${statusBadgeClass}`}>
                            <Award size={12} />
                            <span>{statusLabel}</span>
                        </span>
                        <span className="text-xs text-[var(--text-muted)]">
                            Benchmark v{benchmark_version || '1.0.0'}
                        </span>
                    </div>

                    <h2 className="text-2xl sm:text-3xl font-extrabold text-[var(--text-primary)]">
                        {role_title || target_role}
                    </h2>

                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[var(--text-secondary)]">
                        <span className="inline-flex items-center gap-1">
                            <FileText size={13} className="text-[var(--accent)]" />
                            <span>Resume: <strong>{resume_name || 'Active Candidate Profile'}</strong></span>
                        </span>
                        <span className="inline-flex items-center gap-1 text-[var(--text-muted)]">
                            <Calendar size={13} />
                            <span>{formattedDate}</span>
                        </span>
                    </div>
                </div>

                {/* Score Number Display */}
                <div className="shrink-0 flex items-center sm:flex-col sm:items-end justify-between sm:justify-center p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-[var(--surface-solid)] to-[var(--surface-hover)] border border-[var(--border)] shadow-sm min-w-[150px]">
                    <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                        Overall Match
                    </span>
                    <div className="text-3xl sm:text-4xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)]">
                        {scoreDisplay}
                    </div>
                    <span className="text-[11px] text-[var(--text-muted)] font-medium">
                        Role Benchmark Coverage
                    </span>
                </div>
            </div>

            {/* Explanatory Boundary Warning if applicable */}
            {analysis_status === 'no_candidate_skills' && (
                <div className="flex items-start gap-2.5 rounded-xl border border-amber-500/20 bg-amber-500/10 p-3.5 text-xs text-amber-300">
                    <AlertTriangle size={16} className="shrink-0 mt-0.5 text-amber-400" />
                    <div>
                        <strong>No detectable technical skills found:</strong> The parser could not detect technical competency keywords in this resume. Consider updating the resume with clear skill and tool designations.
                    </div>
                </div>
            )}

            {/* Disclaimer Footnote */}
            <div className="flex items-center gap-2 pt-2 border-t border-[var(--border)]/50 text-[11px] text-[var(--text-muted)]">
                <Info size={13} className="shrink-0 text-[var(--accent)]" />
                <span>
                    This benchmark score represents deterministic curriculum coverage of expected core skills. It does not reflect a hiring probability, interview outcome, or guarantee.
                </span>
            </div>
        </div>
    )
}
