import { Eye, ShieldCheck, Crosshair } from 'lucide-react'

const VALUES = [
    {
        title: 'Understand Your Profile',
        description: 'Get structured insights from your resume instead of manually reviewing every detail.',
        icon: Eye,
        color: 'text-indigo-400',
    },
    {
        title: 'Know Your Job Readiness',
        description: 'Understand which job requirements match your current profile.',
        icon: ShieldCheck,
        color: 'text-emerald-400',
    },
    {
        title: 'Identify Improvement Areas',
        description: 'Get actionable insights into missing skills and experience gaps.',
        icon: Crosshair,
        color: 'text-blue-400',
    },
]

export default function WhyCareerMindSection() {
    return (
        <section className="py-20 sm:py-24 border-t border-[var(--border)] relative bg-[var(--surface-solid)]/30">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
                {/* Heading & Subtitle */}
                <div className="text-center space-y-3 max-w-2xl mx-auto">
                    <span className="text-xs font-bold uppercase tracking-wider text-[var(--accent)]">
                        Why CareerMind AI
                    </span>
                    <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-[var(--text-primary)]">
                        Make Career Decisions with Clarity
                    </h2>
                    <p className="text-sm sm:text-base text-[var(--text-secondary)] leading-relaxed">
                        Defensible intelligence designed to give you transparent feedback without ungrounded assumptions or exaggerated promises.
                    </p>
                </div>

                {/* 3 Value Propositions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {VALUES.map((val) => {
                        const Icon = val.icon

                        return (
                            <div
                                key={val.title}
                                className="glass-card rounded-2xl p-7 border border-[var(--border)] space-y-4 transition-all hover:border-[var(--accent)]/30"
                            >
                                <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--surface-solid)] border border-[var(--border)] ${val.color}`}>
                                    <Icon size={22} />
                                </div>

                                <h3 className="text-base font-bold text-[var(--text-primary)]">
                                    {val.title}
                                </h3>

                                <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                                    {val.description}
                                </p>
                            </div>
                        )
                    })}
                </div>
            </div>
        </section>
    )
}

