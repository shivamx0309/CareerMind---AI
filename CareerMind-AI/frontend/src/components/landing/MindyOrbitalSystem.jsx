import { FileText, Briefcase, TrendingUp, Sparkles } from 'lucide-react'
import MindyMascot from '../common/MindyMascot'

/**
 * Four floating career intelligence pillars revolving in orbit around Mindy:
 * 1. Resume (FileText)
 * 2. Job Matching (Briefcase)
 * 3. Analytics (TrendingUp)
 * 4. AI Interview (Sparkles)
 */
const ORBITAL_NODES = [
    {
        id: 'resume',
        label: 'Resume',
        subtitle: 'Intelligence',
        icon: FileText,
        color: 'text-[#8B5CF6]',
        bg: 'bg-[#8B5CF6]/15',
        border: 'border-[#8B5CF6]/30',
        positionClass: 'top-0 left-1/2 -translate-x-1/2 -translate-y-1/2',
    },
    {
        id: 'jobs',
        label: 'Job Matching',
        subtitle: 'Readiness',
        icon: Briefcase,
        color: 'text-[#6D28D9] dark:text-[#A78BFA]',
        bg: 'bg-[#6D28D9]/15',
        border: 'border-[#6D28D9]/30',
        positionClass: 'top-1/2 right-0 translate-x-1/2 -translate-y-1/2',
    },
    {
        id: 'analytics',
        label: 'Analytics',
        subtitle: 'Skill Gaps',
        icon: TrendingUp,
        color: 'text-[#22C55E]',
        bg: 'bg-[#22C55E]/15',
        border: 'border-[#22C55E]/30',
        positionClass: 'bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2',
    },
    {
        id: 'interview',
        label: 'AI Interview',
        subtitle: 'Preparation',
        icon: Sparkles,
        color: 'text-[#C4B5FD] dark:text-[#C4B5FD]',
        bg: 'bg-[#8B5CF6]/20',
        border: 'border-[#C4B5FD]/40',
        positionClass: 'top-1/2 left-0 -translate-x-1/2 -translate-y-1/2',
    },
]

export default function MindyOrbitalSystem() {
    return (
        <div className="relative w-full max-w-[340px] sm:max-w-[420px] lg:max-w-[480px] aspect-square flex items-center justify-center mx-auto select-none my-6 sm:my-0">
            {/* Ambient Purple Backdrop Glow */}
            <div className="absolute inset-4 rounded-full bg-gradient-to-tr from-[#6D28D9]/25 via-[#8B5CF6]/20 to-[#C4B5FD]/15 blur-3xl -z-10 pointer-events-none" />

            {/* Outer Subtle Orbit Guide Ring */}
            <div className="absolute inset-2 sm:inset-4 rounded-full border border-purple-400/20 dark:border-purple-500/20 -z-10" />

            {/* Glowing Elliptical Pulsing Orbit Ring */}
            <div className="absolute inset-6 sm:inset-8 rounded-full border-2 border-dashed border-[#8B5CF6]/40 dark:border-[#C4B5FD]/35 shadow-[0_0_35px_rgba(139,92,246,0.22)] animate-pulse-ring -z-10" />

            {/* Stationary Mindy 3D Mascot with Subtle Breathing Float */}
            <div className="relative z-10 w-[64%] h-[64%] flex items-center justify-center animate-float-gentle">
                <MindyMascot
                    expression="welcome"
                    alt="Mindy Mascot — CareerMind AI"
                    size="custom"
                    priority={true}
                    className="w-full h-full"
                />
            </div>

            {/* Continuously Revolving Orbital System (8-12s rotation) */}
            <div className="absolute inset-6 sm:inset-8 animate-orbit pointer-events-none">
                {ORBITAL_NODES.map((node) => {
                    const Icon = node.icon
                    return (
                        <div
                            key={node.id}
                            className={`absolute ${node.positionClass}`}
                        >
                            {/* Counter-spin cancels rotation to keep text & icon perfectly upright */}
                            <div className="animate-counter-orbit pointer-events-auto">
                                <div className="group flex items-center gap-2 rounded-2xl border border-purple-300/40 dark:border-purple-500/30 bg-white/95 dark:bg-[#191333]/95 px-2.5 py-1.5 sm:px-3 sm:py-2 shadow-lg shadow-purple-500/15 backdrop-blur-md hover:scale-110 hover:shadow-xl hover:shadow-purple-500/25 transition-all cursor-default">
                                    <div
                                        className={`flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-xl ${node.bg} ${node.color} ${node.border} border shadow-inner`}
                                    >
                                        <Icon size={16} strokeWidth={2.4} />
                                    </div>
                                    <div className="text-left leading-tight block">
                                        <span className="block text-[10px] sm:text-xs font-bold text-[#17172E] dark:text-[#F8FAFC]">
                                            {node.label}
                                        </span>
                                        <span className="block text-[8px] sm:text-[10px] font-medium text-[#64748B] dark:text-[#C4B5FD]/80">
                                            {node.subtitle}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
