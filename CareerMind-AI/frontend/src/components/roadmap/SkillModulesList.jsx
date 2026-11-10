import { useState, useMemo } from 'react'
import {
    Flame,
    Zap,
    Sparkles,
    CheckCircle2,
    Clock,
    Search,
    ChevronDown,
    ChevronUp,
    FolderGit2,
    ListChecks,
} from 'lucide-react'
import { getCategoryMeta } from '../../utils/skillCategoryConfig'
import TopicCard from './TopicCard'
import ConfirmModal from './ConfirmModal'

export default function SkillModulesList({
    skills = [],
    roadmapId,
    onUpdateTopicStatus,
    onUpdateSkillStatus,
    updatingTopicId = null,
    updatingSkillId = null,
}) {
    const [filterPriority, setFilterPriority] = useState('all') // 'all' | 'high' | 'medium' | 'low' | 'completed' | 'in_progress'
    const [searchQuery, setSearchQuery] = useState('')
    const [collapsedSkills, setCollapsedSkills] = useState({})
    const [confirmModalSkill, setConfirmModalSkill] = useState(null)

    const toggleSkillCollapse = (skillId) => {
        setCollapsedSkills((prev) => ({
            ...prev,
            [skillId]: !prev[skillId],
        }))
    }

    const filteredSkills = useMemo(() => {
        return skills.filter((skill) => {
            // Priority / Status filter
            if (filterPriority === 'high' && skill.priority !== 'high') return false
            if (filterPriority === 'medium' && skill.priority !== 'medium') return false
            if (filterPriority === 'low' && skill.priority !== 'low') return false
            if (filterPriority === 'completed' && skill.status !== 'completed') return false
            if (filterPriority === 'in_progress' && skill.status !== 'in_progress') return false

            // Search query filter
            if (searchQuery.trim()) {
                const q = searchQuery.toLowerCase().trim()
                const matchesSkill = skill.skill_name.toLowerCase().includes(q)
                const matchesCategory = skill.category.toLowerCase().includes(q)
                const matchesTopic = skill.topics?.some((t) => t.topic_name.toLowerCase().includes(q))
                return matchesSkill || matchesCategory || matchesTopic
            }

            return true
        })
    }, [skills, filterPriority, searchQuery])

    // Group counts
    const highCount = skills.filter((s) => s.priority === 'high').length
    const mediumCount = skills.filter((s) => s.priority === 'medium').length
    const lowCount = skills.filter((s) => s.priority === 'low').length

    const handleConfirmSkillComplete = async () => {
        if (!confirmModalSkill) return
        try {
            await onUpdateSkillStatus(confirmModalSkill.id, 'completed')
        } finally {
            setConfirmModalSkill(null)
        }
    }

    return (
        <div className="space-y-6">
            {/* Header & Filter Controls */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)]">
                        Curated Skill Modules
                    </h3>
                    <p className="text-xs text-[var(--text-secondary)]">
                        Structured learning modules prioritized by role criticality and dependency prerequisites
                    </p>
                </div>

                {/* Filter Pills */}
                <div className="flex flex-wrap items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] p-1">
                    {[
                        { key: 'all', label: `All (${skills.length})` },
                        { key: 'high', label: `High (${highCount})` },
                        { key: 'medium', label: `Medium (${mediumCount})` },
                        { key: 'low', label: `Low (${lowCount})` },
                        { key: 'in_progress', label: 'In Progress' },
                        { key: 'completed', label: 'Completed' },
                    ].map((tab) => (
                        <button
                            key={tab.key}
                            type="button"
                            onClick={() => setFilterPriority(tab.key)}
                            className={`rounded-lg px-3 py-1 text-xs font-semibold transition-all cursor-pointer ${
                                filterPriority === tab.key
                                    ? 'bg-[var(--surface-card)] text-[var(--accent)] shadow-sm'
                                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                            }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Search Bar */}
            <div className="relative">
                <Search
                    size={15}
                    className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
                />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search skills, topics, or categories (e.g. Docker, PostgreSQL, APIs)..."
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] py-2.5 pl-10 pr-4 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none transition-all"
                />
                {searchQuery && (
                    <button
                        type="button"
                        onClick={() => setSearchQuery('')}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-[var(--text-muted)] hover:text-[var(--text-primary)] cursor-pointer"
                    >
                        Clear
                    </button>
                )}
            </div>

            {/* Modules List */}
            {filteredSkills.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface-card)] p-8 text-center">
                    <p className="text-sm font-semibold text-[var(--text-secondary)]">
                        No skill modules match the selected filter or search term.
                    </p>
                </div>
            ) : (
                <div className="space-y-5">
                    {filteredSkills.map((skill) => {
                        const catMeta = getCategoryMeta(skill.category)
                        const CatIcon = catMeta.icon
                        const isCollapsed = Boolean(collapsedSkills[skill.id])
                        const isSkillCompleted = skill.status === 'completed'
                        const isSkillInProgress = skill.status === 'in_progress'

                        const completedTopics = (skill.topics || []).filter((t) => t.status === 'completed').length
                        const totalTopics = (skill.topics || []).length

                        return (
                            <div
                                key={skill.id}
                                className={`rounded-2xl border transition-all ${
                                    isSkillCompleted
                                        ? 'border-emerald-500/25 bg-emerald-500/[0.02] dark:bg-emerald-500/[0.03]'
                                        : isSkillInProgress
                                        ? 'border-amber-500/30 bg-amber-500/[0.015] dark:bg-amber-500/[0.03]'
                                        : 'border-[var(--border)] bg-[var(--surface-card)]'
                                }`}
                            >
                                {/* Module Header Card */}
                                <div className="p-5">
                                    <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                                        <div className="flex items-start gap-3">
                                            {/* Priority Indicator Icon */}
                                            <div
                                                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border ${
                                                    skill.priority === 'high'
                                                        ? 'border-rose-500/25 bg-rose-500/10 text-rose-600 dark:text-rose-400'
                                                        : skill.priority === 'medium'
                                                        ? 'border-amber-500/25 bg-amber-500/10 text-amber-600 dark:text-amber-400'
                                                        : 'border-sky-500/25 bg-sky-500/10 text-sky-600 dark:text-sky-400'
                                                }`}
                                            >
                                                {skill.priority === 'high' ? (
                                                    <Flame size={22} />
                                                ) : skill.priority === 'medium' ? (
                                                    <Zap size={22} />
                                                ) : (
                                                    <Sparkles size={22} />
                                                )}
                                            </div>

                                            <div>
                                                <div className="flex flex-wrap items-center gap-2">
                                                    <h4 className="text-base font-bold text-[var(--text-primary)]">
                                                        {skill.skill_name}
                                                    </h4>

                                                    {/* Category Pill */}
                                                    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${catMeta.badgeClass}`}>
                                                        <CatIcon size={11} />
                                                        {catMeta.label}
                                                    </span>

                                                    {/* Priority Badge */}
                                                    <span
                                                        className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                                                            skill.priority === 'high'
                                                                ? 'border border-rose-500/30 bg-rose-500/15 text-rose-700 dark:text-rose-300'
                                                                : skill.priority === 'medium'
                                                                ? 'border border-amber-500/30 bg-amber-500/15 text-amber-800 dark:text-amber-300'
                                                                : 'border border-sky-500/30 bg-sky-500/15 text-sky-700 dark:text-sky-300'
                                                        }`}
                                                    >
                                                        {skill.priority} Priority
                                                    </span>

                                                    {/* Gap Type Badge */}
                                                    <span className="rounded-full border border-[var(--border)] bg-[var(--surface-hover)] px-2.5 py-0.5 text-[10px] font-medium text-[var(--text-secondary)]">
                                                        {skill.gap_type === 'missing_required'
                                                            ? 'Missing Core'
                                                            : skill.gap_type === 'related_required'
                                                            ? 'Bridge Learning'
                                                            : 'Bonus Preferred'}
                                                    </span>
                                                </div>

                                                <p className="mt-1.5 text-xs text-[var(--text-secondary)] leading-relaxed">
                                                    {skill.rationale}
                                                </p>

                                                {/* Prerequisites List */}
                                                {skill.prerequisites && skill.prerequisites.length > 0 && (
                                                    <div className="mt-2 flex flex-wrap items-center gap-1.5 text-[11px]">
                                                        <span className="font-semibold text-[var(--text-muted)]">Prerequisites:</span>
                                                        {skill.prerequisites.map((p) => (
                                                            <span
                                                                key={p}
                                                                className="rounded-md border border-[var(--border)] bg-[var(--surface)] px-2 py-0.5 font-mono text-[10px] text-[var(--text-secondary)]"
                                                            >
                                                                {p}
                                                            </span>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Right Action / Progress Pill */}
                                        <div className="flex flex-wrap items-center gap-2.5 self-end lg:self-center">
                                            <div className="text-right">
                                                <div className="text-xs font-semibold text-[var(--text-primary)]">
                                                    {completedTopics} of {totalTopics} Topics
                                                </div>
                                                <div className="flex items-center gap-1 text-[11px] text-[var(--text-secondary)]">
                                                    <Clock size={11} />
                                                    {skill.estimated_hours}h estimated
                                                </div>
                                            </div>

                                            {/* Mark Skill Complete Action */}
                                            {!isSkillCompleted ? (
                                                <button
                                                    type="button"
                                                    onClick={() => setConfirmModalSkill(skill)}
                                                    disabled={updatingSkillId === skill.id}
                                                    className="inline-flex items-center gap-1.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/20 transition-all cursor-pointer disabled:opacity-50"
                                                >
                                                    <CheckCircle2 size={13} />
                                                    Mark Mastered
                                                </button>
                                            ) : (
                                                <span className="inline-flex items-center gap-1 rounded-xl border border-emerald-500/30 bg-emerald-500/15 px-3 py-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-300">
                                                    <CheckCircle2 size={13} />
                                                    Mastered
                                                </span>
                                            )}

                                            {/* Collapse Toggle */}
                                            <button
                                                type="button"
                                                onClick={() => toggleSkillCollapse(skill.id)}
                                                className="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                                                aria-label={isCollapsed ? 'Expand module' : 'Collapse module'}
                                            >
                                                {isCollapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {/* Collapsible Body: Practical Project & Topics */}
                                {!isCollapsed && (
                                    <div className="border-t border-[var(--border)] p-5 space-y-4 bg-[var(--surface-card)]/50 rounded-b-2xl">
                                        {/* Practical Mini-Project */}
                                        {skill.practical_project && (
                                            <div className="rounded-xl border border-[var(--accent)]/20 bg-[var(--accent-soft)] p-4">
                                                <div className="flex items-start gap-3">
                                                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[var(--accent)] text-white">
                                                        <FolderGit2 size={16} />
                                                    </div>
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2">
                                                            <span className="rounded-full bg-[var(--accent)]/15 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[var(--accent)]">
                                                                Hands-on Mini-Project
                                                            </span>
                                                            <h5 className="text-xs font-bold text-[var(--text-primary)]">
                                                                {skill.practical_project.title}
                                                            </h5>
                                                        </div>
                                                        <p className="mt-1 text-xs text-[var(--text-secondary)] leading-relaxed">
                                                            {skill.practical_project.description}
                                                        </p>

                                                        {/* Project Deliverables */}
                                                        {skill.practical_project.deliverables && skill.practical_project.deliverables.length > 0 && (
                                                            <div className="mt-2.5">
                                                                <div className="flex items-center gap-1 text-[11px] font-semibold text-[var(--text-primary)]">
                                                                    <ListChecks size={13} className="text-[var(--accent)]" />
                                                                    Deliverables to Build:
                                                                </div>
                                                                <ul className="mt-1 grid grid-cols-1 gap-1 sm:grid-cols-2 text-[11px] text-[var(--text-secondary)]">
                                                                    {skill.practical_project.deliverables.map((item, idx) => (
                                                                        <li key={idx} className="flex items-center gap-1.5">
                                                                            <span className="h-1.5 w-1.5 rounded-full bg-[var(--accent)]" />
                                                                            <span>{item}</span>
                                                                        </li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Topics Syllabus */}
                                        <div className="space-y-2.5">
                                            <div className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                                                Syllabus Lessons & Verified Free Resources
                                            </div>
                                            {skill.topics && skill.topics.length > 0 ? (
                                                skill.topics.map((topic) => (
                                                    <TopicCard
                                                        key={topic.id}
                                                        topic={topic}
                                                        roadmapId={roadmapId}
                                                        onStatusChange={onUpdateTopicStatus}
                                                        isUpdating={updatingTopicId === topic.id}
                                                    />
                                                ))
                                            ) : (
                                                <p className="text-xs text-[var(--text-muted)] italic">
                                                    No granular lessons defined.
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            )}

            {/* Confirmation Dialog for Skill Completion */}
            <ConfirmModal
                isOpen={Boolean(confirmModalSkill)}
                title="Mark Entire Skill as Mastered?"
                message={`Marking "${confirmModalSkill?.skill_name}" as Mastered will automatically mark all ${confirmModalSkill?.topics?.length || 0} associated lesson topics as Completed.`}
                confirmText="Yes, Mark Mastered"
                confirmVariant="primary"
                isLoading={updatingSkillId === confirmModalSkill?.id}
                onConfirm={handleConfirmSkillComplete}
                onCancel={() => setConfirmModalSkill(null)}
            />
        </div>
    )
}
