import api from './api'

/**
 * Service for local user onboarding and career profile management.
 */

/**
 * Check whether the local user has completed onboarding.
 *
 * @returns {Promise<{
 *   onboarding_completed: boolean,
 *   has_profile: boolean,
 *   full_name: string | null,
 *   primary_target_role: string | null,
 *   career_status: string | null
 * }>}
 */
export async function getOnboardingStatus() {
    const response = await api.get('/onboarding/status')
    return response.data
}

/**
 * Retrieve the full registered career profile for the local user.
 *
 * @returns {Promise<object>}
 */
export async function getCareerProfile() {
    const response = await api.get('/onboarding/profile')
    return response.data
}

/**
 * Register a new career profile during onboarding.
 *
 * @param {object} profileData - Validated profile fields.
 * @returns {Promise<object>} Created profile response.
 */
export async function registerCareerProfile(profileData) {
    const response = await api.post('/onboarding/profile', profileData)
    return response.data
}

/**
 * Update an existing registered career profile.
 *
 * @param {object} profileData - Partial or full updated profile fields.
 * @returns {Promise<object>} Updated profile response.
 */
export async function updateCareerProfile(profileData) {
    const response = await api.put('/onboarding/profile', profileData)
    return response.data
}

