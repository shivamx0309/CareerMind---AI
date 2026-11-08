import { ArrowLeft, Sun, Moon } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import MindyMascot from '../common/MindyMascot'

export default function OnboardingLayout({ children, isEdit = false }) {
    const { theme, toggleTheme } = useTheme()

    return (
        <div className="onboarding-page-container bg-[var(--background)] text-[var(--text-primary)] transition-colors duration-200">
            <div className="min-h-full flex flex-col justify-between p-4 sm:p-6 md:p-8 max-w-4xl mx-auto w-full">
                {/* Top Navigation Bar */}
                <header className="w-full flex items-center justify-between py-2 mb-6">
                    <div className="flex items-center gap-3">
                        <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-md shadow-purple-500/25 overflow-hidden">
                            <MindyMascot expression="chatbot" size="xs" alt="CareerMind Mascot" className="scale-125 translate-y-0.5" />
                        </div>
                        <div>
                            <span className="text-base font-black tracking-tight text-[var(--text-primary)]">
                                CareerMind <span className="purple-gradient-text">AI</span>
                            </span>
                            <span className="block text-[11px] font-medium text-[var(--text-secondary)]">
                                Career Intelligence Platform
                            </span>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {isEdit && (
                            <Link
                                to="/dashboard"
                                className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-1.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
                            >
                                <ArrowLeft size={14} />
                                <span>Dashboard</span>
                            </Link>
                        )}

                        <button
                            type="button"
                            onClick={toggleTheme}
                            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
                            className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                        >
                            {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
                        </button>
                    </div>
                </header>

                {/* Main Content Card Container */}
                <main className="w-full max-w-3xl mx-auto flex-1 flex flex-col justify-center my-4">
                    {children}
                </main>

                {/* Footer */}
                <footer className="w-full py-6 text-center text-xs text-[var(--text-muted)]">
                    CareerMind AI &bull; Local-first &bull; Private by design &bull; Zero external cloud APIs
                </footer>
            </div>
        </div>
    )
}
