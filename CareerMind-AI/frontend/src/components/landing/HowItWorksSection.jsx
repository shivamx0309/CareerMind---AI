import { FileSearch, Briefcase, Target, GraduationCap, CheckCircle2 } from 'lucide-react'

const STEPS = [
    {
        number: '01',
        title: 'Analyze Your Resume',
        description: 'Extract your skills, education, experience and projects from your resume.',
        icon: FileSearch,
        status: 'Available',
        statusText: 'Available',
    },
    {
        number: '02',
        title: 'Match Your Dream Job',
        description: 'Compare your resume with job descriptions and discover your skill matches and missing requirements.',
        icon: Briefcase,
        status: 'Available',
        statusText: 'Available',
    },
    {
        number: '03',
        title: 'Identify Your Skill Gaps',
        description: 'Understand which skills you already demonstrate and which skills you need to develop for your target role.',
        icon: Target,
        status: 'Available',
        statusText: 'Available',
    },
    {
        number: '04',
        title: 'Learn & Practice',
        description: 'Follow a personalized learning roadmap and practice with structured mock interviews.',
        icon: GraduationCap,
        status: 'Available',
        statusText: 'Available',
    },
]

export default function HowItWorksSection() {
    return (
        <section id="how-it-works" className="py-20 sm:py-24 border-t border-purple-200/60 dark:border-purple-900/30 relative">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
                {/* Heading & Subtitle */}
                <div className="text-center space-y-3 max-w-2xl mx-auto">
                    <span className="text-xs font-bold uppercase tracking-wider text-[#6D28D9] dark:text-[#C4B5FD]">
                        Step-by-Step Workflow
                    </span>
                    <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-[#17172E] dark:text-[#F8FAFC]">
                        Your Career Journey, Simplified
                    </h2>
                    <p className="text-sm sm:text-base text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed">
                        From understanding your resume to preparing for interviews, everything you need to become job-ready in one place.
                    </p>
                </div>

                {/* Desktop Connected Horizontal Timeline */}
                <div className="hidden md:block relative pt-4">
                    {/* Horizontal Connector Line */}
                    <div className="absolute top-10 left-[12%] right-[12%] h-0.5 bg-gradient-to-r from-[#6D28D9] via-[#8B5CF6] to-[#A78BFA] dark:to-purple-900/50 -z-0" />

                    <div className="grid grid-cols-4 gap-6 relative z-10">
                        {STEPS.map((step) => {
                            const Icon = step.icon

                            return (
                                <div key={step.number} className="flex flex-col items-center text-center space-y-3.5">
                                    {/* Number / Icon Bubble */}
                                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border-2 border-purple-200/80 dark:border-purple-800/40 bg-white dark:bg-[#191333] shadow-md text-sm font-bold text-[#17172E] dark:text-[#F8FAFC] transition-transform hover:scale-105">
                                        <Icon size={20} className="text-[#6D28D9] dark:text-[#C4B5FD]" />
                                    </div>

                                    {/* Step Title */}
                                    <div className="space-y-1">
                                        <span className="text-[11px] font-bold uppercase tracking-wider text-[#6D28D9] dark:text-[#C4B5FD]">
                                            Step {step.number}
                                        </span>
                                        <h3 className="text-sm font-bold text-[#17172E] dark:text-[#F8FAFC]">
                                            {step.title}
                                        </h3>
                                    </div>

                                    {/* Step Description */}
                                    <p className="text-xs text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed">
                                        {step.description}
                                    </p>

                                    {/* Availability Tag */}
                                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold rounded-full px-2.5 py-0.5 border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                                        <CheckCircle2 size={10} />
                                        <span>{step.statusText}</span>
                                    </span>
                                </div>
                            )
                        })}
                    </div>
                </div>

                {/* Mobile Connected Vertical Timeline */}
                <div className="md:hidden relative pl-6 space-y-7">
                    {/* Vertical Connector Line */}
                    <div className="absolute top-4 bottom-4 left-2.5 w-0.5 bg-gradient-to-b from-[#6D28D9] via-[#8B5CF6] to-[#A78BFA] dark:to-purple-900/50" />

                    {STEPS.map((step) => {
                        const Icon = step.icon

                        return (
                            <div key={step.number} className="relative flex items-start gap-3.5">
                                {/* Timeline Dot / Bubble */}
                                <div className="absolute -left-6 mt-0.5 flex h-6 w-6 items-center justify-center rounded-full border border-purple-200 dark:border-purple-700 bg-white dark:bg-[#191333] text-[10px] font-bold text-[#6D28D9] dark:text-[#C4B5FD] shadow-sm">
                                    {step.number}
                                </div>

                                <div className="rounded-2xl p-4 border border-purple-200/80 dark:border-purple-800/40 bg-white/95 dark:bg-[#191333]/95 shadow-sm flex-1 space-y-2">
                                    <div className="flex items-center justify-between gap-2">
                                        <div className="flex items-center gap-2">
                                            <Icon size={16} className="text-[#6D28D9] dark:text-[#C4B5FD]" />
                                            <h3 className="text-sm font-bold text-[#17172E] dark:text-[#F8FAFC]">
                                                {step.title}
                                            </h3>
                                        </div>
                                        <span className="text-[9px] font-semibold rounded-full px-2 py-0.5 border shrink-0 border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                                            <CheckCircle2 size={9} />
                                            <span>{step.statusText}</span>
                                        </span>
                                    </div>
                                    <p className="text-xs text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed">
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
