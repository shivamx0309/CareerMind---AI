import { useState } from 'react'
import {
    X,
    Save,
    RotateCcw,
    AlertCircle,
    Info,
    Plus,
    Tag,
} from 'lucide-react'

const SKILL_CATEGORIES = [
    { key: 'programming_languages', label: 'Programming Languages' },
    { key: 'frontend', label: 'Frontend Technologies' },
    { key: 'backend', label: 'Backend Technologies' },
    { key: 'databases', label: 'Databases' },
    { key: 'data_analytics', label: 'Data Analytics & BI' },
    { key: 'machine_learning', label: 'Machine Learning' },
    { key: 'deep_learning', label: 'Deep Learning & AI' },
    { key: 'cloud_devops', label: 'Cloud & DevOps' },
    { key: 'tools', label: 'Tools & Platforms' },
    { key: 'other', label: 'Other Skills' },
]

export default function ProfileEditor({
    candidate,
    onSave,
    onClose,
    onResetToOriginal,
}) {
    const personal = candidate?.personal_information || {}
    const skills = candidate?.technical_skills || {}

    // Form state
    const [fullName, setFullName] = useState(personal.full_name || '')
    const [email, setEmail] = useState(personal.email || '')
    const [phone, setPhone] = useState(personal.phone || '')
    const [linkedin, setLinkedin] = useState(personal.linkedin || '')
    const [github, setGithub] = useState(personal.github || '')
    const [portfolio, setPortfolio] = useState(personal.portfolio || '')
    const [location, setLocation] = useState(personal.location || '')
    const [summary, setSummary] = useState(candidate?.professional_summary || '')

    // Skills state
    const [skillsMap, setSkillsMap] = useState(() => {
        const copy = {}
        SKILL_CATEGORIES.forEach((c) => {
            copy[c.key] = [...(skills[c.key] || [])]
        })
        return copy
    })

    const [selectedCategory, setSelectedCategory] = useState('programming_languages')
    const [newSkillInput, setNewSkillInput] = useState('')
    const [formError, setFormError] = useState('')

    function handleAddSkill() {
        const trimmed = newSkillInput.trim()
        if (!trimmed) return

        const currentList = skillsMap[selectedCategory] || []
        if (currentList.some((s) => s.toLowerCase() === trimmed.toLowerCase())) {
            setFormError(`"${trimmed}" is already in this category.`)
            return
        }

        setFormError('')
        setSkillsMap((prev) => ({
            ...prev,
            [selectedCategory]: [...prev[selectedCategory], trimmed],
        }))
        setNewSkillInput('')
    }

    function handleRemoveSkill(catKey, skillToRemove) {
        setSkillsMap((prev) => ({
            ...prev,
            [catKey]: prev[catKey].filter((s) => s !== skillToRemove),
        }))
    }

    function validate() {
        if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            return 'Please enter a valid email address.'
        }
        if (linkedin && !linkedin.startsWith('http://') && !linkedin.startsWith('https://')) {
            return 'LinkedIn URL must start with https:// or http://'
        }
        if (github && !github.startsWith('http://') && !github.startsWith('https://')) {
            return 'GitHub URL must start with https:// or http://'
        }
        if (portfolio && !portfolio.startsWith('http://') && !portfolio.startsWith('https://')) {
            return 'Portfolio URL must start with https:// or http://'
        }
        return ''
    }

    function handleSave(e) {
        e.preventDefault()
        const err = validate()
        if (err) {
            setFormError(err)
            return
        }

        const updatedCandidate = {
            ...candidate,
            personal_information: {
                ...personal,
                full_name: fullName.trim() || null,
                email: email.trim() || null,
                phone: phone.trim() || null,
                linkedin: linkedin.trim() || null,
                github: github.trim() || null,
                portfolio: portfolio.trim() || null,
                location: location.trim() || null,
            },
            professional_summary: summary.trim() || null,
            technical_skills: {
                ...skillsMap,
            },
        }

        onSave(updatedCandidate)
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-sm animate-fadeIn">
            <div className="flex max-h-[90vh] w-full max-w-3xl flex-col rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] shadow-2xl overflow-hidden">
                {/* Modal Header */}
                <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4">
                    <div>
                        <h3 className="text-lg font-bold text-[var(--text-primary)]">
                            Edit Candidate Profile
                        </h3>
                        <p className="text-xs text-[var(--text-muted)]">
                            Modify extracted details for this session
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-xl p-2 text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)]"
                        aria-label="Close modal"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Session Notice Banner */}
                <div className="flex items-center gap-2.5 bg-[var(--accent-soft)] px-6 py-2.5 text-xs text-[var(--accent)] border-b border-[var(--accent)]/15">
                    <Info size={16} className="shrink-0" />
                    <span>
                        Edits are preserved in your current browser session. No database write is performed in this milestone.
                    </span>
                </div>

                {/* Form Body */}
                <form id="profile-editor-form" onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-6">
                    {formError && (
                        <div className="flex items-center gap-2 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-xs text-red-400">
                            <AlertCircle size={16} className="shrink-0" />
                            <span>{formError}</span>
                        </div>
                    )}

                    {/* Personal Information */}
                    <div>
                        <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                            Personal & Contact Details
                        </h4>

                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                            <div>
                                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                                    Full Name
                                </label>
                                <input
                                    type="text"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    placeholder="e.g. Jane Doe"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                                    Email Address
                                </label>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="e.g. jane@example.com"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                                    Phone Number
                                </label>
                                <input
                                    type="text"
                                    value={phone}
                                    onChange={(e) => setPhone(e.target.value)}
                                    placeholder="e.g. +91 9876543210"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                                    Location (City, Country)
                                </label>
                                <input
                                    type="text"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                    placeholder="e.g. San Francisco, CA"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                                    LinkedIn Profile URL
                                </label>
                                <input
                                    type="url"
                                    value={linkedin}
                                    onChange={(e) => setLinkedin(e.target.value)}
                                    placeholder="https://linkedin.com/in/username"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                                    GitHub Profile URL
                                </label>
                                <input
                                    type="url"
                                    value={github}
                                    onChange={(e) => setGithub(e.target.value)}
                                    placeholder="https://github.com/username"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                            </div>

                            <div className="sm:col-span-2">
                                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                                    Portfolio / Website URL
                                </label>
                                <input
                                    type="url"
                                    value={portfolio}
                                    onChange={(e) => setPortfolio(e.target.value)}
                                    placeholder="https://myportfolio.dev"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Summary */}
                    <div>
                        <h4 className="mb-2 text-sm font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                            Professional Summary
                        </h4>
                        <textarea
                            rows={4}
                            value={summary}
                            onChange={(e) => setSummary(e.target.value)}
                            placeholder="Enter professional summary or career objective..."
                            className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 text-sm text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none leading-relaxed"
                        />
                    </div>

                    {/* Technical Skills Editor */}
                    <div>
                        <h4 className="mb-2 text-sm font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                            Technical Skills by Category
                        </h4>

                        {/* Category Selector */}
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                            <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-xs font-medium text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                            >
                                {SKILL_CATEGORIES.map((c) => (
                                    <option key={c.key} value={c.key}>
                                        {c.label} ({skillsMap[c.key]?.length || 0})
                                    </option>
                                ))}
                            </select>

                            <div className="flex flex-1 items-center gap-2">
                                <input
                                    type="text"
                                    value={newSkillInput}
                                    onChange={(e) => setNewSkillInput(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            e.preventDefault()
                                            handleAddSkill()
                                        }
                                    }}
                                    placeholder="Add skill tag..."
                                    className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-xs text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                />
                                <button
                                    type="button"
                                    onClick={handleAddSkill}
                                    className="inline-flex items-center gap-1 rounded-xl bg-[var(--accent)] px-3.5 py-2 text-xs font-semibold text-white hover:opacity-90"
                                >
                                    <Plus size={14} /> Add
                                </button>
                            </div>
                        </div>

                        {/* Selected Category Skill Tags */}
                        <div className="mt-3 min-h-[60px] rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-3">
                            <div className="flex flex-wrap gap-2">
                                {(skillsMap[selectedCategory] || []).length > 0 ? (
                                    skillsMap[selectedCategory].map((skill) => (
                                        <span
                                            key={skill}
                                            className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--accent)]/30 bg-[var(--accent-soft)] px-2.5 py-1 text-xs font-medium text-[var(--text-primary)]"
                                        >
                                            <Tag size={12} className="text-[var(--accent)]" />
                                            <span>{skill}</span>
                                            <button
                                                type="button"
                                                onClick={() => handleRemoveSkill(selectedCategory, skill)}
                                                className="text-[var(--text-muted)] hover:text-red-400"
                                                aria-label={`Remove ${skill}`}
                                            >
                                                <X size={12} />
                                            </button>
                                        </span>
                                    ))
                                ) : (
                                    <span className="text-xs text-[var(--text-muted)] italic">
                                        No skills added to this category yet.
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                </form>

                {/* Modal Footer */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[var(--border)] px-6 py-4 bg-[var(--surface-solid)]">
                    <button
                        type="button"
                        onClick={onResetToOriginal}
                        className="inline-flex items-center gap-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                    >
                        <RotateCcw size={14} />
                        <span>Reset to Extracted</span>
                    </button>

                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="rounded-xl border border-[var(--border)] px-4 py-2 text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            form="profile-editor-form"
                            className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-4 py-2 text-xs font-semibold text-white shadow-md hover:opacity-95"
                        >
                            <Save size={14} />
                            <span>Save Session Profile</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}

