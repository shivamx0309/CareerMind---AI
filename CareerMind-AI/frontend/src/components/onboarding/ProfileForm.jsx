import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, ArrowRight, ArrowLeft, Save, AlertCircle, Loader2, Check } from 'lucide-react'
import { Link } from 'react-router-dom'
import PersonalInfoFields from './PersonalInfoFields'
import EducationFields from './EducationFields'
import CareerPreferenceFields from './CareerPreferenceFields'

const STEP_METADATA = {
    1: {
        title: 'Personal Information',
        description: 'Enter your full name and current career status',
        nextLabel: 'Continue to Education',
    },
    2: {
        title: 'Educational Background',
        description: 'Provide your highest qualification and degree credentials',
        nextLabel: 'Continue to Preferences',
    },
    3: {
        title: 'Career Preferences',
        description: 'Set your primary target role, working mode, and locations',
        nextLabel: 'Complete Registration & Enter Dashboard',
    },
}

export default function ProfileForm({
    initialData = null,
    onSubmit,
    isLoading = false,
    serverError = null,
    isEdit = false,
    onStepChange,
}) {
    const [currentStep, setCurrentStep] = useState(1) // 1: Personal, 2: Education, 3: Preferences

    const [formData, setFormData] = useState(() => ({
        full_name: initialData?.full_name || '',
        career_status: initialData?.career_status || 'Fresher',
        highest_education: initialData?.highest_education || "Bachelor's Degree",
        degree: initialData?.degree || '',
        institution: initialData?.institution || '',
        graduation_year: initialData?.graduation_year || new Date().getFullYear(),
        primary_target_role: initialData?.primary_target_role || '',
        preferred_job_type: initialData?.preferred_job_type || 'Full-time',
        preferred_work_mode: initialData?.preferred_work_mode || 'Remote',
        preferred_locations: Array.isArray(initialData?.preferred_locations) && initialData.preferred_locations.length > 0
            ? initialData.preferred_locations
            : ['Remote'],
        career_objective: initialData?.career_objective || '',
    }))

    const [errors, setErrors] = useState({})

    const handleStepChange = (nextStep) => {
        setCurrentStep(nextStep)
        if (onStepChange) {
            onStepChange(nextStep)
        }
    }

    const handleFieldChange = (field, value) => {
        setFormData((prev) => ({ ...prev, [field]: value }))
        if (errors[field]) {
            setErrors((prev) => {
                const next = { ...prev }
                delete next[field]
                return next
            })
        }
    }

    // Step 1 Validation
    const validateStep1 = () => {
        const nextErrors = {}
        if (!formData.full_name || !formData.full_name.trim()) {
            nextErrors.full_name = 'Full name is required.'
        } else if (formData.full_name.trim().length < 2) {
            nextErrors.full_name = 'Name must be at least 2 characters.'
        }

        if (!formData.career_status) {
            nextErrors.career_status = 'Please select your career status.'
        }

        setErrors((prev) => ({ ...prev, ...nextErrors }))
        return Object.keys(nextErrors).length === 0
    }

    // Step 2 Validation
    const validateStep2 = () => {
        const nextErrors = {}
        if (!formData.highest_education || !formData.highest_education.trim()) {
            nextErrors.highest_education = 'Please select your highest education level.'
        }

        if (!formData.degree || !formData.degree.trim()) {
            nextErrors.degree = 'Degree or qualification specialization is required.'
        }

        if (!formData.institution || !formData.institution.trim()) {
            nextErrors.institution = 'Institution or university name is required.'
        }

        const year = Number(formData.graduation_year)
        if (!year || isNaN(year) || year < 1970 || year > 2040) {
            nextErrors.graduation_year = 'Please enter a valid graduation year (1970–2040).'
        }

        setErrors((prev) => ({ ...prev, ...nextErrors }))
        return Object.keys(nextErrors).length === 0
    }

    // Step 3 Validation
    const validateStep3 = () => {
        const nextErrors = {}
        if (!formData.primary_target_role || !formData.primary_target_role.trim()) {
            nextErrors.primary_target_role = 'Primary target role is required.'
        }

        setErrors((prev) => ({ ...prev, ...nextErrors }))
        return Object.keys(nextErrors).length === 0
    }

    const handleNext = () => {
        if (currentStep === 1) {
            if (validateStep1()) {
                handleStepChange(2)
            }
        } else if (currentStep === 2) {
            if (validateStep2()) {
                handleStepChange(3)
            }
        }
    }

    const handlePrev = () => {
        if (currentStep > 1) {
            handleStepChange(currentStep - 1)
        }
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        if (isLoading) return

        const s1Ok = validateStep1()
        const s2Ok = validateStep2()
        const s3Ok = validateStep3()

        if (!s1Ok) {
            handleStepChange(1)
            return
        }
        if (!s2Ok) {
            handleStepChange(2)
            return
        }
        if (!s3Ok) {
            handleStepChange(3)
            return
        }

        onSubmit(formData)
    }

    const currentMeta = STEP_METADATA[currentStep]

    return (
        <form onSubmit={handleSubmit} noValidate className="space-y-6">
            {/* Server Error Alert */}
            {serverError && (
                <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3.5 text-xs text-rose-300">
                    <AlertCircle size={16} className="mt-0.5 shrink-0 text-rose-400" />
                    <div>
                        <strong className="block font-semibold">Registration Error:</strong>
                        <span>{serverError}</span>
                    </div>
                </div>
            )}

            {/* Centered Step Indicator — Only active step name shown centered */}
            <div className="flex flex-col items-center justify-center gap-2.5 pb-4 border-b border-[var(--border)]">
                {/* 1 - 2 - 3 Progress Bubbles */}
                <div className="flex items-center gap-2.5">
                    {[1, 2, 3].map((step) => {
                        const isCompleted = step < currentStep
                        const isCurrent = step === currentStep
                        return (
                            <div key={step} className="flex items-center gap-2.5">
                                <button
                                    type="button"
                                    onClick={() => {
                                        if (isEdit || step < currentStep) handleStepChange(step)
                                        else if (step === 2 && currentStep === 1 && validateStep1()) handleStepChange(2)
                                        else if (step === 3 && currentStep === 2 && validateStep2()) handleStepChange(3)
                                    }}
                                    className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-all ${
                                        isCompleted
                                            ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 cursor-pointer'
                                            : isCurrent
                                            ? 'bg-[var(--accent)] text-white shadow-md shadow-indigo-500/30 ring-4 ring-[var(--accent-soft)]'
                                            : 'bg-[var(--surface-solid)] border border-[var(--border)] text-[var(--text-muted)] cursor-not-allowed'
                                    }`}
                                    title={`Step ${step}`}
                                >
                                    {isCompleted ? <Check size={13} strokeWidth={3} /> : step}
                                </button>
                                {step < 3 && (
                                    <div
                                        className={`w-8 sm:w-12 h-0.5 transition-all duration-300 ${
                                            step < currentStep ? 'bg-emerald-500/60' : 'bg-[var(--border)]'
                                        }`}
                                    />
                                )}
                            </div>
                        )
                    })}
                </div>

                {/* Only the active step's name and description centered */}
                <div className="text-center space-y-0.5 pt-1">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--accent)] block">
                        Step {currentStep} of 3
                    </span>
                    <h2 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                        {currentMeta.title}
                    </h2>
                    <p className="text-xs text-[var(--text-secondary)]">
                        {currentMeta.description}
                    </p>
                </div>
            </div>

            {/* Step Body with Smooth Transition */}
            <div className="min-h-[260px]">
                <AnimatePresence mode="wait">
                    {currentStep === 1 && (
                        <motion.div
                            key="step1"
                            initial={{ opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -6 }}
                            transition={{ duration: 0.18 }}
                        >
                            <PersonalInfoFields
                                formData={formData}
                                onChange={handleFieldChange}
                                errors={errors}
                                hideHeader={true}
                            />
                        </motion.div>
                    )}

                    {currentStep === 2 && (
                        <motion.div
                            key="step2"
                            initial={{ opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -6 }}
                            transition={{ duration: 0.18 }}
                        >
                            <EducationFields
                                formData={formData}
                                onChange={handleFieldChange}
                                errors={errors}
                                hideHeader={true}
                            />
                        </motion.div>
                    )}

                    {currentStep === 3 && (
                        <motion.div
                            key="step3"
                            initial={{ opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -6 }}
                            transition={{ duration: 0.18 }}
                        >
                            <CareerPreferenceFields
                                formData={formData}
                                onChange={handleFieldChange}
                                errors={errors}
                                hideHeader={true}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Stepper Footer Actions */}
            <div className="border-t border-[var(--border)] pt-4 flex flex-col sm:flex-row items-center justify-between gap-3">
                {/* Left Action: Cancel (if Edit) or Previous Step */}
                <div className="w-full sm:w-auto flex items-center gap-2">
                    {isEdit && (
                        <Link
                            to="/dashboard"
                            className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-4 py-2.5 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)] transition-all"
                        >
                            Cancel
                        </Link>
                    )}

                    {currentStep > 1 && (
                        <button
                            type="button"
                            onClick={handlePrev}
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-4 py-2.5 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                        >
                            <ArrowLeft size={14} />
                            <span>Previous Step</span>
                        </button>
                    )}
                </div>

                {/* Right Action: Next Step or Submit */}
                <div className="w-full sm:w-auto flex items-center gap-2 justify-end">
                    {currentStep < 3 ? (
                        <button
                            type="button"
                            onClick={handleNext}
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-6 py-2.5 text-xs font-bold text-white shadow-md shadow-indigo-500/25 transition-all hover:opacity-95 hover:shadow-lg cursor-pointer"
                        >
                            <span>{currentMeta.nextLabel}</span>
                            <ArrowRight size={14} />
                        </button>
                    ) : (
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-6 py-3 text-xs font-bold text-white shadow-md shadow-indigo-500/25 transition-all hover:opacity-95 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 size={16} className="animate-spin" />
                                    <span>{isEdit ? 'Saving Changes...' : 'Creating Profile...'}</span>
                                </>
                            ) : isEdit ? (
                                <>
                                    <Save size={16} />
                                    <span>Save Profile Changes</span>
                                </>
                            ) : (
                                <>
                                    <Sparkles size={16} />
                                    <span>Complete Registration &amp; Enter Dashboard</span>
                                    <ArrowRight size={15} />
                                </>
                            )}
                        </button>
                    )}
                </div>
            </div>
        </form>
    )
}
