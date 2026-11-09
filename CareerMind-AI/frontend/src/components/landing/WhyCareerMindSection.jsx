import { Eye, ShieldCheck, Crosshair } from 'lucide-react'

const VALUES = [
    {
        title: 'Understand Your Profile',
        description: 'Get structured insights from your resume instead of manually reviewing every detail.',
        icon: Eye,
        color: 'text-indigo-600 dark:text-indigo-400',
    },
    {
        title: 'Know Your Job Readiness',
        description: 'Understand which job requirements match your current profile.',
        icon: ShieldCheck,
        color: 'text-emerald-600 dark:text-emerald-400',
    },
    {
        title: 'Identify Improvement Areas',
        description: 'Get actionable insights into missing skills and experience gaps.',
        icon: Crosshair,
        color: 'text-purple-600 dark:text-purple-400',
    },
]

export default function WhyCareerMindSection() {
    return (
        <section id="why-careermind" className="py-20 sm:py-24 border-t border-[var(--border)] relative bg-[var(--surface-solid)]/30">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
                {/* Heading & Subtitle */}
                <div className="text-center space-y-3 max-w-2xl mx-auto">
                    <span className="text-xs font-bold uppercase tracking-wider text-[#6D28D9] dark:text-[#C4B5FD]">
                        Why CareerMind AI
                    </span>
                    <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-[#17172E] dark:text-[#F8FAFC]">
                        Make Career Decisions with Clarity
                    </h2>
                    <p className="text-sm sm:text-base text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed">
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
                                className="rounded-2xl p-7 border border-purple-200/80 dark:border-purple-800/40 bg-white/90 dark:bg-[#191333]/90 shadow-sm space-y-4 transition-all hover:border-[#8B5CF6]/50 hover:shadow-md"
                            >
                                <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 dark:bg-[#20183E] border border-purple-200/60 dark:border-purple-800/40 ${val.color}`}>
                                    <Icon size={22} />
                                </div>

                                <h3 className="text-base font-bold text-[#17172E] dark:text-[#F8FAFC]">
                                    {val.title}
                                </h3>

                                <p className="text-xs text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed">
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
