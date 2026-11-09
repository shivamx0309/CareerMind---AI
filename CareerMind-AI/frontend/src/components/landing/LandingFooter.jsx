import { Link } from 'react-router-dom'
import MindyMascot from '../common/MindyMascot'

export default function LandingFooter() {
    const handleScrollToTop = () => {
        const container = document.querySelector('.landing-page-container') || window
        if (container.scrollTo) {
            container.scrollTo({ top: 0, behavior: 'smooth' })
        }
    }

    return (
        <footer className="border-t border-purple-200/60 dark:border-purple-900/30 bg-white/60 dark:bg-[#0D0A1A]/60 py-12 transition-colors duration-200">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                    {/* Brand & Description */}
                    <div className="space-y-2 max-w-sm">
                        <Link
                            to="/"
                            onClick={handleScrollToTop}
                            className="flex items-center gap-2.5 transition-opacity hover:opacity-90"
                        >
                            <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-sm overflow-hidden">
                                <MindyMascot expression="chatbot" size="xs" alt="CareerMind Logo" className="scale-125 translate-y-0.5" />
                            </div>
                            <span className="text-sm font-extrabold tracking-tight text-[#17172E] dark:text-[#F8FAFC]">
                                CareerMind <span className="purple-gradient-text">AI</span>
                            </span>
                        </Link>
                        <p className="text-xs text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed">
                            A modern, local-first career intelligence platform designed to help candidates evaluate their skills and accelerate career growth.
                        </p>
                    </div>

                    {/* Navigation Links — EXACT FOUR ITEMS */}
                    <nav className="flex flex-wrap items-center gap-6 text-xs font-semibold text-[#64748B] dark:text-[#C4B5FD]">
                        <a
                            href="#"
                            onClick={handleScrollToTop}
                            className="hover:text-[#6D28D9] dark:hover:text-white transition-colors"
                        >
                            Home
                        </a>
                        <a
                            href="#features"
                            className="hover:text-[#6D28D9] dark:hover:text-white transition-colors"
                        >
                            Features
                        </a>
                        <a
                            href="#how-it-works"
                            className="hover:text-[#6D28D9] dark:hover:text-white transition-colors"
                        >
                            How It Works
                        </a>
                        <Link
                            to="/onboarding"
                            className="text-[#6D28D9] dark:text-[#A78BFA] font-bold hover:underline"
                        >
                            Get Started
                        </Link>
                    </nav>
                </div>

                {/* Bottom Copyright */}
                <div className="pt-6 border-t border-purple-100 dark:border-purple-900/30 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-[#64748B] dark:text-[#CBD5E1]/90">
                    <span>&copy; {new Date().getFullYear()} CareerMind AI &bull; Mindy Mascot. All rights reserved.</span>
                    <span className="flex items-center gap-1.5">
                        <span className="h-1.5 w-1.5 rounded-full bg-[#22C55E]" />
                        <span>Private, Local-First Architecture</span>
                    </span>
                </div>
            </div>
        </footer>
    )
}
