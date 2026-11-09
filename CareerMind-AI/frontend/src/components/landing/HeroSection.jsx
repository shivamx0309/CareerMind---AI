import { Link } from 'react-router-dom'
import { Sparkles, ArrowRight, ShieldCheck, Layers, Lock, Cpu } from 'lucide-react'
import MindyOrbitalSystem from './MindyOrbitalSystem'
import MobileHeroMascot from './MobileHeroMascot'

export default function HeroSection() {
    return (
        <section className="relative overflow-hidden pt-5 pb-10 sm:pt-14 sm:pb-20 lg:pt-20 lg:pb-28">
            {/* Ambient Background Aura */}
            <div className="pointer-events-none absolute top-1/4 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[400px] bg-gradient-to-tr from-[#6D28D9]/15 via-[#8B5CF6]/15 to-[#C4B5FD]/10 rounded-full blur-3xl -z-10" />

            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-center">
                    {/* Left Column — Content on Desktop & Full Flow on Mobile */}
                    <div className="lg:col-span-7 flex flex-col items-center lg:items-start text-center lg:text-left space-y-4 sm:space-y-6">
                        {/* 1. Small Badge */}
                        <div className="inline-flex items-center gap-1.5 rounded-full border border-purple-200/90 dark:border-purple-500/30 bg-[#EDE9FE] dark:bg-purple-950/40 px-3.5 py-1 text-xs font-bold text-[#6D28D9] dark:text-[#C4B5FD] shadow-sm">
                            <Sparkles size={13} className="text-[#6D28D9] dark:text-[#C4B5FD]" />
                            <span>AI-Powered Career Intelligence Platform</span>
                        </div>

                        {/* 2. Main Heading with Purple Gradient Highlight */}
                        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-[#17172E] dark:text-[#F8FAFC] leading-[1.12]">
                            <span className="block">Your Career.</span>
                            <span className="purple-gradient-text block">
                                Your Intelligence.
                            </span>
                            <span className="purple-gradient-text block">
                                Your Growth.
                            </span>
                        </h1>

                        {/* 3. Short Description */}
                        <p className="text-sm sm:text-base lg:text-lg text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed max-w-md lg:max-w-xl">
                            Analyze your skills, find opportunities and get interview-ready — all in one platform.
                        </p>

                        {/* 4. Two CTA Buttons: Full-width stacked on mobile, row on tablet/desktop */}
                        <div className="flex flex-col sm:flex-row items-center gap-3 pt-1 w-full sm:w-auto">
                            {/* Primary CTA */}
                            <Link
                                to="/onboarding"
                                className="purple-gradient-btn w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-2xl px-7 py-3.5 text-sm font-bold shadow-lg shadow-purple-600/25 cursor-pointer hover:shadow-purple-600/35 transition-all"
                            >
                                <Sparkles size={15} />
                                <span>Build My Career Profile</span>
                                <ArrowRight size={15} />
                            </Link>

                            {/* Secondary CTA */}
                            <a
                                href="#features"
                                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-2xl border border-purple-200/90 dark:border-purple-500/30 bg-white dark:bg-[#191333] px-6 py-3.5 text-sm font-bold text-[#17172E] dark:text-[#F8FAFC] shadow-sm hover:border-[#8B5CF6] hover:bg-purple-50/50 dark:hover:bg-[#20183E] transition-all"
                            >
                                <span>Explore Features</span>
                            </a>
                        </div>

                        {/* 5. Mobile-Only Section: Mindy Mascot + 4 Floating Cards (Visible only on < lg screens) */}
                        <div className="w-full block lg:hidden pt-2">
                            <MobileHeroMascot />
                        </div>

                        {/* 6. Mobile-Only Section: Compact 3-Column Trust Indicators Card (Visible only on < lg screens) */}
                        <div className="w-full block lg:hidden pt-1">
                            <div className="w-full rounded-2xl border border-purple-200/90 dark:border-purple-500/30 bg-white/95 dark:bg-[#191333]/95 shadow-sm p-3.5 backdrop-blur-md">
                                <div className="grid grid-cols-3 divide-x divide-purple-100 dark:divide-purple-800/40 text-center items-center">
                                    <div className="flex flex-col items-center justify-center px-1">
                                        <ShieldCheck size={18} className="text-[#22C55E]" />
                                        <span className="text-[10px] sm:text-xs font-bold text-[#17172E] dark:text-[#F8FAFC] mt-1.5 leading-tight">
                                            Local-First<br />&amp; Private
                                        </span>
                                    </div>
                                    <div className="flex flex-col items-center justify-center px-1">
                                        <Layers size={18} className="text-[#8B5CF6]" />
                                        <span className="text-[10px] sm:text-xs font-bold text-[#17172E] dark:text-[#F8FAFC] mt-1.5 leading-tight">
                                            Explainable<br />Scoring
                                        </span>
                                    </div>
                                    <div className="flex flex-col items-center justify-center px-1">
                                        <Lock size={18} className="text-[#3B82F6] dark:text-[#A78BFA]" />
                                        <span className="text-[10px] sm:text-xs font-bold text-[#17172E] dark:text-[#F8FAFC] mt-1.5 leading-tight">
                                            Zero External<br />LLM APIs
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* 7. Desktop-Only Trust Indicators (Visible only on >= lg screens) */}
                        <div className="hidden lg:flex pt-6 flex-wrap items-center justify-start gap-8 text-xs font-semibold text-[#64748B] dark:text-[#CBD5E1]/90 border-t border-[var(--border)] w-full">
                            <div className="flex items-center gap-2">
                                <ShieldCheck size={16} className="text-[#22C55E]" />
                                <span className="text-[#17172E] dark:text-[#F8FAFC] font-bold">Local-First &amp; Private</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Cpu size={16} className="text-[#8B5CF6]" />
                                <span className="text-[#17172E] dark:text-[#F8FAFC] font-bold">Explainable Scoring</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Lock size={16} className="text-[#6D28D9] dark:text-[#C4B5FD]" />
                                <span className="text-[#17172E] dark:text-[#F8FAFC] font-bold">Zero External LLM APIs</span>
                            </div>
                        </div>
                    </div>

                    {/* Right Column – Desktop-Only Mindy Mascot & Orbital Animation */}
                    <div className="hidden lg:flex lg:col-span-5 items-center justify-center w-full">
                        <MindyOrbitalSystem />
                    </div>
                </div>
            </div>
        </section>
    )
}
