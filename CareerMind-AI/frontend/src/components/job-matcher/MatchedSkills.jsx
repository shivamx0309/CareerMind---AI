import { useState } from 'react'
import {
    CheckCircle2,
    Sparkles,
    Search,
    Code,
    Layers,
} from 'lucide-react'

function formatEvidenceSource(source) {
    if (!source) return 'Candidate Profile'
    switch (source) {
        case 'technical_skills':
            return 'Technical Skills'
        case 'experience':
            return 'Work Experience'
        case 'internship':
            return 'Internship'
        case 'projects':
            return 'Projects'
        case 'certifications':
            return 'Certifications'
        default:
            return source.replace('_', ' ')
    }
}

export default function MatchedSkills({ matchedSkills = [] }) {
    const [filter, setFilter] = useState('all') // 'all' | 'exact' | 'alias'
    const [searchQuery, setSearchQuery] = useState('')

    // Filter strictly exact matches and canonical alias matches (related skills are handled separately)
    const exactAndAliasList = matchedSkills.filter(
        (item) => item.status === 'exact_match' || item.status === 'alias_match'
    )

    const filteredList = exactAndAliasList.filter((item) => {
        if (filter === 'exact' && item.status !== 'exact_match') return false
        if (filter === 'alias' && item.status !== 'alias_match') return false
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase()
            return (
                item.skill.toLowerCase().includes(q) ||
                (item.candidate_evidence && item.candidate_evidence.toLowerCase().includes(q))
            )
        }
        return true
    })

    const exactCount = exactAndAliasList.filter((i) => i.status === 'exact_match').length
    const aliasCount = exactAndAliasList.filter((i) => i.status === 'alias_match').length

    return (
        <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border)] pb-4">
                <div>
                    <div className="flex items-center gap-2">
                        <CheckCircle2 size={18} className="text-emerald-600 dark:text-emerald-400" />
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Direct Matched Skills
                        </h3>
                        <span className="rounded-full border border-emerald-500/30 bg-emerald-500/15 px-2.5 py-0.5 text-xs font-bold text-emerald-700 dark:text-emerald-300">
                            {exactAndAliasList.length}
                        </span>
                    </div>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Technical requirements matched via verified resume evidence or canonical alias normalization.
                    </p>
                </div>

                {/* Filter Tabs */}
                <div className="flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-1">
                    <button
                        type="button"
                        onClick={() => setFilter('all')}
                        className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                            filter === 'all'
                                ? 'bg-[var(--accent)] text-white shadow-sm'
                                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                        }`}
                    >
                        All ({exactAndAliasList.length})
                    </button>
                    <button
                        type="button"
                        onClick={() => setFilter('exact')}
                        className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                            filter === 'exact'
                                ? 'bg-[var(--accent)] text-white shadow-sm'
                                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                        }`}
                    >
                        Exact ({exactCount})
                    </button>
                    <button
                        type="button"
                        onClick={() => setFilter('alias')}
                        className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                            filter === 'alias'
                                ? 'bg-[var(--accent)] text-white shadow-sm'
                                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                        }`}
                    >
                        Canonical Aliases ({aliasCount})
                    </button>
                </div>
            </div>

            {/* Quick search input if more than 6 skills */}
            {exactAndAliasList.length > 6 && (
                <div className="relative">
                    <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                    <input
                        type="text"
                        placeholder="Search matched skills..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] py-1.5 pl-8 pr-3 text-xs text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                    />
                </div>
            )}

            {filteredList.length === 0 ? (
                <div className="rounded-xl border border-dashed border-[var(--border)] p-8 text-center text-xs text-[var(--text-muted)]">
                    No skills match the selected filter.
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {filteredList.map((item, idx) => {
                        const isAlias = item.status === 'alias_match'

                        return (
                            <div
                                key={`${item.skill}-${idx}`}
                                className="group relative rounded-xl border border-[var(--border)] bg-[var(--surface-solid)]/70 p-4 transition-all hover:border-emerald-500/40 hover:bg-[var(--surface-hover)] flex flex-col justify-between"
                            >
                                <div>
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex items-center gap-1.5">
                                            <Code size={14} className="text-emerald-600 dark:text-emerald-400 shrink-0" />
                                            <h4 className="text-sm font-bold text-[var(--text-primary)]">
                                                {item.skill}
                                            </h4>
                                        </div>

                                        {/* Status badge */}
                                        <span
                                            className={`rounded-full px-2 py-0.5 text-[10px] font-semibold shrink-0 ${
                                                isAlias
                                                    ? 'border border-sky-500/30 bg-sky-500/10 text-sky-700 dark:text-sky-300'
                                                    : 'border border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'
                                            }`}
                                        >
                                            {isAlias ? 'Canonical Alias' : 'Exact Match'}
                                        </span>
                                    </div>

                                    {/* Requirement Type Pill */}
                                    <div className="mt-2 flex items-center gap-2 text-[11px] text-[var(--text-muted)]">
                                        <span className="capitalize font-medium text-[var(--text-secondary)]">
                                            {item.requirement_type || 'Required'}
                                        </span>
                                        <span>•</span>
                                        <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                                            <Sparkles size={11} />
                                            {Math.round((item.match_confidence ?? item.confidence ?? 1.0) * 100)}% match
                                        </span>
                                    </div>

                                    {/* Candidate Evidence */}
                                    {item.candidate_evidence && (
                                        <div className="mt-3 rounded-lg bg-[var(--surface-hover)]/60 p-2 text-xs">
                                            <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] block mb-0.5">
                                                Found In Resume:
                                            </span>
                                            <p className="text-[var(--text-primary)] font-mono text-[11px] truncate" title={item.candidate_evidence}>
                                                "{item.candidate_evidence}"
                                            </p>
                                        </div>
                                    )}

                                    {/* Original JD Phrase */}
                                    {item.original_jd_phrase && (
                                        <div className="mt-2 text-[11px] text-[var(--text-muted)] italic truncate" title={item.original_jd_phrase}>
                                            JD: "{item.original_jd_phrase}"
                                        </div>
                                    )}
                                </div>

                                {/* Source pill footer */}
                                <div className="mt-3 border-t border-[var(--border)] pt-2 flex items-center justify-between text-[11px] text-[var(--text-muted)]">
                                    <span className="flex items-center gap-1">
                                        <Layers size={11} />
                                        <span>{formatEvidenceSource(item.evidence_source)}</span>
                                    </span>
                                    {isAlias && item.relationship_explanation && (
                                        <span className="text-[10px] text-sky-400 truncate max-w-[140px]" title={item.relationship_explanation}>
                                            {item.relationship_explanation}
                                        </span>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
