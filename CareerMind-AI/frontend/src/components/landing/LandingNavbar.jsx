import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Sun, Moon, Menu, X, ArrowRight } from 'lucide-react'
import { useTheme } from '../../context/ThemeContext'
import MindyMascot from '../common/MindyMascot'

export default function LandingNavbar() {
    const { theme, toggleTheme } = useTheme()
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

    const handleScrollToTop = () => {
        if (window.location.pathname === '/') {
            const container = document.querySelector('.landing-page-container') || window
            if (container.scrollTo) {
                container.scrollTo({ top: 0, behavior: 'smooth' })
            }
        }
        setMobileMenuOpen(false)
    }

    const handleAnchorClick = () => {
        setMobileMenuOpen(false)
    }

    return (
        <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-[var(--bg)]/85 border-b border-[var(--border)] transition-colors duration-200">
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

                {/* 2. Center: Home, Features, How It Works */}
                <nav className="hidden md:flex items-center justify-center gap-8 text-xs font-semibold text-[#64748B] dark:text-[#C4B5FD]/90">
                    <a
                        href="#"
                        onClick={handleScrollToTop}
                        className="hover:text-[#6D28D9] dark:hover:text-white transition-colors"
                    >
                        Home
                    </a>
                    <a
                        href="#features"
                        onClick={handleAnchorClick}
                        className="hover:text-[#6D28D9] dark:hover:text-white transition-colors"
                    >
                        Features
                    </a>
                    <a
                        href="#how-it-works"
                        onClick={handleAnchorClick}
                        className="hover:text-[#6D28D9] dark:hover:text-white transition-colors"
                    >
                        How It Works
                    </a>
                </nav>

                {/* 3. Right: Get Started Button + Theme Toggle + Mobile Toggle */}
                <div className="flex items-center gap-3 shrink-0">
                    <button
                        type="button"
                        onClick={toggleTheme}
                        aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
                        title="Toggle color theme"
                        className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[#8B5CF6]/40 transition-all cursor-pointer"
                    >
                        {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
                    </button>

                    {/* Get Started Button (Desktop) */}
                    <Link
                        to="/onboarding"
                        className="purple-gradient-btn hidden sm:inline-flex items-center gap-1.5 rounded-xl px-4 py-2 text-xs font-bold shadow-md cursor-pointer"
                    >
                        <span>Get Started</span>
                        <ArrowRight size={13} />
                    </Link>

                    {/* Mobile Hamburger Toggle */}
                    <button
                        type="button"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
                        className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                    >
                        {mobileMenuOpen ? <X size={19} /> : <Menu size={19} />}
                    </button>
                </div>
            </div>

            {/* Mobile Collapsible Navigation Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-b border-[var(--border)] bg-[var(--surface-solid)]/95 backdrop-blur-xl px-4 py-5 shadow-2xl transition-all">
                    <div className="flex flex-col gap-3">
                        <a
                            href="#"
                            onClick={handleScrollToTop}
                            className="px-3 py-2 text-sm font-semibold text-[#17172E] dark:text-[#F8FAFC] rounded-lg hover:bg-[#8B5CF6]/10 transition-colors"
                        >
                            Home
                        </a>
                        <a
                            href="#features"
                            onClick={handleAnchorClick}
                            className="px-3 py-2 text-sm font-semibold text-[#64748B] dark:text-[#C4B5FD] rounded-lg hover:bg-[#8B5CF6]/10 transition-colors"
                        >
                            Features
                        </a>
                        <a
                            href="#how-it-works"
                            onClick={handleAnchorClick}
                            className="px-3 py-2 text-sm font-semibold text-[#64748B] dark:text-[#C4B5FD] rounded-lg hover:bg-[#8B5CF6]/10 transition-colors"
                        >
                            How It Works
                        </a>

                        <div className="pt-3 border-t border-[var(--border)]">
                            <Link
                                to="/onboarding"
                                onClick={() => setMobileMenuOpen(false)}
                                className="purple-gradient-btn w-full inline-flex items-center justify-center gap-2 rounded-xl py-3 text-xs font-bold text-white shadow-md"
                            >
                                <span>Get Started</span>
                                <ArrowRight size={14} />
                            </Link>
                        </div>
                    </div>
                </div>
            )}
        </header>
    )
}
