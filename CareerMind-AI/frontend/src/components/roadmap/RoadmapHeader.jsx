import {
    Route,
    Sliders,
    History,
    Plus,
    ChevronDown,
} from 'lucide-react'

export default function RoadmapHeader({
    activeRoadmap,
    allRoadmaps = [],
    onSelectRoadmap,
    onOpenGenerator,
    onOpenPreferences,
    onOpenHistory,
}) {
    const isCompleted = activeRoadmap?.status === 'completed'

    return (
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between pb-6 border-b border-[var(--border)]">
            {/* Title & Description */}
            <div>
                <div className="flex flex-wrap items-center gap-2.5">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-md shadow-purple-600/20">
                        <Route size={20} />
                    </div>
                    <h1 className="text-2xl font-black tracking-tight text-[var(--text-primary)]">
                        Personalized Learning Roadmap
                    </h1>
                    {activeRoadmap && (
                        <span
                            className={`rounded-full px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider ${
                                isCompleted
                                    ? 'border border-emerald-500/30 bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                                    : 'border border-amber-500/30 bg-amber-500/15 text-amber-700 dark:text-amber-300'
                            }`}
                        >
                            {isCompleted ? 'Completed' : 'In Progress'}
                        </span>
                    )}
                </div>
                <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    AI-powered curriculum sequenced by prerequisite dependencies with verified free documentation, hands-on tasks, and weekly milestones.
                </p>
            </div>

            {/* Actions & Switcher */}
            <div className="flex flex-wrap items-center gap-2.5">
                {/* Active Roadmap Switcher Dropdown (if more than 1 exists) */}
                {allRoadmaps.length > 1 && (
                    <div className="relative">
                        <select
                            value={activeRoadmap?.id || ''}
                            onChange={(e) => onSelectRoadmap(e.target.value)}
                            className="appearance-none rounded-xl border border-[var(--border)] bg-[var(--surface-card)] py-2 pl-3.5 pr-8 text-xs font-bold text-[var(--text-primary)] shadow-sm focus:border-[var(--accent)] focus:outline-none cursor-pointer"
                        >
                            {allRoadmaps.map((rm) => (
                                <option key={rm.id} value={rm.id}>
                                    {rm.role_title} ({rm.weekly_study_hours}h/wk)
                                </option>
                            ))}
                        </select>
                        <ChevronDown
                            size={14}
                            className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
                        />
                    </div>
                )}

                {/* History Button */}
                <button
                    type="button"
                    onClick={onOpenHistory}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-card)] px-3 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--border-hover)] transition-all cursor-pointer shadow-sm"
                >
                    <History size={14} />
                    <span className="hidden sm:inline">History</span>
                    {allRoadmaps.length > 0 && (
                        <span className="rounded-full bg-[var(--surface-hover)] px-1.5 py-0.2 text-[10px] font-mono font-bold text-[var(--text-secondary)]">
                            {allRoadmaps.length}
                        </span>
                    )}
                </button>

                {/* Preferences Button */}
                <button
                    type="button"
                    onClick={onOpenPreferences}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-card)] px-3 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--border-hover)] transition-all cursor-pointer shadow-sm"
                >
                    <Sliders size={14} />
                    <span className="hidden sm:inline">Study Pace</span>
                </button>

                {/* New Roadmap Button */}
                <button
                    type="button"
                    onClick={onOpenGenerator}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--primary-purple)] px-4 py-2 text-xs font-bold text-white shadow-md shadow-purple-600/20 hover:opacity-95 transition-all cursor-pointer"
                >
                    <Plus size={14} />
                    <span>New Roadmap</span>
                </button>
            </div>
        </div>
    )
}
