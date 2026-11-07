import {
    Award,
    CheckCircle2,
    AlertTriangle,
    Info,
    HelpCircle,
    Scale,
    TrendingUp,
} from 'lucide-react'

/**
 * Determine classification color palette.
 */
function getClassificationTheme(classification) {
    switch (classification) {
        case 'Strong Match':
            return {
                bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
                badgeBg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
                ringColor: '#10b981',
                textColor: 'text-emerald-400',
            }
        case 'Moderate Match':
            return {
                bg: 'bg-sky-500/10 border-sky-500/30 text-sky-400',
                badgeBg: 'bg-sky-500/20 text-sky-300 border-sky-500/40',
                ringColor: '#0ea5e9',
                textColor: 'text-sky-400',
            }
        case 'Partial Match':
            return {
                bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
                badgeBg: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
                ringColor: '#f59e0b',
                textColor: 'text-amber-400',
            }
        case 'Low Match':
            return {
                bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
                badgeBg: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
                ringColor: '#f43f5e',
                textColor: 'text-rose-400',
            }
        default: // 'Not assessable'
            return {
                bg: 'bg-slate-500/10 border-slate-500/30 text-slate-400',
                badgeBg: 'bg-slate-500/20 text-slate-300 border-slate-500/40',
                ringColor: '#64748b',
                textColor: 'text-slate-400',
            }
    }
}

export default function MatchScoreCard({
    matchScore,
    overallScore,
    matchClassification,
    targetTitle,
    targetCompany,
}) {
    const isUnassessable = overallScore === null || matchClassification === 'Not assessable'
    const classification = matchClassification || matchScore?.match_classification || 'Not assessable'
    const scoreValue = overallScore !== null && overallScore !== undefined ? overallScore : matchScore?.overall_score
    const explanation = matchScore?.explanation || 'Evaluation completed based on available criteria.'
    const weightNormalization = matchScore?.weight_normalization_applied || false

    const theme = getClassificationTheme(classification)

    // Calculate circular SVG progress stroke
    const radius = 54
    const circumference = 2 * Math.PI * radius
    const progressOffset = isUnassessable
        ? circumference
        : circumference - ((scoreValue || 0) / 100) * circumference

    return (
        <div className="glass-card relative overflow-hidden rounded-2xl p-6 sm:p-8">
            {/* Ambient Background Aura */}
            <div
                className={`pointer-events-none absolute -top-20 -right-20 h-64 w-64 rounded-full blur-3xl opacity-20 ${
                    isUnassessable
                        ? 'bg-slate-500'
                        : classification === 'Strong Match'
                        ? 'bg-emerald-500'
                        : classification === 'Moderate Match'
                        ? 'bg-sky-500'
                        : classification === 'Partial Match'
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                }`}
            />

            <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                {/* Left Side: Score Context and Narrative */}
                <div className="space-y-3 max-w-xl">
                    <div className="flex flex-wrap items-center gap-2.5">
                        <span className="text-xs font-semibold uppercase tracking-wider text-[var(--accent)] flex items-center gap-1.5">
                            <Award size={14} />
                            <span>Match Analysis Report</span>
                        </span>

                        <span
                            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-0.5 text-xs font-bold ${theme.badgeBg}`}
                        >
                            {isUnassessable ? (
                                <HelpCircle size={13} />
                            ) : classification === 'Strong Match' ? (
                                <CheckCircle2 size={13} />
                            ) : (
                                <TrendingUp size={13} />
                            )}
                            <span>{classification}</span>
                        </span>

                        {weightNormalization && (
                            <span
                                title="Unassessed criteria were safely excluded and available weights re-normalized to 100%"
                                className="inline-flex items-center gap-1 rounded-full border border-purple-500/30 bg-purple-500/10 px-2.5 py-0.5 text-[11px] font-medium text-purple-300"
                            >
                                <Scale size={11} />
                                <span>Normalized Weights</span>
                            </span>
                        )}
                    </div>

                    <div>
                        <h2 className="text-2xl font-bold tracking-tight text-[var(--text-primary)] sm:text-3xl">
                            {targetTitle || 'Target Position'}
                            {targetCompany ? (
                                <span className="text-[var(--text-secondary)] font-normal text-xl sm:text-2xl">
                                    {' '}at {targetCompany}
                                </span>
                            ) : null}
                        </h2>
                    </div>

                    {/* Score Narrative */}
                    <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                        {explanation}
                    </p>

                    {/* Unassessable Warning Note */}
                    {isUnassessable && (
                        <div className="flex items-start gap-2.5 rounded-xl border border-slate-500/30 bg-slate-500/10 p-3 text-xs text-slate-300">
                            <Info size={16} className="mt-0.5 shrink-0 text-slate-400" />
                            <span>
                                The candidate profile or job description lacked verifiable criteria across all scoring dimensions.
                                No automatic zeros or speculative scores were awarded.
                            </span>
                        </div>
                    )}
                </div>

                {/* Right Side: Score Gauge or Unassessable Box */}
                <div className="flex flex-col items-center justify-center shrink-0 self-center">
                    {isUnassessable ? (
                        <div className="flex flex-col items-center justify-center w-36 h-36 rounded-2xl border border-dashed border-slate-600 bg-slate-900/40 p-4 text-center">
                            <AlertTriangle size={32} className="text-slate-400 mb-2" />
                            <span className="text-xs font-bold text-slate-300">Not Assessable</span>
                            <span className="text-[10px] text-slate-400 mt-1">Insufficient Data</span>
                        </div>
                    ) : (
                        <div className="relative flex items-center justify-center">
                            <svg className="w-36 h-36 transform -rotate-90" viewBox="0 0 128 128">
                                {/* Background circle track */}
                                <circle
                                    cx="64"
                                    cy="64"
                                    r={radius}
                                    stroke="currentColor"
                                    strokeWidth="10"
                                    fill="transparent"
                                    className="text-[var(--surface-hover)]"
                                />
                                {/* Animated score fill */}
                                <circle
                                    cx="64"
                                    cy="64"
                                    r={radius}
                                    stroke={theme.ringColor}
                                    strokeWidth="10"
                                    strokeDasharray={circumference}
                                    strokeDashoffset={progressOffset}
                                    strokeLinecap="round"
                                    fill="transparent"
                                    className="transition-all duration-1000 ease-out"
                                />
                            </svg>

                            {/* Center Score Text */}
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                                <span className="text-3xl font-extrabold text-[var(--text-primary)] tracking-tight">
                                    {Math.round(scoreValue)}%
                                </span>
                                <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] mt-0.5">
                                    Match Score
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

