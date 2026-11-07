import api from './api.js'

/**
 * Match an uploaded candidate resume against a target job description.
 *
 * Calls POST /api/v1/jobs/match with structured job criteria and candidate file_id.
 *
 * @param {Object} payload
 * @param {string} payload.file_id - 32-character hexadecimal UUID of the resume PDF.
 * @param {string} payload.job_description - Full text of the job posting (min 50 chars, max 30000 chars).
 * @param {string} [payload.job_title] - Optional job title.
 * @param {string} [payload.company] - Optional company name.
 * @param {string} [payload.location] - Optional job location or work mode.
 * @returns {Promise<Object>} Complete JobMatchResponse from backend.
 * @throws {Error} Enhanced error with userMessage and status code.
 */
export async function matchJob(payload) {
    if (!payload || typeof payload !== 'object') {
        const err = new Error('Match payload must be a valid object.')
        err.userMessage = 'Invalid job matching request.'
        throw err
    }

    const { file_id, job_description, job_title, company, location } = payload

    if (!file_id || typeof file_id !== 'string') {
        const err = new Error('A valid resume file_id is required.')
        err.userMessage = 'No active resume found. Please upload a resume before matching.'
        err.status = 400
        throw err
    }

    if (!job_description || typeof job_description !== 'string' || job_description.trim().length < 50) {
        const err = new Error('Job description must be at least 50 characters.')
        err.userMessage = 'Please enter a detailed job description of at least 50 characters.'
        err.status = 422
        throw err
    }

    const requestBody = {
        file_id: file_id.trim().toLowerCase(),
        job_description: job_description.trim(),
        job_title: job_title?.trim() || null,
        company: company?.trim() || null,
        location: location?.trim() || null,
    }

    try {
        const response = await api.post('/jobs/match', requestBody)
        return response.data
    } catch (error) {
        // Handle HTTP response codes specifically
        const status = error.response?.status
        const detail = error.response?.data?.detail

        if (status === 400) {
            error.userMessage =
                typeof detail === 'string'
                    ? detail
                    : 'Invalid resume identifier or request parameters.'
        } else if (status === 404) {
            error.userMessage =
                'The specified resume PDF could not be found on the server. Please re-upload your resume.'
        } else if (status === 422) {
            error.userMessage =
                typeof detail === 'string'
                    ? detail
                    : Array.isArray(detail)
                    ? detail.map((d) => d.msg || d.detail).join('; ')
                    : 'The job description is invalid, empty, or unprocessable.'
        } else if (status === 500) {
            error.userMessage =
                'A server error occurred while processing the match. Please try again or check the backend service.'
        } else if (!error.response) {
            error.userMessage =
                'Unable to connect to CareerMind AI backend. Please verify the backend server is running on http://127.0.0.1:8000.'
        } else {
            error.userMessage =
                typeof detail === 'string'
                    ? detail
                    : 'An unexpected error occurred during job description matching.'
        }

        throw error
    }
}
