import { Link } from 'react-router-dom'
import { Sparkles, ArrowRight, ShieldCheck, Cpu, Lock } from 'lucide-react'
import MindyOrbitalSystem from './MindyOrbitalSystem'

export default function HeroSection() {
    return (
        <section className="relative overflow-hidden pt-10 pb-16 sm:pt-16 sm:pb-24 lg:pt-20 lg:pb-28">
            {/* Ambient Background Aura */}
            <div className="pointer-events-none absolute top-1/4 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[400px] bg-gradient-to-tr from-[#6D28D9]/15 via-[#8B5CF6]/15 to-[#C4B5FD]/10 rounded-full blur-3xl -z-10" />

            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-8 items-center">
                    {/* Left Column — Content (55–60% width) */}
                    <div className="lg:col-span-7 flex flex-col items-center lg:items-start text-center lg:text-left space-y-6">
                        {/* Small Badge */}
                        <div className="inline-flex items-center gap-2 rounded-full border border-[#8B5CF6]/30 bg-[#8B5CF6]/10 dark:bg-[#8B5CF6]/20 px-3.5 py-1 text-xs font-bold text-[#6D28D9] dark:text-[#C4B5FD] shadow-sm">
                            <Sparkles size={14} className="text-[#8B5CF6]" />
                            <span>AI-Powered Career Intelligence Platform</span>
                        </div>

                        {/* Main Heading with Purple Gradient Highlight */}
                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-[#17172E] dark:text-[#F8FAFC] leading-[1.12]">
                            Your Career.{' '}
                            <span className="purple-gradient-text block sm:inline">
                                Your Intelligence. Your Growth.
                            </span>
                        </h1>

                        {/* Short Description */}
                        <p className="text-base sm:text-lg text-[#64748B] dark:text-[#C4B5FD]/90 leading-relaxed max-w-xl">
                            Analyze your skills, find opportunities and get interview-ready — all in one platform.
                        </p>

                        {/* Two CTA Buttons */}
                        <div className="flex flex-col sm:flex-row items-center gap-3.5 pt-2 w-full sm:w-auto">
                            {/* Primary CTA */}
                            <Link
                                to="/onboarding"
                                className="purple-gradient-btn w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl px-7 py-3.5 text-sm font-bold shadow-lg cursor-pointer"
                            >
                                <Sparkles size={16} />
                                <span>Build My Career Profile</span>
                                <ArrowRight size={16} />
                            </Link>

                            {/* Secondary CTA */}
                            <a
                                href="#features"
                                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-purple-200 dark:border-purple-500/30 bg-white/80 dark:bg-[#191333]/80 px-6 py-3.5 text-sm font-semibold text-[#17172E] dark:text-[#F8FAFC] hover:bg-purple-50 dark:hover:bg-purple-950/30 transition-all"
                            >
                                <span>Explore Features</span>
                            </a>
                        </div>

                        {/* Three Trust Indicators */}
                        <div className="pt-6 flex flex-wrap items-center justify-center lg:justify-start gap-5 sm:gap-8 text-xs font-semibold text-[#64748B] dark:text-[#C4B5FD]/80 border-t border-[var(--border)] w-full">
                            <div className="flex items-center gap-2">
                                <ShieldCheck size={16} className="text-[#22C55E]" />
                                <span>Local-First &amp; Private</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Cpu size={16} className="text-[#8B5CF6]" />
                                <span>Explainable Scoring</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Lock size={16} className="text-[#6D28D9] dark:text-[#C4B5FD]" />
                                <span>Zero External LLM APIs</span>
                            </div>
                        </div>
                    </div>

                    {/* Right Column – Mindy Mascot & Orbital Animation (40–45% width) */}
                    <div className="lg:col-span-5 flex items-center justify-center w-full">
                        <MindyOrbitalSystem />
                    </div>
                </div>
            </div>
        </section>
    )
}
