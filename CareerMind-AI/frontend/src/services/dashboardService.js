import api from './api'

/**
 * Fetch centralized, real candidate career insights for the dashboard.
 *
 * Returns authoritative metrics from SQLite database:
 * - career_profile: Essential profile attributes, target role, education, tech skills count.
 * - resume: Actual parsed resume metrics (status, display_name, total_skills, exp_count, etc.).
 * - job_matching: Persisted match analyses (if available; no fabricated numbers).
 * - skill_gap: Latest benchmark score, role title, required coverage, matched/missing counts.
 * - learning_roadmap: Active roadmap progress %, completed/total topics, remaining study hours.
 * - mock_interview: Total completed sessions, average score, best score, latest date.
 *
 * @returns {Promise<Object>} DashboardInsightsResponse
 */
export async function getDashboardInsights() {
    const response = await api.get('/dashboard/insights')
    return response.data
}

