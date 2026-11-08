import { UserPlus, FileUp, FileCheck2, TrendingUp, CheckCircle2, Clock } from 'lucide-react'

const STEPS = [
    {
        number: '01',
        title: 'Create Your Career Profile',
        description: 'Register your basic career information and define your professional goals.',
        icon: UserPlus,
        status: 'Available',
        statusText: 'Active in Onboarding',
    },
    {
        number: '02',
        title: 'Analyze Your Resume',
        description: 'Upload your resume and let CareerMind AI extract your professional profile.',
        icon: FileUp,
        status: 'Available',
        statusText: 'Active in Resume Analyzer',
    },
    {
        number: '03',
        title: 'Match Your Dream Job',
        description: 'Compare your resume with a job description to understand your strengths and gaps.',
        icon: FileCheck2,
        status: 'Available',
        statusText: 'Active in Job Matcher',
    },
    {
        number: '04',
        title: 'Improve and Prepare',
        description: 'Use recommendations and future learning tools to improve your career readiness.',
        icon: TrendingUp,
        status: 'Planned',
        statusText: 'Future Roadmap',
    },
]

export default function HowItWorksSection() {
    return (
        <section id="how-it-works" className="py-20 sm:py-24 border-t border-[var(--border)] relative">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
                {/* Heading & Subtitle */}
                <div className="text-center space-y-3 max-w-2xl mx-auto">
                    <span className="text-xs font-bold uppercase tracking-wider text-[var(--accent)]">
                        Step-by-Step Workflow
                    </span>
                    <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-[var(--text-primary)]">
                        Your Career Journey, Simplified
                    </h2>
                    <p className="text-sm sm:text-base text-[var(--text-secondary)] leading-relaxed">
                        A transparent, explainable pathway from profile registration to job alignment and preparation.
                    </p>
                </div>

                {/* Desktop Connected Horizontal Timeline */}
                <div className="hidden md:block relative pt-4">
                    {/* Horizontal Connector Line */}
                    <div className="absolute top-10 left-[12%] right-[12%] h-0.5 bg-gradient-to-r from-[var(--accent)] via-[var(--accent-secondary)] to-[var(--border)] -z-0" />

                    <div className="grid grid-cols-4 gap-6 relative z-10">
                        {STEPS.map((step) => {
                            const Icon = step.icon
                            const isAvailable = step.status === 'Available'

                            return (
                                <div key={step.number} className="flex flex-col items-center text-center space-y-3.5">
                                    {/* Number / Icon Bubble */}
                                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border-2 border-[var(--border)] bg-[var(--surface-solid)] shadow-md text-sm font-bold text-[var(--text-primary)] transition-transform hover:scale-105">
                                        <Icon size={20} className={isAvailable ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'} />
                                    </div>

                                    {/* Step Title */}
                                    <div className="space-y-1">
                                        <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--accent)]">
                                            Step {step.number}
                                        </span>
                                        <h3 className="text-sm font-bold text-[var(--text-primary)]">
                                            {step.title}
                                        </h3>
                                    </div>

                                    {/* Step Description */}
                                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                                        {step.description}
                                    </p>

                                    {/* Availability Tag */}
                                    <span
                                        className={`inline-flex items-center gap-1 text-[10px] font-semibold rounded-full px-2 py-0.5 border ${
                                            isAvailable
                                                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                                                : 'border-slate-600/30 bg-slate-800/30 text-slate-400'
                                        }`}
                                    >
                                        {isAvailable ? <CheckCircle2 size={10} /> : <Clock size={10} />}
                                        <span>{step.statusText}</span>
                                    </span>
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* Mobile Connected Vertical Timeline */}
                <div className="md:hidden relative pl-6 space-y-8">
                    {/* Vertical Connector Line */}
                    <div className="absolute top-4 bottom-4 left-2.5 w-0.5 bg-gradient-to-b from-[var(--accent)] via-[var(--accent-secondary)] to-[var(--border)]" />

                    {STEPS.map((step) => {
                        const Icon = step.icon
                        const isAvailable = step.status === 'Available'

                        return (
                            <div key={step.number} className="relative flex items-start gap-4">
                                {/* Timeline Dot / Bubble */}
                                <div className="absolute -left-6 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface-solid)] text-[10px] font-bold text-[var(--accent)]">
                                    {step.number}
                                </div>

                                <div className="glass-card rounded-xl p-4 border border-[var(--border)] flex-1 space-y-2">
                                    <div className="flex items-center justify-between gap-2">
                                        <div className="flex items-center gap-2">
                                            <Icon size={16} className={isAvailable ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'} />
                                            <h3 className="text-sm font-bold text-[var(--text-primary)]">
                                                {step.title}
                                            </h3>
                                        </div>
                                        <span
                                            className={`text-[9px] font-semibold rounded-full px-2 py-0.5 border shrink-0 ${
                                                isAvailable
                                                    ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                                                    : 'border-slate-600/30 bg-slate-800/30 text-slate-400'
                                            }`}
                                        >
                                            {step.statusText}
                                        </span>
                                    </div>
                                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                                        {step.description}
                                    </p>
                                </div>
                            </div>
                        )
                    })}
                </div>
            </div>
        </section>
    )
}

