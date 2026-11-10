import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Sliders,
    X,
    Check,
    AlertCircle,
} from 'lucide-react'
import { getLearningPreferences, updateLearningPreferences } from '../../services/learningService'

export default function RoadmapPreferencesModal({
    isOpen,
    onClose,
    onSaved,
}) {
    const [preferences, setPreferences] = useState({
        daily_learning_hours: 2.0,
        learning_objective: '',
        preferred_learning_style: 'Hands-on projects & Documentation',
        preferred_language: 'English',
        interview_preparation_type: 'Coding & Architecture',
    })
    const [isLoading, setIsLoading] = useState(false)
    const [isSaving, setIsSaving] = useState(false)
    const [errorMessage, setErrorMessage] = useState(null)
    const [successMessage, setSuccessMessage] = useState(null)

    useEffect(() => {
        if (!isOpen) return
        let isMounted = true

        async function fetchPrefs() {
            setIsLoading(true)
            setErrorMessage(null)
            setSuccessMessage(null)
            try {
                const data = await getLearningPreferences()
                if (!isMounted) return
                if (data) {
                    setPreferences({
                        daily_learning_hours: data.daily_learning_hours || 2.0,
                        learning_objective: data.learning_objective || '',
                        preferred_learning_style: data.preferred_learning_style || 'Hands-on projects & Documentation',
                        preferred_language: data.preferred_language || 'English',
                        interview_preparation_type: data.interview_preparation_type || 'Coding & Architecture',
                    })
                }
            } catch (err) {
                if (!isMounted) return
                console.error('Failed to load learning preferences:', err)
                setErrorMessage('Unable to load preferences.')
            } finally {
                if (isMounted) setIsLoading(false)
            }
        }

        fetchPrefs()

        return () => {
            isMounted = false
        }
    }, [isOpen])

    if (!isOpen) return null

    const handleSave = async (e) => {
        e.preventDefault()
        setIsSaving(true)
        setErrorMessage(null)
        setSuccessMessage(null)

        try {
            const updated = await updateLearningPreferences({
                daily_learning_hours: Number(preferences.daily_learning_hours),
                learning_objective: preferences.learning_objective || null,
                preferred_learning_style: preferences.preferred_learning_style || null,
                preferred_language: preferences.preferred_language || 'English',
                interview_preparation_type: preferences.interview_preparation_type || null,
            })
            setSuccessMessage('Study preferences saved successfully!')
            if (onSaved) onSaved(updated)
            setTimeout(() => {
                onClose()
            }, 800)
        } catch (err) {
            console.error('Failed to save preferences:', err)
            setErrorMessage(err.userMessage || 'Failed to save preferences.')
        } finally {
            setIsSaving(false)
        }
    }

    const hourPresets = [1.0, 1.5, 2.0, 3.0, 4.0]

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />

                {/* Modal Window */}
                <motion.div
                    initial={{ scale: 0.95, opacity: 0, y: 10 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.95, opacity: 0, y: 10 }}
                    className="relative w-full max-w-md rounded-3xl border border-[var(--border)] bg-[var(--surface-card)] p-6 shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="flex items-start justify-between pb-4 border-b border-[var(--border)]">
                        <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/20">
                                <Sliders size={18} />
                            </div>
                            <div>
                                <h3 className="text-base font-bold text-[var(--text-primary)]">
                                    Learning Preferences
                                </h3>
                                <p className="text-xs text-[var(--text-secondary)]">
                                    Customize daily study goals and preferred educational styles
                                </p>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={onClose}
                            className="rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                        >
                            <X size={15} />
                        </button>
                    </div>

                    {/* Alerts */}
                    {errorMessage && (
                        <div className="mt-3.5 flex items-center gap-2 rounded-xl border border-rose-500/20 bg-rose-500/10 p-2.5 text-xs text-rose-600 dark:text-rose-400">
                            <AlertCircle size={15} className="shrink-0" />
                            <span>{errorMessage}</span>
                        </div>
                    )}
                    {successMessage && (
                        <div className="mt-3.5 flex items-center gap-2 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-2.5 text-xs text-emerald-600 dark:text-emerald-400">
                            <Check size={15} className="shrink-0" />
                            <span>{successMessage}</span>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSave} className="mt-4 space-y-4">
                        {/* Daily Learning Hours */}
                        <div>
                            <div className="flex items-center justify-between mb-1.5">
                                <label className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                                    Daily Study Commitment
                                </label>
                                <span className="text-xs font-bold text-[var(--accent)]">
                                    {preferences.daily_learning_hours} hrs / day
                                </span>
                            </div>
                            <div className="grid grid-cols-5 gap-1.5">
                                {hourPresets.map((h) => (
                                    <button
                                        key={h}
                                        type="button"
                                        onClick={() => setPreferences({ ...preferences, daily_learning_hours: h })}
                                        className={`rounded-xl border py-1.5 text-xs font-semibold cursor-pointer transition-all ${
                                            preferences.daily_learning_hours === h
                                                ? 'border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent)] shadow-sm'
                                                : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]'
                                        }`}
                                    >
                                        {h}h
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Preferred Learning Style */}
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] mb-1.5">
                                Preferred Learning Style
                            </label>
                            <select
                                value={preferences.preferred_learning_style}
                                onChange={(e) => setPreferences({ ...preferences, preferred_learning_style: e.target.value })}
                                className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-xs text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                            >
                                <option value="Hands-on projects & Documentation">Hands-on projects & Official Documentation</option>
                                <option value="Interactive Tutorials & Coding Exercises">Interactive Tutorials & Coding Exercises</option>
                                <option value="Deep-Dive Architecture & Articles">Deep-Dive Architecture & Case Studies</option>
                                <option value="Video Lectures & Code Alongs">Video Lectures & Code Alongs</option>
                            </select>
                        </div>

                        {/* Primary Career Goal / Objective */}
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] mb-1.5">
                                Learning Objective
                            </label>
                            <input
                                type="text"
                                value={preferences.learning_objective}
                                onChange={(e) => setPreferences({ ...preferences, learning_objective: e.target.value })}
                                placeholder="e.g. Master Production Backend & Cloud Deployment"
                                className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none"
                            />
                        </div>

                        {/* Interview Prep Focus */}
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] mb-1.5">
                                Interview Prep Focus
                            </label>
                            <select
                                value={preferences.interview_preparation_type}
                                onChange={(e) => setPreferences({ ...preferences, interview_preparation_type: e.target.value })}
                                className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-xs text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                            >
                                <option value="Coding & Architecture">Coding & System Architecture</option>
                                <option value="Algorithms & Data Structures">Algorithms & Data Structures (LeetCode)</option>
                                <option value="System Design & Scalability">System Design & Scalability</option>
                                <option value="Full Stack Mastery">Full Stack Practical Implementation</option>
                            </select>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-[var(--border)]">
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={isSaving}
                                className="rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] px-4 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isSaving || isLoading}
                                className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--primary-purple)] px-4 py-2 text-xs font-bold text-white shadow-md hover:opacity-90 transition-all cursor-pointer disabled:opacity-50"
                            >
                                {isSaving ? (
                                    <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                ) : (
                                    <Check size={14} />
                                )}
                                Save Preferences
                            </button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </AnimatePresence>
    )
}
