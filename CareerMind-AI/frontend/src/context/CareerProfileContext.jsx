/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react'
import { getOnboardingStatus, getCareerProfile } from '../services/onboardingService'

const CareerProfileContext = createContext(null)

export function CareerProfileProvider({ children }) {
    const [profile, setProfile] = useState(null)
    const [statusData, setStatusData] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)

    const refreshProfile = useCallback(async () => {
        try {
            setError(null)
            const status = await getOnboardingStatus()
            setStatusData(status)

            if (status.has_profile) {
                try {
                    const fullProfile = await getCareerProfile()
                    setProfile(fullProfile)
                } catch (profErr) {
                    console.warn('[CareerProfileContext] Failed to load full profile:', profErr)
                    setProfile(null)
                }
            } else {
                setProfile(null)
            }
        } catch (err) {
            console.error('[CareerProfileContext] Failed to fetch onboarding status:', err)
            setError(err.userMessage || 'Could not verify onboarding status with backend server.')
        } finally {
            setIsLoading(false)
        }
    }, [])

    useEffect(() => {
        let isMounted = true

        async function init() {
            try {
                const status = await getOnboardingStatus()
                if (!isMounted) return
                setStatusData(status)

                if (status.has_profile) {
                    try {
                        const fullProfile = await getCareerProfile()
                        if (isMounted) setProfile(fullProfile)
                    } catch (profErr) {
                        console.warn('[CareerProfileContext] Initial profile fetch failed:', profErr)
                    }
                }
            } catch (err) {
                console.error('[CareerProfileContext] Initial status fetch failed:', err)
                if (isMounted) {
                    setError(err.userMessage || 'Could not verify onboarding status with backend server.')
                }
            } finally {
                if (isMounted) {
                    setIsLoading(false)
                }
            }
        }

        init()

        return () => {
            isMounted = false
        }
    }, [])

    const onboardingCompleted = Boolean(statusData?.onboarding_completed)

    const value = useMemo(
        () => ({
            profile,
            statusData,
            onboardingCompleted,
            isLoading,
            error,
            refreshProfile,
        }),
        [profile, statusData, onboardingCompleted, isLoading, error, refreshProfile]
    )

    return (
        <CareerProfileContext.Provider value={value}>
            {children}
        </CareerProfileContext.Provider>
    )
}

export function useCareerProfile() {
    const context = useContext(CareerProfileContext)
    if (!context) {
        throw new Error('useCareerProfile must be used within a CareerProfileProvider')
    }
    return context
}
