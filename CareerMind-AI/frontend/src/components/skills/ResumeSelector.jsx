import { Link } from 'react-router-dom'
import {
    FileText,
    CheckCircle2,
    Clock,
    AlertCircle,
    Star,
    UploadCloud,
} from 'lucide-react'

export default function ResumeSelector({
    resumes = [],
    selectedResumeId,
    onSelectResume,
    isLoading = false,
}) {
    if (isLoading) {
        return (
            <div className="space-y-2">
                <div className="h-4 w-32 bg-[var(--surface-hover)] rounded animate-pulse" />
                <div className="h-12 w-full bg-[var(--surface-hover)] rounded-xl animate-pulse" />
            </div>
        )
    }

    if (!resumes || resumes.length === 0) {
        return (
            <div className="rounded-xl border border-dashed border-[var(--border)] p-4 bg-[var(--surface)] text-center space-y-3">
                <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                    <FileText size={20} />
                </div>
                <div className="space-y-1">
                    <p className="text-sm font-semibold text-[var(--text-primary)]">
                        No resumes found in your library
                    </p>
                    <p className="text-xs text-[var(--text-muted)]">
                        Please upload and parse a resume first to evaluate skill gaps.
                    </p>
                </div>
                <Link
                    to="/resume"
                    className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--accent)] px-3 py-1.5 text-xs font-semibold text-white hover:opacity-90 transition-all"
                >
                    <UploadCloud size={13} />
                    <span>Upload Resume</span>
                </Link>
            </div>
        )
    }

    const completedResumes = resumes.filter((r) => r.parsing_status === 'completed')

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <label
                    htmlFor="resume-select"
                    className="block text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]"
                >
                    Select Resume
                </label>
                <Link
                    to="/resume"
                    className="text-xs font-medium text-[var(--accent)] hover:underline inline-flex items-center gap-1"
                >
                    <span>Manage Library</span>
                </Link>
            </div>

            <div className="relative">
                <select
                    id="resume-select"
                    value={selectedResumeId || ''}
                    onChange={(e) => onSelectResume(e.target.value)}
                    className="w-full appearance-none rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2.5 pr-10 text-sm font-medium text-[var(--text-primary)] shadow-sm transition-all focus:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/20 cursor-pointer"
                >
                    <option value="" disabled>
                        -- Choose a parsed resume --
                    </option>
                    {resumes.map((resume) => {
                        const isCompleted = resume.parsing_status === 'completed'
                        const labelParts = []
                        if (resume.display_name) {
                            labelParts.push(resume.display_name)
                        } else {
                            labelParts.push(resume.original_filename)
                        }
                        if (resume.is_default) {
                            labelParts.push('(Default)')
                        }
                        if (!isCompleted) {
                            labelParts.push(`[${resume.parsing_status}]`)
                        }

                        return (
                            <option
                                key={resume.id}
                                value={resume.id}
                                disabled={!isCompleted}
                            >
                                {labelParts.join(' ')}
                            </option>
                        )
                    })}
                </select>

                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-[var(--text-muted)]">
                    <FileText size={16} />
                </div>
            </div>

            {/* Selected Resume Status Indicator */}
            {selectedResumeId && (
                (() => {
                    const selected = resumes.find((r) => r.id === selectedResumeId)
                    if (!selected) return null
                    const isCompleted = selected.parsing_status === 'completed'

                    return (
                        <div className="flex items-center gap-2 text-xs pt-1">
                            {isCompleted ? (
                                <span className="inline-flex items-center gap-1 text-[var(--success)] font-medium">
                                    <CheckCircle2 size={13} />
                                    <span>Parsed & Ready</span>
                                </span>
                            ) : (
                                <span className="inline-flex items-center gap-1 text-[var(--warning)] font-medium">
                                    <Clock size={13} />
                                    <span>Status: {selected.parsing_status} (Cannot analyze unparsed resume)</span>
                                </span>
                            )}

                            {selected.is_default && (
                                <span className="inline-flex items-center gap-0.5 rounded bg-[var(--accent-soft)] px-1.5 py-0.5 text-[11px] font-semibold text-[var(--accent)]">
                                    <Star size={11} className="fill-[var(--accent)]" />
                                    <span>Default Resume</span>
                                </span>
                            )}
                        </div>
                    )
                })()
            )}

            {completedResumes.length === 0 && (
                <div className="flex items-center gap-1.5 rounded-lg border border-amber-500/20 bg-amber-500/10 p-2 text-xs text-amber-300">
                    <AlertCircle size={14} className="shrink-0" />
                    <span>None of your resumes have been parsed yet. Go to Resume Analyzer to parse a resume.</span>
                </div>
            )}
        </div>
    )
}

