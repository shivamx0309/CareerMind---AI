import api from './api'

/**
 * Fetch candidate's learning preferences.
 * @returns {Promise<Object>} LearningPreferenceResponse
 */
export async function getLearningPreferences() {
    const response = await api.get('/learning/preferences')
    return response.data
}

/**
 * Update candidate's learning preferences.
 * @param {Object} prefs - LearningPreferenceCreate payload
 * @returns {Promise<Object>} Updated LearningPreferenceResponse
 */
export async function updateLearningPreferences(prefs) {
    const response = await api.put('/learning/preferences', prefs)
    return response.data
}

/**
 * Generate a personalized learning roadmap from a SkillGapReport.
 * @param {Object} payload
 * @param {string} payload.skill_gap_report_id - UUID of the saved SkillGapReport
 * @param {number} [payload.weekly_study_hours] - Optional study hours per week (default: 10)
 * @param {string} [payload.title] - Optional custom roadmap title
 * @returns {Promise<Object>} Full LearningRoadmapResponse
 */
export async function generateRoadmap({ skill_gap_report_id, weekly_study_hours, title }) {
    const payload = { skill_gap_report_id }
    if (weekly_study_hours) {
        payload.weekly_study_hours = Number(weekly_study_hours)
    }
    if (title?.trim()) {
        payload.title = title.trim()
    }
    const response = await api.post('/learning/roadmaps/generate', payload)
    return response.data
}

/**
 * List all historical learning roadmaps for the active career profile.
 * @returns {Promise<Array>} List of LearningRoadmapSummaryResponse objects
 */
export async function getRoadmaps() {
    const response = await api.get('/learning/roadmaps')
    return response.data
}

/**
 * Retrieve comprehensive details of a specific learning roadmap by ID.
 * @param {string} roadmapId - LearningRoadmap UUID
 * @returns {Promise<Object>} Full LearningRoadmapResponse
 */
export async function getRoadmapById(roadmapId) {
    const response = await api.get(`/learning/roadmaps/${roadmapId}`)
    return response.data
}

/**
 * Update topic completion status.
 * @param {string} roadmapId - LearningRoadmap UUID
 * @param {string} topicId - RoadmapTopic UUID
 * @param {'not_started' | 'in_progress' | 'completed'} status - New completion status
 * @returns {Promise<Object>} Updated RoadmapTopicResponse
 */
export async function updateTopicStatus(roadmapId, topicId, status) {
    const response = await api.patch(`/learning/roadmaps/${roadmapId}/topics/${topicId}`, { status })
    return response.data
}

/**
 * Update skill module completion status (cascades to all child topics).
 * @param {string} roadmapId - LearningRoadmap UUID
 * @param {string} skillId - RoadmapSkill UUID
 * @param {'not_started' | 'in_progress' | 'completed'} status - New completion status
 * @returns {Promise<Object>} Updated RoadmapSkillResponse
 */
export async function updateSkillStatus(roadmapId, skillId, status) {
    const response = await api.patch(`/learning/roadmaps/${roadmapId}/skills/${skillId}`, { status })
    return response.data
}

/**
 * Update weekly milestone progress status.
 * @param {string} roadmapId - LearningRoadmap UUID
 * @param {string} milestoneId - RoadmapMilestone UUID
 * @param {'pending' | 'in_progress' | 'completed'} status - New milestone status
 * @returns {Promise<Object>} Updated RoadmapMilestoneResponse
 */
export async function updateMilestoneStatus(roadmapId, milestoneId, status) {
    const response = await api.patch(`/learning/roadmaps/${roadmapId}/milestones/${milestoneId}`, { status })
    return response.data
}

/**
 * Retrieve real-time progress metrics and next recommended study topic.
 * @param {string} roadmapId - LearningRoadmap UUID
 * @returns {Promise<Object>} RoadmapProgressResponse
 */
export async function getRoadmapProgress(roadmapId) {
    const response = await api.get(`/learning/roadmaps/${roadmapId}/progress`)
    return response.data
}

/**
 * Permanently delete a learning roadmap and cascade all associated items.
 * @param {string} roadmapId - LearningRoadmap UUID
 * @returns {Promise<void>}
 */
export async function deleteRoadmap(roadmapId) {
    await api.delete(`/learning/roadmaps/${roadmapId}`)
}

