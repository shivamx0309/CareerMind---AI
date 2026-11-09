import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FileText, Briefcase, Target, BarChart3, Bot, Sparkles } from 'lucide-react'

const MOBILE_FEATURES = [
    {
        id: 'resume',
        title: 'Resume',
        subtitle: 'Intelligence',
        icon: FileText,
    },
    {
        id: 'jobs',
        title: 'Job',
        subtitle: 'Matching',
        icon: Briefcase,
    },
    {
        id: 'skills',
        title: 'Skill Gap',
        subtitle: 'Analysis',
        icon: Target,
    },
    {
        id: 'learning',
        title: 'Learning',
        subtitle: 'Path',
        icon: BarChart3,
    },
    {
        id: 'interview',
        title: 'AI Interview',
        subtitle: 'Preparation',
        icon: Bot,
    },
]

// Glowing node positions along orbital path for each card (0 to 4)
const ORBIT_NODE_COORDS = [
    { cx: 215, cy: 15 },
    { cx: 130, cy: 45 },
    { cx: 85, cy: 110 },
    { cx: 115, cy: 175 },
    { cx: 210, cy: 215 },
]

export default function MobileHeroMascot() {
    const [activeIndex, setActiveIndex] = useState(0)

    // Infinite loop cycling top to bottom with a 2-second pause per item
    useEffect(() => {
        const interval = setInterval(() => {
            setActiveIndex((prev) => (prev + 1) % MOBILE_FEATURES.length)
        }, 2000)

        return () => clearInterval(interval)
    }, [])

    const activeNode = ORBIT_NODE_COORDS[activeIndex] || ORBIT_NODE_COORDS[0]

    return (
        <div className="relative w-full max-w-sm sm:max-w-md mx-auto my-2 py-0.5 select-none">
            {/* Ambient Purple Backdrop Glow */}
            <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full bg-gradient-to-tr from-[#6D28D9]/20 via-[#8B5CF6]/15 to-[#C4B5FD]/15 blur-3xl -z-10" />

            {/* Orbital Curve SVG with Dynamic Active Node */}
            <svg
                className="pointer-events-none absolute inset-0 w-full h-full -z-0 overflow-visible"
                viewBox="0 0 380 230"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    d="M 225 15 C 185 15, 100 45, 88 115 C 75 185, 155 218, 225 218"
                    stroke="#8B5CF6"
                    strokeWidth="1.5"
                    strokeDasharray="4 4"
                    strokeOpacity="0.45"
                />
                {/* Static Guide Nodes */}
                <circle cx="225" cy="15" r="3" fill="#8B5CF6" opacity="0.6" />
                <circle cx="105" cy="62" r="2.5" fill="#C4B5FD" opacity="0.6" />
                <circle cx="88" cy="118" r="2.5" fill="#8B5CF6" opacity="0.6" />
                <circle cx="138" cy="202" r="3" fill="#C4B5FD" opacity="0.6" />

                {/* Animated Glowing Beacon tracking the active card top-to-bottom */}
                <motion.circle
                    animate={{ cx: activeNode.cx, cy: activeNode.cy }}
                    transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    r="4.5"
                    fill="#8B5CF6"
                    className="drop-shadow-[0_0_8px_#8B5CF6]"
                />
                <motion.circle
                    animate={{ cx: activeNode.cx, cy: activeNode.cy }}
                    transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    r="7"
                    fill="#C4B5FD"
                    opacity="0.35"
                    className="animate-ping"
                />
            </svg>

            {/* Sparkles near Mascot */}
            <div className="pointer-events-none absolute top-8 left-[35%] text-amber-400 animate-bounce">
                <Sparkles size={14} />
            </div>

            <div className="relative z-10 flex items-center justify-between gap-2 sm:gap-3 px-0.5">
                {/* Left: 3D Cute Mindy Robot Mascot */}
                <div className="w-[42%] flex items-center justify-center shrink-0">
                    <motion.div
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
                        className="relative w-full max-w-[140px] sm:max-w-[165px] aspect-[4/5] flex items-center justify-center"
                    >
                        <img
                            src="/assets/mindy/mindy-welcome.png"
                            alt="Mindy AI Mascot"
                            loading="eager"
                            decoding="async"
                            className="w-full h-full object-contain filter drop-shadow-[0_10px_20px_rgba(109,40,217,0.22)]"
                        />
                    </motion.div>
                </div>

                {/* Right: Exactly 5 Compact Feature Cards with 2-Second Top-to-Bottom Loop */}
                <div className="w-[56%] flex flex-col gap-1 sm:gap-1.5">
                    {MOBILE_FEATURES.map((item, idx) => {
                        const Icon = item.icon
                        const isActive = activeIndex === idx

                        return (
                            <motion.div
                                key={item.id}
                                layout
                                data-testid="mascot-feature-card"
                                onClick={() => setActiveIndex(idx)}
                                className={`group relative flex items-center justify-between rounded-xl py-1 px-2 sm:py-1.5 sm:px-2.5 border transition-all duration-400 cursor-pointer ${
                                    isActive
                                        ? 'border-[#8B5CF6] dark:border-[#A78BFA] bg-gradient-to-r from-purple-100/95 via-purple-50 to-white dark:from-[#291B52] dark:via-[#201542] dark:to-[#191333] shadow-md shadow-purple-500/20 -translate-x-1 scale-[1.02] ring-1 ring-[#8B5CF6]/50'
                                        : 'border-purple-200/80 dark:border-purple-500/30 bg-white/95 dark:bg-[#191333]/95 shadow-xs opacity-90 hover:opacity-100 hover:border-[#8B5CF6]'
                                }`}
                            >
                                <div className="flex items-center gap-2 min-w-0">
                                    <div
                                        className={`flex h-6 w-6 sm:h-7 sm:w-7 items-center justify-center rounded-lg shrink-0 transition-all duration-300 ${
                                            isActive
                                                ? 'bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-sm shadow-purple-600/40 ring-1 ring-purple-300 dark:ring-purple-500'
                                                : 'bg-purple-100/80 dark:bg-purple-900/40 text-[#6D28D9] dark:text-[#C4B5FD] border border-purple-200/60 dark:border-purple-800/40'
                                        }`}
                                    >
                                        <Icon size={13} strokeWidth={isActive ? 2.5 : 2.2} />
                                    </div>
                                    <div className="min-w-0 text-left leading-[1.1]">
                                        <span
                                            className={`block text-[11px] font-bold truncate transition-colors duration-200 ${
                                                isActive
                                                    ? 'text-[#6D28D9] dark:text-[#C4B5FD]'
                                                    : 'text-[#17172E] dark:text-[#F8FAFC]'
                                            }`}
                                        >
                                            {item.title}
                                        </span>
                                        <span
                                            className={`block text-[9.5px] font-semibold truncate transition-colors duration-200 ${
                                                isActive
                                                    ? 'text-[#7C3AED] dark:text-purple-200'
                                                    : 'text-[#64748B] dark:text-[#C4B5FD]/80'
                                            }`}
                                        >
                                            {item.subtitle}
                                        </span>
                                    </div>
                                </div>

                                {/* Active Pulse Indicator Dot */}
                                {isActive && (
                                    <div className="flex items-center pr-1 shrink-0">
                                        <span className="relative flex h-2 w-2">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#8B5CF6] opacity-75" />
                                            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[#8B5CF6] dark:bg-[#C4B5FD] shadow-[0_0_6px_#8B5CF6]" />
                                        </span>
                                    </div>
                                )}
                            </motion.div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}
