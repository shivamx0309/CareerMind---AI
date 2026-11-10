import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Sparkles,
    X,
    Check,
    AlertCircle,
    ArrowRight,
    Briefcase,
} from 'lucide-react'
import { getReports } from '../../services/skillGapService'

export default function RoadmapGeneratorModal({
    isOpen,
    onClose,
    onGenerate,
    defaultWeeklyHours = 10,
    isGenerating = false,
}) {
    const [reports, setReports] = useState([])
    const [isLoadingReports, setIsLoadingReports] = useState(false)
    const [selectedReportId, setSelectedReportId] = useState('')
    const [weeklyHours, setWeeklyHours] = useState(defaultWeeklyHours || 10)
    const [isCustomHours, setIsCustomHours] = useState(false)
    const [customHoursInput, setCustomHoursInput] = useState('12')
    const [roadmapTitle, setRoadmapTitle] = useState('')
    const [errorMessage, setErrorMessage] = useState(null)

    // Load available Skill Gap Reports whenever modal opens
    useEffect(() => {
        if (!isOpen) return

        let isMounted = true

        async function fetchAvailableReports() {
            setIsLoadingReports(true)
            setErrorMessage(null)
            try {
                const data = await getReports()
                if (!isMounted) return
                const validReports = data || []
                setReports(validReports)
                if (validReports.length > 0) {
                    setSelectedReportId(validReports[0].id)
                }
            } catch (err) {
                if (!isMounted) return
                console.error('Failed to load skill gap reports:', err)
                setErrorMessage('Unable to load previous skill gap reports. Please ensure backend is running.')
            } finally {
                if (isMounted) setIsLoadingReports(false)
            }
        }

        fetchAvailableReports()

        return () => {
            isMounted = false
        }
    }, [isOpen])

    if (!isOpen) return null

    const handleSelectPresetHours = (hours) => {
        setIsCustomHours(false)
        setWeeklyHours(hours)
    }

    const handleCustomHoursChange = (val) => {
        setCustomHoursInput(val)
        const num = parseInt(val, 10)
        if (!isNaN(num) && num >= 1 && num <= 60) {
            setWeeklyHours(num)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!selectedReportId) {
            setErrorMessage('Please select a Skill Gap Analysis report to convert into a roadmap.')
            return
        }

        setErrorMessage(null)
        try {
            await onGenerate({
                skill_gap_report_id: selectedReportId,
                weekly_study_hours: weeklyHours,
                title: roadmapTitle.trim() || undefined,
            })
            onClose()
        } catch (err) {
            console.error('Roadmap generation failed:', err)
            setErrorMessage(err.userMessage || 'Failed to generate learning roadmap.')
        }
    }

    const presetHours = [
        { hours: 5, label: '5h / wk', desc: 'Casual' },
        { hours: 10, label: '10h / wk', desc: 'Recommended' },
        { hours: 15, label: '15h / wk', desc: 'Accelerated' },
        { hours: 20, label: '20h / wk', desc: 'Intensive' },
    ]

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
                    className="relative w-full max-w-lg rounded-3xl border border-[var(--border)] bg-[var(--surface-card)] p-6 sm:p-7 shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto"
                >
                    {/* Header */}
                    <div className="flex items-start justify-between pb-4 border-b border-[var(--border)]">
                        <div className="flex items-center gap-3">
                            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] text-white shadow-md shadow-purple-600/20">
                                <Sparkles size={20} />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-[var(--text-primary)]">
                                    Generate Learning Roadmap
                                </h3>
                                <p className="text-xs text-[var(--text-secondary)]">
                                    Convert an assessed Skill Gap Report into an actionable learning curriculum
                                </p>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={onClose}
                            className="rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                        >
                            <X size={16} />
                        </button>
                    </div>

                    {/* Error Banner */}
                    {errorMessage && (
                        <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/10 p-3 text-xs text-rose-600 dark:text-rose-400">
                            <AlertCircle size={16} className="shrink-0 mt-0.5" />
                            <span>{errorMessage}</span>
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="mt-5 space-y-5">
                        {/* 1. Skill Gap Report Selection */}
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] mb-2">
                                1. Select Skill Gap Report
                            </label>

                            {isLoadingReports ? (
                                <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 text-center text-xs text-[var(--text-secondary)]">
                                    Loading your saved Skill Gap Reports...
                                </div>
                            ) : reports.length === 0 ? (
                                <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-hover)] p-4 text-center">
                                    <p className="text-xs text-[var(--text-secondary)]">
                                        No Skill Gap Reports found. You must analyze your resume against a target role before generating a roadmap.
                                    </p>
                                    <Link
                                        to="/skills"
                                        onClick={onClose}
                                        className="mt-3 inline-flex items-center gap-1.5 rounded-xl bg-[var(--primary-purple)] px-3.5 py-1.5 text-xs font-bold text-white hover:opacity-90 shadow-md"
                                    >
                                        Run Skill Gap Analysis
                                        <ArrowRight size={13} />
                                    </Link>
                                </div>
                            ) : (
                                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                                    {reports.map((rep) => {
                                        const isSelected = selectedReportId === rep.id
                                        return (
                                            <div
                                                key={rep.id}
                                                onClick={() => setSelectedReportId(rep.id)}
                                                className={`flex items-center justify-between gap-3 rounded-xl border p-3 cursor-pointer transition-all ${
                                                    isSelected
                                                        ? 'border-[var(--accent)] bg-[var(--accent-soft)] shadow-sm'
                                                        : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--border-hover)]'
                                                }`}
                                            >
                                                <div className="min-w-0 flex-1">
                                                    <div className="flex items-center gap-2">
                                                        <Briefcase size={14} className="text-[var(--accent)] shrink-0" />
                                                        <span className="truncate text-xs font-bold text-[var(--text-primary)]">
                                                            {rep.role_title}
                                                        </span>
                                                        <span className="rounded-full bg-[var(--surface-hover)] px-2 py-0.2 text-[10px] font-mono text-[var(--text-secondary)]">
                                                            Score: {Math.round(rep.overall_score || 0)}%
                                                        </span>
                                                    </div>
                                                    <div className="mt-1 flex items-center gap-2 text-[10px] text-[var(--text-secondary)]">
                                                        <span>{new Date(rep.created_at).toLocaleDateString()}</span>
                                                        <span>•</span>
                                                        <span>{rep.missing_required_skills_count || 0} core gaps</span>
                                                    </div>
                                                </div>
                                                <div
                                                    className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border ${
                                                        isSelected
                                                            ? 'border-[var(--accent)] bg-[var(--accent)] text-white'
                                                            : 'border-[var(--border)]'
                                                    }`}
                                                >
                                                    {isSelected && <Check size={12} />}
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            )}
                        </div>

                        {/* 2. Study Time Availability */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                                    2. Weekly Study Availability
                                </label>
                                <span className="text-xs font-bold text-[var(--accent)]">
                                    {weeklyHours} hrs / week
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                                {presetHours.map((preset) => {
                                    const active = !isCustomHours && weeklyHours === preset.hours
                                    return (
                                        <button
                                            key={preset.hours}
                                            type="button"
                                            onClick={() => handleSelectPresetHours(preset.hours)}
                                            className={`rounded-xl border p-2.5 text-center transition-all cursor-pointer ${
                                                active
                                                    ? 'border-[var(--accent)] bg-[var(--accent-soft)] shadow-sm'
                                                    : 'border-[var(--border)] bg-[var(--surface)] hover:bg-[var(--surface-hover)]'
                                            }`}
                                        >
                                            <div className="text-xs font-bold text-[var(--text-primary)]">
                                                {preset.label}
                                            </div>
                                            <div className="mt-0.5 text-[10px] text-[var(--text-secondary)]">
                                                {preset.desc}
                                            </div>
                                        </button>
                                    )
                                })}
                            </div>

                            {/* Custom Hours Option */}
                            <div className="mt-2.5 flex items-center gap-2">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setIsCustomHours(true)
                                        handleCustomHoursChange(customHoursInput)
                                    }}
                                    className={`rounded-xl border px-3 py-1.5 text-xs font-semibold cursor-pointer transition-all ${
                                        isCustomHours
                                            ? 'border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent)]'
                                            : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)]'
                                    }`}
                                >
                                    Custom hours
                                </button>
                                {isCustomHours && (
                                    <div className="flex items-center gap-1.5">
                                        <input
                                            type="number"
                                            min="1"
                                            max="60"
                                            value={customHoursInput}
                                            onChange={(e) => handleCustomHoursChange(e.target.value)}
                                            className="w-16 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-2 py-1 text-xs text-center font-bold text-[var(--text-primary)] focus:border-[var(--accent)] focus:outline-none"
                                        />
                                        <span className="text-xs text-[var(--text-secondary)]">hrs / week</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* 3. Optional Custom Title */}
                        <div>
                            <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] mb-1.5">
                                3. Roadmap Title (Optional)
                            </label>
                            <input
                                type="text"
                                value={roadmapTitle}
                                onChange={(e) => setRoadmapTitle(e.target.value)}
                                placeholder="e.g. Backend Engineer Mastery Sprint"
                                className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none"
                            />
                        </div>

                        {/* Actions */}
                        <div className="flex items-center justify-end gap-3 pt-4 border-t border-[var(--border)]">
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={isGenerating}
                                className="rounded-xl border border-[var(--border)] bg-[var(--surface-hover)] px-4 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isGenerating || reports.length === 0}
                                className="inline-flex items-center gap-2 rounded-xl bg-[var(--primary-purple)] px-5 py-2 text-xs font-bold text-white shadow-md shadow-purple-600/20 hover:opacity-90 transition-all cursor-pointer disabled:opacity-50"
                            >
                                {isGenerating ? (
                                    <>
                                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                                        <span>Generating Curriculum...</span>
                                    </>
                                ) : (
                                    <>
                                        <Sparkles size={14} />
                                        <span>Generate Roadmap</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </AnimatePresence>
    )
}
