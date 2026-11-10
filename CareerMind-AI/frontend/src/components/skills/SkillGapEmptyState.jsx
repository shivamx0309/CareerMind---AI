import { ChartNoAxesCombined, Sparkles, ShieldCheck, Target, CheckCircle2 } from 'lucide-react'

export default function SkillGapEmptyState() {
    return (
        <div className="glass-card rounded-2xl p-8 sm:p-12 text-center space-y-6">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)]">
                <ChartNoAxesCombined size={32} />
            </div>

            <div className="max-w-md mx-auto space-y-2">
                <h3 className="text-xl sm:text-2xl font-extrabold text-[var(--text-primary)]">
                    Evaluate Your Role Competency Gaps
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                    Compare verified skills from your parsed resume directly against standardized industry career benchmarks—no job description required.
                </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-xl mx-auto pt-2 text-left">
                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3.5 space-y-1">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-[var(--accent)]">
                        <Target size={14} />
                        <span>8 Standard Roles</span>
                    </div>
                    <p className="text-[11px] text-[var(--text-muted)]">
                        Curated benchmarks for SDE, Frontend, Backend, Data, ML & Python roles.
                    </p>
                </div>

                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3.5 space-y-1">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-amber-500 dark:text-amber-400">
                        <Sparkles size={14} />
                        <span>Related Credit</span>
                    </div>
                    <p className="text-[11px] text-[var(--text-muted)]">
                        Transferable skills earn 60% partial credit toward your overall readiness.
                    </p>
                </div>

                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3.5 space-y-1">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-500">
                        <CheckCircle2 size={14} />
                        <span>Deterministic</span>
                    </div>
                    <p className="text-[11px] text-[var(--text-muted)]">
                        Transparent mathematical scoring. Zero hallucinations or paid external APIs.
                    </p>
                </div>
            </div>

            <div className="flex items-center justify-center gap-2 pt-2 text-xs text-[var(--text-muted)]">
                <ShieldCheck size={14} className="text-[var(--success)]" />
                <span>Local SQLite persistence. Your career data remains private on your machine.</span>
            </div>
        </div>
    )
}
