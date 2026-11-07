import { FolderGit2, ExternalLink, Code, Wrench } from 'lucide-react'
import { GithubIcon } from './BrandIcons'

export default function ProjectsSection({ projects }) {
    const entries = Array.isArray(projects) ? projects : []

    return (
        <div className="glass-card p-6 sm:p-8">
            <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <FolderGit2 size={20} />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Featured Projects & Portfolio
                        </h3>
                        <p className="text-xs text-[var(--text-muted)]">
                            Key software engineering and data applications
                        </p>
                    </div>
                </div>

                <span className="rounded-full bg-[var(--surface-hover)] px-2.5 py-1 text-xs font-semibold text-[var(--text-secondary)]">
                    {entries.length} {entries.length === 1 ? 'Project' : 'Projects'}
                </span>
            </div>

            {entries.length > 0 ? (
                <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                    {entries.map((project, idx) => {
                        const hasTech = Array.isArray(project.technologies) && project.technologies.length > 0
                        const isGitHub = project.project_url && project.project_url.includes('github.com')

                        return (
                            <div
                                key={idx}
                                className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 transition-all hover:border-[var(--accent)]/50 hover:shadow-md"
                            >
                                <div>
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="flex items-center gap-2">
                                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--accent-soft)] text-[var(--accent)]">
                                                <Code size={16} />
                                            </div>
                                            <h4 className="text-base font-bold text-[var(--text-primary)]">
                                                {project.project_name || `Project #${idx + 1}`}
                                            </h4>
                                        </div>

                                        {project.project_url && (
                                            <a
                                                href={project.project_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface-hover)] px-2.5 py-1 text-xs font-medium text-[var(--text-primary)] transition-all hover:border-[var(--accent)] hover:text-[var(--accent)]"
                                            >
                                                {isGitHub ? <GithubIcon size={13} /> : <ExternalLink size={13} />}
                                                <span>{isGitHub ? 'Repository' : 'View Demo'}</span>
                                            </a>
                                        )}
                                    </div>

                                    {/* Description */}
                                    {project.description && (
                                        <div className="mt-3.5 space-y-1.5 text-xs sm:text-sm leading-relaxed text-[var(--text-secondary)]">
                                            {project.description.split('\n').map((line, lIdx) => (
                                                <p key={lIdx} className="whitespace-pre-line">
                                                    {line}
                                                </p>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Tech stack tags */}
                                {hasTech && (
                                    <div className="mt-4 pt-3 border-t border-[var(--border)]">
                                        <div className="flex flex-wrap items-center gap-1.5">
                                            <Wrench size={12} className="text-[var(--text-muted)] mr-1" />
                                            {project.technologies.map((tech) => (
                                                <span
                                                    key={tech}
                                                    className="rounded-md border border-[var(--border)] bg-[var(--surface)] px-2 py-0.5 text-xs font-medium text-[var(--text-primary)]"
                                                >
                                                    {tech}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            ) : (
                <div className="rounded-xl border border-dashed border-[var(--border)] p-6 text-center text-sm text-[var(--text-muted)]">
                    No individual projects detected in this resume.
                </div>
            )}
        </div>
    )
}
