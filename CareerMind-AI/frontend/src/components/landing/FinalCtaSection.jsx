import { Link } from 'react-router-dom'
import { Sparkles, ArrowRight, ShieldCheck } from 'lucide-react'
import MindyMascot from '../common/MindyMascot'

export default function FinalCtaSection() {
    return (
        <section className="py-20 sm:py-24 border-t border-[var(--border)] relative overflow-hidden">
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="glass-card relative overflow-hidden rounded-3xl p-8 sm:p-12 lg:p-16 border border-purple-300/30 dark:border-purple-500/30 shadow-2xl bg-gradient-to-br from-white/95 via-purple-50/40 to-white/95 dark:from-[#191333]/95 dark:via-[#160F28]/95 dark:to-[#191333]/95">
                    {/* Ambient Glow */}
                    <div className="pointer-events-none absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-48 bg-gradient-to-r from-[#6D28D9]/25 via-[#8B5CF6]/20 to-[#C4B5FD]/15 rounded-full blur-3xl -z-10" />

                    <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
                        {/* Left Column: Heading & CTA */}
                        <div className="md:col-span-8 text-center md:text-left space-y-5">
                            <div className="inline-flex items-center gap-1.5 rounded-full border border-[#8B5CF6]/30 bg-[#8B5CF6]/10 dark:bg-[#8B5CF6]/20 px-3.5 py-1 text-xs font-bold text-[#6D28D9] dark:text-[#C4B5FD]">
                                <Sparkles size={13} className="text-[#8B5CF6]" />
                                <span>Take The Next Step</span>
                            </div>

                            <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-[#17172E] dark:text-[#F8FAFC] leading-tight">
                                Ready to Take Control of{' '}
                                <span className="purple-gradient-text">Your Career?</span>
                            </h2>

                            <p className="text-sm sm:text-base text-[#64748B] dark:text-[#C4B5FD]/90 leading-relaxed max-w-lg">
                                Start by creating your career profile and unlocking private, explainable intelligence with Mindy.
                            </p>

                            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center md:justify-start gap-3.5">
                                <Link
                                    to="/onboarding"
                                    className="purple-gradient-btn w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl px-8 py-3.5 text-sm font-bold shadow-lg cursor-pointer"
                                >
                                    <span>Build My Career Profile</span>
                                    <ArrowRight size={16} />
                                </Link>
                            </div>

                            <div className="pt-3 flex items-center justify-center md:justify-start gap-2 text-xs text-[#64748B] dark:text-[#8E8AA7]">
                                <ShieldCheck size={15} className="text-[#22C55E]" />
                                <span>100% Free &bull; Local-First &bull; Zero External LLM APIs</span>
                            </div>
                        </div>

                        {/* Right Column: Mindy Celebrating / Thumbs Up Mascot */}
                        <div className="md:col-span-4 flex items-center justify-center">
                            <div className="relative w-44 h-44 sm:w-52 sm:h-52 flex items-center justify-center animate-float-gentle">
                                <MindyMascot
                                    expression="welcome"
                                    alt="Mindy Celebrating"
                                    size="custom"
                                    className="w-full h-full"
                                    speechBubble="Let's do this! 🚀"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    )
}
