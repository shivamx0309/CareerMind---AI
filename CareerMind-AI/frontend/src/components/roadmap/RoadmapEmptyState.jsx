import { Link } from 'react-router-dom'
import {
    Route,
    Sparkles,
    ArrowRight,
    Briefcase,
    Calendar,
    BookOpen,
} from 'lucide-react'
import MindyMascot from '../common/MindyMascot'

export default function RoadmapEmptyState({ onOpenGenerator }) {
    return (
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-card)] p-8 sm:p-12 text-center shadow-sm">
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-tr from-[#6D28D9]/20 to-[#8B5CF6]/20 border border-[var(--accent)]/30 text-[var(--accent)] mb-6 shadow-inner">
                <MindyMascot expression="excited" size="md" alt="Mindy Mascot" />
            </div>

            <h3 className="text-xl sm:text-2xl font-black text-[var(--text-primary)]">
                Personalized Learning Roadmap
            </h3>
            <p className="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-[var(--text-secondary)]">
                Convert your assessed skill gaps into a sequential, milestone-driven curriculum.
                We analyze your target role, topological prerequisites, and weekly study pace to generate tailored lessons with verified free resources.
            </p>

            {/* Feature Highlights Grid */}
            <div className="mx-auto mt-8 grid max-w-2xl grid-cols-1 gap-3 sm:grid-cols-3 text-left">
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 mb-2.5">
                        <Route size={16} />
                    </div>
                    <div className="text-xs font-bold text-[var(--text-primary)]">
                        Prerequisite Sequenced
                    </div>
                    <div className="mt-1 text-[11px] text-[var(--text-secondary)]">
                        Foundational skills come first so you learn without getting stuck.
                    </div>
                </div>

                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 mb-2.5">
                        <BookOpen size={16} />
                    </div>
                    <div className="text-xs font-bold text-[var(--text-primary)]">
                        100% Verified Free
                    </div>
                    <div className="mt-1 text-[11px] text-[var(--text-secondary)]">
                        Official documentation, tutorials, and practical hands-on exercises.
                    </div>
                </div>

                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
                    <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400 mb-2.5">
                        <Calendar size={16} />
                    </div>
                    <div className="text-xs font-bold text-[var(--text-primary)]">
                        Paced to Your Schedule
                    </div>
                    <div className="mt-1 text-[11px] text-[var(--text-secondary)]">
                        Choose 5, 10, 15, or 20 hours per week for realistic milestones.
                    </div>
                </div>
            </div>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                <button
                    type="button"
                    onClick={onOpenGenerator}
                    className="inline-flex items-center gap-2 rounded-xl bg-[var(--primary-purple)] px-6 py-3 text-sm font-bold text-white shadow-lg shadow-purple-600/25 hover:opacity-95 transition-all cursor-pointer"
                >
                    <Sparkles size={16} />
                    Generate Your Roadmap
                </button>
                <Link
                    to="/skills"
                    className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] px-5 py-3 text-sm font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all"
                >
                    <Briefcase size={15} />
                    View Skill Gap Analysis
                    <ArrowRight size={14} />
                </Link>
            </div>
        </div>
    )
}

