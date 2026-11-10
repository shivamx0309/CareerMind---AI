import api from './api'

/**
 * Fetch all available role benchmarks from the backend.
 * @returns {Promise<Array>} List of RoleBenchmarkSummaryResponse objects.
 */
export async function getRoles() {
    const response = await api.get('/skills/roles')
    return response.data
}

/**
 * Fetch all candidate resumes from the user's resume library.
 * @returns {Promise<Array>} List of ResumeRecordResponse objects.
 */
export async function getResumeLibrary() {
    const response = await api.get('/resumes/library')
    return response.data
}

/**
 * Execute standalone skill gap analysis against a selected role benchmark.
 *
 * @param {Object} payload
 * @param {string} payload.target_role - Target role identifier (e.g. 'sde', 'python_developer').
 * @param {string} [payload.resume_id] - Optional resume record UUID or file_id.
 * @returns {Promise<Object>} SkillGapReportResponse.
 */
export async function analyzeSkills({ target_role, resume_id }) {
    const payload = { target_role }
    if (resume_id) {
        payload.resume_id = resume_id
    }
    const response = await api.post('/skills/analyze', payload)
    return response.data
}

/**
 * Fetch historical skill gap reports for the active career profile.
 * @returns {Promise<Array>} List of SkillGapReportSummaryResponse objects.
 */
export async function getReports() {
    const response = await api.get('/skills/reports')
    return response.data
}

/**
 * Retrieve a specific skill gap report by its unique ID.
 * @param {string} reportId - SkillGapReport UUID.
 * @returns {Promise<Object>} Full SkillGapReportResponse.
 */
export async function getReportById(reportId) {
    const response = await api.get(`/skills/reports/${reportId}`)
    return response.data
}

/**
 * Permanently delete a historical skill gap report.
 * @param {string} reportId - SkillGapReport UUID.
 * @returns {Promise<void>}
 */
export async function deleteReport(reportId) {
    const response = await api.delete(`/skills/reports/${reportId}`)
    return response.data
}

