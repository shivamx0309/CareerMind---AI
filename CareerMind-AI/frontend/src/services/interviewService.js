import api from './api'

/**
 * Fetch interview catalog metadata (supported roles, types, difficulties, counts, and categories).
 * @returns {Promise<Object>} InterviewMetadataResponse
 */
export async function getInterviewMetadata() {
  const response = await api.get('/interviews/metadata')
  return response.data
}

/**
 * Start a new interview session.
 * @param {Object} payload
 * @param {string} payload.target_role
 * @param {string} [payload.interview_type="technical"]
 * @param {string} [payload.difficulty="intermediate"]
 * @param {number} [payload.question_count=5]
 * @param {string} [payload.resume_id]
 * @param {string} [payload.skill_gap_report_id]
 * @returns {Promise<Object>} InterviewSessionResponse
 */
export async function startInterviewSession(payload) {
  const response = await api.post('/interviews/sessions', payload)
  return response.data
}

/**
 * Fetch candidate's mock interview history list.
 * @returns {Promise<Array>} List of InterviewSessionSummaryResponse
 */
export async function getInterviewHistory() {
  const response = await api.get('/interviews/sessions')
  return response.data
}

/**
 * Fetch a specific interview session by ID.
 * @param {string} sessionId
 * @returns {Promise<Object>} InterviewSessionResponse
 */
export async function getInterviewSession(sessionId) {
  const response = await api.get(`/interviews/sessions/${sessionId}`)
  return response.data
}

/**
 * Fetch the currently active unanswered question for a session.
 * @param {string} sessionId
 * @returns {Promise<Object|null>} SessionQuestionResponse or null if completed
 */
export async function getCurrentQuestion(sessionId) {
  const response = await api.get(`/interviews/sessions/${sessionId}/current-question`)
  return response.data
}

/**
 * Submit an answer to the active or specified question in a session.
 * @param {string} sessionId
 * @param {Object} payload
 * @param {string} [payload.question_id]
 * @param {string} payload.answer_text
 * @returns {Promise<Object>} InterviewAnswerResponse with evaluation
 */
export async function submitAnswer(sessionId, payload) {
  const response = await api.post(`/interviews/sessions/${sessionId}/answer`, payload)
  return response.data
}

/**
 * Submit an answer explicitly for a specific question ID.
 * @param {string} sessionId
 * @param {string} questionId
 * @param {string} answerText
 * @returns {Promise<Object>} InterviewAnswerResponse with evaluation
 */
export async function submitAnswerToQuestion(sessionId, questionId, answerText) {
  const response = await api.post(
    `/interviews/sessions/${sessionId}/questions/${questionId}/answer`,
    { question_id: questionId, answer_text: answerText }
  )
  return response.data
}

/**
 * Finalize an interview session and generate the persistent report.
 * @param {string} sessionId
 * @returns {Promise<Object>} InterviewReportResponse
 */
export async function completeInterview(sessionId) {
  const response = await api.post(`/interviews/sessions/${sessionId}/complete`)
  return response.data
}

/**
 * Fetch the performance report for an interview session.
 * @param {string} sessionId
 * @returns {Promise<Object>} InterviewReportResponse
 */
export async function getInterviewReport(sessionId) {
  const response = await api.get(`/interviews/sessions/${sessionId}/report`)
  return response.data
}

/**
 * Delete an interview session and its cascade children.
 * @param {string} sessionId
 * @returns {Promise<void>}
 */
export async function deleteInterviewSession(sessionId) {
  await api.delete(`/interviews/sessions/${sessionId}`)
}

