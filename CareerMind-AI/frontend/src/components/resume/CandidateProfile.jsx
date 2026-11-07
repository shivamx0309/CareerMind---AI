import {
    Mail,
    Phone,
    Globe,
    MapPin,
    Edit3,
    FileUp,
    Copy,
    Check,
    BriefcaseBusiness,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { LinkedinIcon, GithubIcon } from './BrandIcons'
import { useState } from 'react'

export default function CandidateProfile({
    personalInfo,
    fileId,
    isEdited,
    onEdit,
    onUploadAnother,
}) {
    const [copied, setCopied] = useState(false)

    const {
        full_name,
        email,
        phone,
        linkedin,
        github,
        portfolio,
        location,
    } = personalInfo || {}

    function getInitials(name) {
        if (!name) return 'CM'
        const parts = name.trim().split(/\s+/)
        if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }

    async function copyFileId() {
        if (!fileId) return
        try {
            await navigator.clipboard.writeText(fileId)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch {
            // ignore clipboard errors
        }
    }

    return (
        <div className="glass-card relative overflow-hidden p-6 sm:p-8">
            {/* Background ambient gradient */}
            <div className="pointer-events-none absolute -top-24 -right-24 h-64 w-64 rounded-full bg-gradient-to-br from-[var(--accent)]/15 to-[var(--accent-secondary)]/10 blur-3xl" />

            <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
                {/* Left: Avatar & primary info */}
                <div className="flex items-start gap-5">
                    <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-tr from-[var(--accent)] to-[var(--accent-secondary)] text-xl font-bold text-white shadow-lg shadow-indigo-500/20 sm:h-20 sm:w-20 sm:text-2xl">
                        {getInitials(full_name)}
                    </div>

                    <div className="space-y-1.5">
                        <div className="flex flex-wrap items-center gap-2">
                            <h2 className="text-2xl font-bold tracking-tight text-[var(--text-primary)] sm:text-3xl">
                                {full_name || 'Candidate Name'}
                            </h2>

                            {isEdited && (
                                <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-500/10 px-2.5 py-0.5 text-xs font-medium text-amber-400">
                                    Edited in session
                                </span>
                            )}
                        </div>

                        {location ? (
                            <p className="flex items-center gap-1.5 text-sm text-[var(--text-secondary)]">
                                <MapPin size={16} className="text-[var(--accent)]" />
                                <span>{location}</span>
                            </p>
                        ) : (
                            <p className="text-xs text-[var(--text-muted)] italic">
                                Location not detected
                            </p>
                        )}

                        {fileId && (
                            <div className="flex items-center gap-2 pt-1 text-xs text-[var(--text-muted)]">
                                <span className="font-mono">ID: {fileId.slice(0, 8)}...{fileId.slice(-6)}</span>
                                <button
                                    type="button"
                                    onClick={copyFileId}
                                    title="Copy full file ID"
                                    className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)]"
                                >
                                    {copied ? (
                                        <>
                                            <Check size={12} className="text-[var(--success)]" />
                                            <span className="text-[var(--success)]">Copied</span>
                                        </>
                                    ) : (
                                        <Copy size={12} />
                                    )}
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Actions */}
                <div className="flex flex-wrap items-center gap-3">
                    <Link
                        to="/jobs"
                        className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-500/20 transition-all hover:opacity-95"
                    >
                        <BriefcaseBusiness size={16} />
                        <span>Match with Jobs</span>
                    </Link>

                    <button
                        type="button"
                        onClick={onEdit}
                        className="inline-flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] shadow-sm transition-all hover:border-[var(--accent)] hover:bg-[var(--surface-hover)]"
                    >
                        <Edit3 size={16} className="text-[var(--accent)]" />
                        <span>Edit Profile</span>
                    </button>

                    <button
                        type="button"
                        onClick={onUploadAnother}
                        className="inline-flex items-center gap-2 rounded-xl border border-transparent bg-[var(--surface-hover)] px-4 py-2.5 text-sm font-medium text-[var(--text-secondary)] transition-all hover:bg-[var(--accent-soft)] hover:text-[var(--accent)]"
                    >
                        <FileUp size={16} />
                        <span>Upload Another</span>
                    </button>
                </div>
            </div>

            {/* Contact links ribbon */}
            <div className="mt-6 grid grid-cols-1 gap-3 border-t border-[var(--border)] pt-6 sm:grid-cols-2 lg:grid-cols-4">
                {/* Email */}
                {email ? (
                    <a
                        href={`mailto:${email}`}
                        className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 text-sm text-[var(--text-primary)] transition-all hover:border-[var(--accent)] hover:bg-[var(--surface-hover)]"
                    >
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--accent-soft)] text-[var(--accent)]">
                            <Mail size={16} />
                        </div>
                        <span className="truncate">{email}</span>
                    </a>
                ) : (
                    <div className="flex items-center gap-3 rounded-xl border border-[var(--border)]/50 bg-[var(--surface)] p-3 text-xs text-[var(--text-muted)]">
                        <Mail size={16} className="shrink-0" />
                        <span>Email not detected</span>
                    </div>
                )}

                {/* Phone */}
                {phone ? (
                    <a
                        href={`tel:${phone}`}
                        className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 text-sm text-[var(--text-primary)] transition-all hover:border-[var(--accent)] hover:bg-[var(--surface-hover)]"
                    >
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--accent-soft)] text-[var(--accent)]">
                            <Phone size={16} />
                        </div>
                        <span className="truncate">{phone}</span>
                    </a>
                ) : (
                    <div className="flex items-center gap-3 rounded-xl border border-[var(--border)]/50 bg-[var(--surface)] p-3 text-xs text-[var(--text-muted)]">
                        <Phone size={16} className="shrink-0" />
                        <span>Phone not detected</span>
                    </div>
                )}

                {/* LinkedIn */}
                {linkedin ? (
                    <a
                        href={linkedin}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 text-sm text-[var(--text-primary)] transition-all hover:border-[var(--accent)] hover:bg-[var(--surface-hover)]"
                    >
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-500/15 text-blue-400">
                            <LinkedinIcon size={16} />
                        </div>
                        <span className="truncate">LinkedIn Profile</span>
                    </a>
                ) : (
                    <div className="flex items-center gap-3 rounded-xl border border-[var(--border)]/50 bg-[var(--surface)] p-3 text-xs text-[var(--text-muted)]">
                        <LinkedinIcon size={16} className="shrink-0" />
                        <span>LinkedIn not detected</span>
                    </div>
                )}

                {/* GitHub */}
                {github ? (
                    <a
                        href={github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 text-sm text-[var(--text-primary)] transition-all hover:border-[var(--accent)] hover:bg-[var(--surface-hover)]"
                    >
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-purple-500/15 text-purple-400">
                            <GithubIcon size={16} />
                        </div>
                        <span className="truncate">GitHub Profile</span>
                    </a>
                ) : (
                    <div className="flex items-center gap-3 rounded-xl border border-[var(--border)]/50 bg-[var(--surface)] p-3 text-xs text-[var(--text-muted)]">
                        <GithubIcon size={16} className="shrink-0" />
                        <span>GitHub not detected</span>
                    </div>
                )}
            </div>

            {/* Optional Portfolio URL */}
            {portfolio && (
                <div className="mt-3">
                    <a
                        href={portfolio}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-1.5 text-xs text-[var(--accent)] transition-all hover:bg-[var(--surface-hover)]"
                    >
                        <Globe size={14} />
                        <span className="truncate font-medium">{portfolio}</span>
                    </a>
                </div>
            )}
        </div>
    )
}
