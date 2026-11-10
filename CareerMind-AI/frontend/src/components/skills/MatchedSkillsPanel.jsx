import { useState, useMemo } from 'react'
import { CheckCircle2, Search, Tag } from 'lucide-react'
import { getCategoryMeta } from '../../utils/skillCategoryConfig'

export default function MatchedSkillsPanel({ matchedSkills = [] }) {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedCategory, setSelectedCategory] = useState('all')

    // Collect available categories from actual matched skills
    const categories = useMemo(() => {
        const set = new Set()
        matchedSkills.forEach((s) => {
            if (s.category) set.add(s.category)
        })
        return ['all', ...Array.from(set)]
    }, [matchedSkills])

    // Filter matched skills
    const filteredSkills = useMemo(() => {
        return matchedSkills.filter((item) => {
            const matchesSearch =
                !searchQuery ||
                item.skill_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                item.matched_skill?.toLowerCase().includes(searchQuery.toLowerCase())

            const matchesCategory =
                selectedCategory === 'all' || item.category === selectedCategory

            return matchesSearch && matchesCategory
        })
    }, [matchedSkills, searchQuery, selectedCategory])

    if (!matchedSkills || matchedSkills.length === 0) {
        return (
            <div className="glass-card rounded-2xl p-6 text-center space-y-2">
                <CheckCircle2 size={28} className="mx-auto text-[var(--text-muted)]" />
                <h4 className="text-base font-bold text-[var(--text-primary)]">
                    No Matched Skills Detected
                </h4>
                <p className="text-xs text-[var(--text-muted)] max-w-sm mx-auto">
                    No direct or alias skill matches were found between the resume and the benchmark expectations.
                </p>
            </div>
        )
    }

    return (
        <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                        <CheckCircle2 size={18} className="text-[var(--success)]" />
                        <h3 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                            Matched Skills ({matchedSkills.length})
                        </h3>
                    </div>
                    <p className="text-xs text-[var(--text-muted)]">
                        Exact canonical keywords and verified technical aliases detected in candidate profile
                    </p>
                </div>

                {/* Search Bar */}
                <div className="relative w-full sm:w-64">
                    <input
                        type="text"
                        placeholder="Search matched skills..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-1.5 pl-8 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none"
                    />
                    <Search
                        size={14}
                        className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
                    />
                </div>
            </div>

            {/* Category Filter Pills */}
            {categories.length > 2 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                    {categories.map((cat) => {
                        const meta = getCategoryMeta(cat)
                        const isSelected = selectedCategory === cat
                        return (
                            <button
                                key={cat}
                                type="button"
                                onClick={() => setSelectedCategory(cat)}
                                className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all cursor-pointer ${
                                    isSelected
                                        ? 'bg-[var(--accent)] text-white'
                                        : 'bg-[var(--surface-solid)] border border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]'
                                }`}
                            >
                                {cat === 'all' ? 'All Categories' : meta.label}
                            </button>
                        )
                    })}
                </div>
            )}

            {/* Skills List */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-2">
                {filteredSkills.map((item, idx) => {
                    const meta = getCategoryMeta(item.category)
                    const Icon = meta.icon
                    const isAlias = item.status === 'alias_match'

                    return (
                        <div
                            key={`${item.skill_name}-${idx}`}
                            className="flex flex-col justify-between rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 space-y-2 hover:border-[var(--accent)]/40 transition-colors"
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div className="space-y-0.5">
                                    <div className="flex items-center gap-1.5">
                                        <Icon size={14} style={{ color: meta.color }} />
                                        <span className="text-sm font-bold text-[var(--text-primary)]">
                                            {item.skill_name}
                                        </span>
                                    </div>
                                    <span className="text-[10px] text-[var(--text-muted)]">
                                        {meta.label}
                                    </span>
                                </div>

                                <span
                                    className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                                        isAlias
                                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                    }`}
                                >
                                    {isAlias ? 'Alias Match' : 'Exact Match'}
                                </span>
                            </div>

                            {/* Evidence Info */}
                            <div className="flex items-center justify-between text-[11px] pt-1.5 border-t border-[var(--border)]/40 text-[var(--text-muted)]">
                                <span className="capitalize">
                                    {item.importance} Skill
                                </span>
                                {item.evidence_source && (
                                    <span className="inline-flex items-center gap-1 font-medium text-[var(--text-secondary)]">
                                        <Tag size={10} />
                                        <span>Found in: {item.evidence_source}</span>
                                    </span>
                                )}
                            </div>
                        </div>
                    )
                })}
            </div>

            {filteredSkills.length === 0 && (
                <div className="text-center py-6 text-xs text-[var(--text-muted)]">
                    No matched skills match your current search or category filter.
                </div>
            )}
        </div>
    )
}
