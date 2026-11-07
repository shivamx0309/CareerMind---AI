import api from './api'

/**
 * Upload candidate resume PDF to the backend.
 *
 * @param {File} file - PDF file to upload.
 * @param {Function} onProgress - Callback for upload progress percentage (0 - 100).
 * @returns {Promise<Object>} ResumeUploadResponse from backend.
 */
export async function uploadResume(file, onProgress) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/resumes/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (progressEvent.total && onProgress) {
                const percent = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                )
                onProgress(percent)
            }
        },
    })

    return response.data
}

/**
 * Parse an already-uploaded resume PDF into a structured candidate profile.
 *
 * @param {string} fileId - 32-character hexadecimal UUID of the uploaded file.
 * @returns {Promise<Object>} ResumeParseResponse containing candidate profile.
 */
export async function parseResume(fileId) {
    const response = await api.post(`/resumes/${fileId}/parse`)
    return response.data
}

/**
 * Extract raw text and page breakdown from an uploaded resume PDF.
 *
 * @param {string} fileId - 32-character hexadecimal UUID of the uploaded file.
 * @returns {Promise<Object>} ResumeExtractionResponse.
 */
export async function extractResumeText(fileId) {
    const response = await api.post(`/resumes/${fileId}/extract`)
    return response.data
}

