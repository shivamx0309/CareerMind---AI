import { CheckCircle2, Loader2, Sparkles, Brain, Cpu, Database } from 'lucide-react'

export default function ResumeProcessing({ step = 'parsing' }) {
    const steps = [
        {
            id: 'upload',
            label: 'PDF Validation & Storage',
            desc: 'Validated cryptographic UUID and file boundaries',
            done: true,
            icon: CheckCircle2,
        },
        {
            id: 'extract',
            label: 'Text Extraction Engine',
            desc: 'Extracted semantic text streams and hyperlink metadata',
            done: true,
            icon: CheckCircle2,
        },
        {
            id: 'parse',
            label: 'Information Extraction & NLP Engine',
            desc: 'Categorizing skills, extracting education, work history and projects',
            done: step === 'completed',
            current: step === 'parsing',
            icon: step === 'completed' ? CheckCircle2 : Loader2,
        },
    ]

    return (
        <div className="glass-card space-y-8 p-6 sm:p-10">
            {/* Header animation */}
            <div className="flex flex-col items-center text-center">
                <div className="relative mb-5 flex h-20 w-20 items-center justify-center rounded-3xl bg-[var(--accent-soft)] text-[var(--accent)] shadow-xl">
                    <Brain size={40} className="animate-pulse" />
                    <div className="absolute -top-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full bg-[var(--accent)] text-white shadow-md">
                        <Sparkles size={16} />
                    </div>
                </div>

                <h3 className="text-xl font-bold tracking-tight text-[var(--text-primary)] sm:text-2xl">
                    Analyzing Your Resume Intelligence
                </h3>
                <p className="mt-2 max-w-md text-sm text-[var(--text-secondary)]">
                    CareerMind AI is parsing your profile, classifying technical skills into 10 domains, and structuring your career timeline.
                </p>
            </div>

            {/* Stepper progress */}
            <div className="mx-auto max-w-md space-y-4">
                {steps.map((s, index) => {
                    const Icon = s.icon
                    return (
                        <div
                            key={s.id}
                            className={`flex items-start gap-4 rounded-xl border p-4 transition-all ${
                                s.current
                                    ? 'border-[var(--accent)] bg-[var(--accent-soft)] shadow-md'
                                    : s.done
                                    ? 'border-[var(--success)]/30 bg-[var(--surface-solid)]'
                                    : 'border-[var(--border)] bg-[var(--surface)] opacity-50'
                            }`}
                        >
                            <div className="mt-0.5">
                                {s.current ? (
                                    <Icon
                                        size={22}
                                        className="animate-spin text-[var(--accent)]"
                                    />
                                ) : s.done ? (
                                    <Icon
                                        size={22}
                                        className="text-[var(--success)]"
                                    />
                                ) : (
                                    <div className="flex h-5 w-5 items-center justify-center rounded-full border border-[var(--border)] text-xs text-[var(--text-muted)]">
                                        {index + 1}
                                    </div>
                                )}
                            </div>

                            <div className="min-w-0 flex-1">
                                <p className="text-sm font-semibold text-[var(--text-primary)]">
                                    {s.label}
                                </p>
                                <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
                                    {s.desc}
                                </p>
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Skeleton preview cards */}
            <div className="space-y-4 pt-2">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                    <Cpu size={14} />
                    <span>Processing Engine Preview</span>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="space-y-3 rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-5">
                        <div className="h-4 w-1/3 animate-pulse rounded-md bg-[var(--surface-hover)]" />
                        <div className="h-3 w-3/4 animate-pulse rounded-md bg-[var(--surface-hover)]" />
                        <div className="h-3 w-1/2 animate-pulse rounded-md bg-[var(--surface-hover)]" />
                    </div>

                    <div className="space-y-3 rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-5">
                        <div className="flex items-center gap-2">
                            <Database size={16} className="text-[var(--accent)]" />
                            <div className="h-4 w-1/2 animate-pulse rounded-md bg-[var(--surface-hover)]" />
                        </div>
                        <div className="flex flex-wrap gap-2 pt-1">
                            <div className="h-6 w-16 animate-pulse rounded-lg bg-[var(--surface-hover)]" />
                            <div className="h-6 w-20 animate-pulse rounded-lg bg-[var(--surface-hover)]" />
                            <div className="h-6 w-14 animate-pulse rounded-lg bg-[var(--surface-hover)]" />
                            <div className="h-6 w-24 animate-pulse rounded-lg bg-[var(--surface-hover)]" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

