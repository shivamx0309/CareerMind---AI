import { FileText, Sparkles } from 'lucide-react'

export default function ProfessionalSummary({ summary }) {
    return (
        <div className="glass-card p-6 sm:p-8">
            <div className="mb-4 flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                    <Sparkles size={18} />
                </div>
                <div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)]">
                        Professional Summary
                    </h3>
                    <p className="text-xs text-[var(--text-muted)]">
                        Extracted candidate overview and career objective
                    </p>
                </div>
            </div>

            {summary ? (
                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 sm:p-5">
                    <p className="whitespace-pre-line text-sm leading-relaxed text-[var(--text-secondary)]">
                        {summary}
                    </p>
                </div>
            ) : (
                <div className="flex items-center gap-3 rounded-xl border border-dashed border-[var(--border)] p-6 text-center text-sm text-[var(--text-muted)]">
                    <FileText size={20} className="mx-auto text-[var(--text-muted)]" />
                    <span>No professional summary or objective statement was detected in this resume.</span>
                </div>
            )}
        </div>
    )
}

