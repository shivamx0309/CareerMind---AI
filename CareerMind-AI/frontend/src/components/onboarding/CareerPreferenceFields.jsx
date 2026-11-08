import { useState } from 'react'
import { MapPin, X, Plus } from 'lucide-react'

const JOB_TYPE_OPTIONS = ['Full-time', 'Internship', 'Contract', 'Part-time']
const WORK_MODE_OPTIONS = ['Remote', 'Hybrid', 'On-site']
const SUGGESTED_LOCATIONS = ['Remote', 'Bangalore', 'San Francisco', 'New York', 'London', 'Hyderabad', 'Pune']

export default function CareerPreferenceFields({ formData, onChange, errors = {}, hideHeader = false }) {
    const [newLocationInput, setNewLocationInput] = useState('')

    const locations = Array.isArray(formData.preferred_locations) ? formData.preferred_locations : []

    const handleAddLocation = (loc) => {
        const trimmed = loc.trim()
        if (!trimmed) return
        if (!locations.some((l) => l.toLowerCase() === trimmed.toLowerCase())) {
            onChange('preferred_locations', [...locations, trimmed])
        }
        setNewLocationInput('')
    }

    const handleRemoveLocation = (indexToRemove) => {
        onChange(
            'preferred_locations',
            locations.filter((_, idx) => idx !== indexToRemove)
        )
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault()
            handleAddLocation(newLocationInput)
        }
    }

    return (
        <section className="space-y-4">
            {!hideHeader && (
                <div className="border-b border-[var(--border)] pb-2.5">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--accent)] flex items-center gap-2">
                        <span>Career Preferences</span>
                    </h3>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Target designations and working styles to tailor matching and intelligence.
                    </p>
                </div>
            )}

            {/* Primary Target Role */}
            <div className="space-y-1.5">
                <label htmlFor="primary_target_role" className="block text-xs font-semibold text-[var(--text-primary)]">
                    Primary Target Role <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                    <input
                        id="primary_target_role"
                        type="text"
                        name="primary_target_role"
                        value={formData.primary_target_role}
                        onChange={(e) => onChange('primary_target_role', e.target.value)}
                        placeholder="e.g. Full Stack Developer, Python Backend Engineer, ML Specialist"
                        maxLength={150}
                        className={`w-full rounded-xl border bg-[var(--surface-solid)] px-3.5 py-2.5 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none transition-all ${
                            errors.primary_target_role
                                ? 'border-rose-500 focus:border-rose-500'
                                : 'border-[var(--border)] focus:border-[var(--accent)]'
                        }`}
                    />
                </div>
                {errors.primary_target_role && (
                    <p className="text-[11px] font-medium text-rose-500">{errors.primary_target_role}</p>
                )}
            </div>

            {/* Job Type & Work Mode */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {/* Preferred Job Type */}
                <div className="space-y-1.5">
                    <label className="block text-xs font-semibold text-[var(--text-primary)]">
                        Preferred Job Type <span className="text-rose-500">*</span>
                    </label>
                    <div className="flex flex-wrap gap-2">
                        {JOB_TYPE_OPTIONS.map((jt) => {
                            const isSelected = formData.preferred_job_type === jt
                            return (
                                <button
                                    key={jt}
                                    type="button"
                                    onClick={() => onChange('preferred_job_type', jt)}
                                    className={`rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                                        isSelected
                                            ? 'border-[var(--accent)] bg-[var(--accent)] text-white shadow-sm'
                                            : 'border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-secondary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
                                    }`}
                                >
                                    {jt}
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* Preferred Work Mode */}
                <div className="space-y-1.5">
                    <label className="block text-xs font-semibold text-[var(--text-primary)]">
                        Preferred Work Mode <span className="text-rose-500">*</span>
                    </label>
                    <div className="flex flex-wrap gap-2">
                        {WORK_MODE_OPTIONS.map((wm) => {
                            const isSelected = formData.preferred_work_mode === wm
                            return (
                                <button
                                    key={wm}
                                    type="button"
                                    onClick={() => onChange('preferred_work_mode', wm)}
                                    className={`rounded-xl border px-3 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                                        isSelected
                                            ? 'border-indigo-500 bg-indigo-500 text-white shadow-sm'
                                            : 'border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-secondary)] hover:border-[var(--border-hover)] hover:text-[var(--text-primary)]'
                                    }`}
                                >
                                    {wm}
                                </button>
                            )
                        })}
                    </div>
                </div>
            </div>

            {/* Preferred Locations (Chips / Tag input) */}
            <div className="space-y-2">
                <label className="block text-xs font-semibold text-[var(--text-primary)]">
                    Preferred Locations (Add multiple)
                </label>

                {/* Selected location chips */}
                {locations.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                        {locations.map((loc, idx) => (
                            <span
                                key={idx}
                                className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface-hover)] px-2.5 py-1 text-xs text-[var(--text-primary)]"
                            >
                                <MapPin size={11} className="text-[var(--accent)]" />
                                <span>{loc}</span>
                                <button
                                    type="button"
                                    onClick={() => handleRemoveLocation(idx)}
                                    className="ml-0.5 text-[var(--text-muted)] hover:text-rose-400 transition-colors cursor-pointer"
                                    title={`Remove ${loc}`}
                                >
                                    <X size={12} />
                                </button>
                            </span>
                        ))}
                    </div>
                )}

                {/* Input row */}
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newLocationInput}
                        onChange={(e) => setNewLocationInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type a city or region and press Enter..."
                        className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none"
                    />
                    <button
                        type="button"
                        onClick={() => handleAddLocation(newLocationInput)}
                        className="inline-flex items-center gap-1 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-2 text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                    >
                        <Plus size={14} />
                        <span>Add</span>
                    </button>
                </div>

                {/* Quick suggestions */}
                <div className="flex flex-wrap items-center gap-1 pt-1 text-[11px] text-[var(--text-muted)]">
                    <span>Suggestions:</span>
                    {SUGGESTED_LOCATIONS.map((sug) => {
                        const isAdded = locations.some((l) => l.toLowerCase() === sug.toLowerCase())
                        if (isAdded) return null
                        return (
                            <button
                                key={sug}
                                type="button"
                                onClick={() => handleAddLocation(sug)}
                                className="rounded bg-[var(--surface-solid)] border border-[var(--border)] px-1.5 py-0.5 text-[10px] text-[var(--text-secondary)] hover:text-[var(--accent)] hover:border-[var(--accent)] transition-all cursor-pointer"
                            >
                                + {sug}
                            </button>
                        )
                    })}
                </div>
            </div>

            {/* Career Objective (Optional) */}
            <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                    <label htmlFor="career_objective" className="block text-xs font-semibold text-[var(--text-primary)]">
                        Career Objective <span className="text-[var(--text-muted)] font-normal">(Optional)</span>
                    </label>
                    <span className="text-[10px] text-[var(--text-muted)]">
                        {formData.career_objective?.length || 0} / 2000
                    </span>
                </div>
                <textarea
                    id="career_objective"
                    name="career_objective"
                    rows={3}
                    value={formData.career_objective || ''}
                    onChange={(e) => onChange('career_objective', e.target.value)}
                    placeholder="Briefly describe your career aspirations, key areas of interest, or goals..."
                    maxLength={2000}
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2.5 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none transition-all leading-relaxed"
                />
            </div>
        </section>
    )
}
