import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { ShieldCheck } from 'lucide-react'
import OnboardingLayout from '../components/onboarding/OnboardingLayout'
import ProfileForm from '../components/onboarding/ProfileForm'
import { useCareerProfile } from '../context/CareerProfileContext'
import { registerCareerProfile, updateCareerProfile } from '../services/onboardingService'

export default function Onboarding() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const isEdit = searchParams.get('edit') === 'true'

    const { profile, onboardingCompleted, isLoading: isContextLoading, refreshProfile } = useCareerProfile()

    const [isSubmitting, setIsSubmitting] = useState(false)
    const [serverError, setServerError] = useState(null)

    // If user already completed onboarding and didn't ask to edit, redirect to Dashboard
    useEffect(() => {
        if (!isContextLoading && onboardingCompleted && !isEdit) {
            navigate('/dashboard', { replace: true })
        }
    }, [isContextLoading, onboardingCompleted, isEdit, navigate])

    const handleSubmit = async (formData) => {
        setIsSubmitting(true)
        setServerError(null)

        try {
            if (isEdit) {
                await updateCareerProfile(formData)
            } else {
                try {
                    await registerCareerProfile(formData)
                } catch (regErr) {
                    if (regErr.response?.status === 409) {
                        // Profile already exists in local DB; seamlessly update and proceed
                        await updateCareerProfile(formData)
                    } else {
                        throw regErr
                    }
                }
            }

            // Sync global context with newly saved profile from database
            await refreshProfile()

            // Navigate directly to Dashboard
            navigate('/dashboard', { replace: true })
        } catch (err) {
            console.error('[Onboarding] Profile registration/update failed:', err)
            setServerError(err.userMessage || 'An unexpected error occurred while saving your profile. Please try again.')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <OnboardingLayout isEdit={isEdit}>
            <div className="glass-card rounded-2xl p-5 sm:p-7 md:p-8 shadow-xl border border-[var(--border)] space-y-5">
                {/* Form with Centered Active Step Stepper */}
                <ProfileForm
                    key={profile?.id || (isEdit ? 'edit' : 'create')}
                    initialData={profile}
                    onSubmit={handleSubmit}
                    isLoading={isSubmitting}
                    serverError={serverError}
                    isEdit={isEdit}
                />

                {/* Privacy Safeguard Callout */}
                <div className="pt-2 flex items-center justify-center gap-2 text-[11px] text-[var(--text-muted)] border-t border-[var(--border)]">
                    <ShieldCheck size={14} className="text-[var(--success)] shrink-0" />
                    <span>
                        CareerMind AI stores your data purely in local SQLite. Zero cloud tracking.
                    </span>
                </div>
            </div>
        </OnboardingLayout>
    )
}
