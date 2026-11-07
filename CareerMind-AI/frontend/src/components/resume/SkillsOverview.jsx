import { useMemo, useState } from 'react'
import {
    Code2,
    Layout,
    Server,
    Database,
    BarChart3,
    Brain,
    Cpu,
    Cloud,
    Wrench,
    Boxes,
    Search,
    Layers,
} from 'lucide-react'

const CATEGORY_CONFIG = [
    {
        key: 'programming_languages',
        label: 'Programming Languages',
        icon: Code2,
        color: 'from-violet-500/15 to-purple-500/15 text-violet-400 border-violet-500/20',
        badgeColor: 'bg-violet-500/10 text-violet-300 border-violet-500/20',
    },
    {
        key: 'frontend',
        label: 'Frontend Technologies',
        icon: Layout,
        color: 'from-blue-500/15 to-cyan-500/15 text-blue-400 border-blue-500/20',
        badgeColor: 'bg-blue-500/10 text-blue-300 border-blue-500/20',
    },
    {
        key: 'backend',
        label: 'Backend Technologies',
        icon: Server,
        color: 'from-emerald-500/15 to-teal-500/15 text-emerald-400 border-emerald-500/20',
        badgeColor: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20',
    },
    {
        key: 'databases',
        label: 'Databases',
        icon: Database,
        color: 'from-amber-500/15 to-yellow-500/15 text-amber-400 border-amber-500/20',
        badgeColor: 'bg-amber-500/10 text-amber-300 border-amber-500/20',
    },
    {
        key: 'data_analytics',
        label: 'Data Analytics & BI',
        icon: BarChart3,
        color: 'from-pink-500/15 to-rose-500/15 text-pink-400 border-pink-500/20',
        badgeColor: 'bg-pink-500/10 text-pink-300 border-pink-500/20',
    },
    {
        key: 'machine_learning',
        label: 'Machine Learning',
        icon: Brain,
        color: 'from-indigo-500/15 to-blue-500/15 text-indigo-400 border-indigo-500/20',
        badgeColor: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20',
    },
    {
        key: 'deep_learning',
        label: 'Deep Learning & AI',
        icon: Cpu,
        color: 'from-fuchsia-500/15 to-pink-500/15 text-fuchsia-400 border-fuchsia-500/20',
        badgeColor: 'bg-fuchsia-500/10 text-fuchsia-300 border-fuchsia-500/20',
    },
    {
        key: 'cloud_devops',
        label: 'Cloud & DevOps',
        icon: Cloud,
        color: 'from-sky-500/15 to-cyan-500/15 text-sky-400 border-sky-500/20',
        badgeColor: 'bg-sky-500/10 text-sky-300 border-sky-500/20',
    },
    {
        key: 'tools',
        label: 'Tools & Platforms',
        icon: Wrench,
        color: 'from-orange-500/15 to-amber-500/15 text-orange-400 border-orange-500/20',
        badgeColor: 'bg-orange-500/10 text-orange-300 border-orange-500/20',
    },
    {
        key: 'other',
        label: 'Other Concepts',
        icon: Boxes,
        color: 'from-slate-500/15 to-gray-500/15 text-slate-400 border-slate-500/20',
        badgeColor: 'bg-slate-500/10 text-slate-300 border-slate-500/20',
    },
]

export default function SkillsOverview({ skills }) {
    const [searchTerm, setSearchTerm] = useState('')
    const [activeTab, setActiveTab] = useState('all')

    // Calculate unique total skills
    const totalSkillsCount = useMemo(() => {
        if (!skills) return 0
        const allSkills = new Set()
        Object.values(skills).forEach((list) => {
            if (Array.isArray(list)) {
                list.forEach((s) => allSkills.add(s.toLowerCase()))
            }
        })
        return allSkills.size
    }, [skills])

    // Filter categories based on search
    const filteredCategories = useMemo(() => {
        if (!skills) return []

        return CATEGORY_CONFIG.map((cfg) => {
            const rawList = skills[cfg.key] || []
            const matchingSkills = rawList.filter((skill) =>
                skill.toLowerCase().includes(searchTerm.toLowerCase().trim())
            )
            return {
                ...cfg,
                skills: matchingSkills,
                totalCount: rawList.length,
            }
        }).filter((cfg) => {
            if (activeTab === 'non_empty') return cfg.skills.length > 0
            if (searchTerm) return cfg.skills.length > 0
            return true
        })
    }, [skills, searchTerm, activeTab])

    return (
        <div className="glass-card p-6 sm:p-8">
            {/* Header & stats */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <Layers size={20} />
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <h3 className="text-lg font-bold text-[var(--text-primary)]">
                                Technical Skills Intelligence
                            </h3>
                            <span className="inline-flex items-center rounded-full bg-[var(--accent)] px-2.5 py-0.5 text-xs font-bold text-white shadow-sm">
                                {totalSkillsCount} Detected
                            </span>
                        </div>
                        <p className="text-xs text-[var(--text-muted)]">
                            Categorized across 10 software engineering domains
                        </p>
                    </div>
                </div>

                {/* Search & filter controls */}
                <div className="flex flex-wrap items-center gap-2">
                    <div className="relative flex-1 sm:w-56">
                        <Search
                            size={14}
                            className="absolute top-1/2 left-3 -translate-y-1/2 text-[var(--text-muted)]"
                        />
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Filter skills..."
                            className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] py-2 pr-3 pl-8 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] transition-all focus:border-[var(--accent)] focus:outline-none"
                        />
                    </div>

                    <button
                        type="button"
                        onClick={() =>
                            setActiveTab((prev) => (prev === 'all' ? 'non_empty' : 'all'))
                        }
                        className={`rounded-xl border px-3 py-2 text-xs font-medium transition-all ${
                            activeTab === 'non_empty'
                                ? 'border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent)]'
                                : 'border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]'
                        }`}
                    >
                        {activeTab === 'non_empty' ? 'Show All Domains' : 'Hide Empty'}
                    </button>
                </div>
            </div>

            {/* Categories Grid */}
            <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
                {filteredCategories.map((cat) => {
                    const Icon = cat.icon
                    const hasSkills = cat.skills.length > 0

                    return (
                        <div
                            key={cat.key}
                            className="flex flex-col justify-between rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 sm:p-5 transition-all hover:border-[var(--border)]/80 hover:shadow-sm"
                        >
                            <div>
                                <div className="mb-3 flex items-center justify-between">
                                    <div className="flex items-center gap-2.5">
                                        <div
                                            className={`flex h-8 w-8 items-center justify-center rounded-lg border bg-gradient-to-br ${cat.color}`}
                                        >
                                            <Icon size={16} />
                                        </div>
                                        <h4 className="text-sm font-semibold text-[var(--text-primary)]">
                                            {cat.label}
                                        </h4>
                                    </div>
                                    <span className="rounded-md bg-[var(--surface-hover)] px-2 py-0.5 text-xs font-mono font-medium text-[var(--text-muted)]">
                                        {cat.totalCount}
                                    </span>
                                </div>

                                {hasSkills ? (
                                    <div className="flex flex-wrap gap-1.5 pt-1">
                                        {cat.skills.map((skill) => (
                                            <span
                                                key={skill}
                                                className={`inline-flex items-center rounded-lg border px-2.5 py-1 text-xs font-medium transition-all hover:scale-105 ${cat.badgeColor}`}
                                            >
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="pt-1 text-xs text-[var(--text-muted)] italic">
                                        No skills detected in this category.
                                    </p>
                                )}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

