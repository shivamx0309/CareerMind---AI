import { Link } from 'react-router-dom'
import { Sun, Moon, ArrowRight } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import MindyMascot from '../common/MindyMascot'

export default function LandingNavbar() {
    const { theme, toggleTheme } = useTheme()

    const handleScrollToTop = () => {
        if (window.location.pathname === '/') {
            const container = document.querySelector('.landing-page-container') || window
            if (container.scrollTo) {
                container.scrollTo({ top: 0, behavior: 'smooth' })
            }
        }
    }

    return (
        <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-white/90 dark:bg-[#0D0A1A]/90 border-b border-purple-200/60 dark:border-purple-900/30 transition-colors duration-200 shadow-sm">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                {/* 1. Left: CareerMind AI Logo + Mascot Icon */}
                <Link
                    to="/"
                    onClick={handleScrollToTop}
                    className="flex items-center gap-2.5 transition-opacity hover:opacity-90 shrink-0"
                >
                    <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-md shadow-purple-500/25 overflow-hidden">
                        <MindyMascot expression="chatbot" size="xs" alt="CareerMind Logo" className="scale-125 translate-y-0.5" />
                    </div>
                    <span className="text-base font-extrabold tracking-tight text-[#17172E] dark:text-[#F8FAFC]">
                        CareerMind <span className="purple-gradient-text">AI</span>
                    </span>
                </Link>

                {/* 2. Center: Home, Features, How It Works (Desktop Only) */}
                <nav className="hidden md:flex items-center justify-center gap-8 text-xs font-semibold text-[#64748B] dark:text-[#C4B5FD]">
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
                </nav>

                {/* 3. Right: Theme Toggle (Always visible) + Get Started Button (Desktop Only) */}
                <div className="flex items-center gap-3 shrink-0">
                    <button
                        type="button"
                        onClick={toggleTheme}
                        aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
                        title="Toggle color theme"
                        className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-purple-200/80 dark:border-purple-800/40 bg-white dark:bg-[#191333] text-[#17172E] dark:text-[#F8FAFC] hover:border-[#8B5CF6] transition-all cursor-pointer shadow-sm"
                    >
                        {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
                    </button>

                    {/* Get Started Button (Desktop Only) */}
                    <Link
                        to="/onboarding"
                        className="purple-gradient-btn hidden md:inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-bold shadow-md cursor-pointer"
                    >
                        <span>Get Started</span>
                        <ArrowRight size={13} />
                    </Link>
                </div>
            </div>
        </header>
    )
}
