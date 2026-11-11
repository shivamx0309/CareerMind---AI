import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    FileSearch,
    BriefcaseBusiness,
    Target,
    BookOpen,
    ArrowUpRight,
    Sparkles,
    Clock3,
    CheckCircle2,
    Check,
    Upload,
    MessageSquare,
    UserCheck,
    GraduationCap,
    MapPin,
    Briefcase,
    Edit3,
    TrendingUp,
    Code2,
    FolderGit2,
    Award,
} from 'lucide-react'
import { useCareerProfile } from '../context/CareerProfileContext'
import { useCandidate } from '../context/CandidateContext'
import { getReports } from '../services/skillGapService'
import { getRoadmaps } from '../services/learningService'
import { getDashboardInsights } from '../services/dashboardService'
import careerHeroIllustration from '../assets/career-hero-illustration.png'

const baseActions = [
    {
        title: 'Analyze Resume',
        description: 'Extract skills and experience from your resume.',
        icon: FileSearch,
        path: '/resume',
    },
    {
        title: 'Explore Job Match',
        description: 'Compare your profile with job requirements.',
        icon: BriefcaseBusiness,
        path: '/jobs',
    },
    {
        title: 'Edit Career Profile',
        description: 'Update your career status, education, and target preferences.',
        icon: UserCheck,
        path: '/onboarding?edit=true',
    },
    {
        title: 'Practice Interview',
        description: 'Prepare for technical and HR interviews.',
        icon: MessageSquare,
        path: '/interview',
    },
]

const activities = [
    {
        title: 'Upload your first resume',
        description: 'Start building your career profile',
        icon: Upload,
    },
    {
        title: 'Discover your skill gaps',
        description: 'Find the skills you need to improve',
        icon: Target,
    },
    {
        title: 'Create a learning roadmap',
        description: 'Build a personalized learning plan',
        icon: BookOpen,
    },
]

export default function Dashboard() {
    const { profile } = useCareerProfile()
    const { hasResume } = useCandidate()
    const [insights, setInsights] = useState(null)
    const [reportsCount, setReportsCount] = useState(0)
    const [roadmapsCount, setRoadmapsCount] = useState(0)

    useEffect(() => {
        let isMounted = true

        async function loadData() {
            try {
                const [insightsRes, repRes, roadRes] = await Promise.allSettled([
                    getDashboardInsights(),
                    getReports(),
                    getRoadmaps(),
                ])

                if (!isMounted) return

                if (insightsRes.status === 'fulfilled' && insightsRes.value) {
                    setInsights(insightsRes.value)
                }
                if (repRes.status === 'fulfilled' && Array.isArray(repRes.value)) {
                    setReportsCount(repRes.value.length)
                }
                if (roadRes.status === 'fulfilled' && Array.isArray(roadRes.value)) {
                    setRoadmapsCount(roadRes.value.length)
                }
            } catch (err) {
                console.error('Failed to load dashboard insights:', err)
            }
        }

        loadData()

        const handleFocus = () => {
            loadData()
        }
        window.addEventListener('focus', handleFocus)

        return () => {
            isMounted = false
            window.removeEventListener('focus', handleFocus)
        }
    }, [])

    // Career Overview Statistics derived strictly from real DB insights
    const stats = useMemo(() => {
        if (!insights) {
            return [
                {
                    title: 'Resume Status',
                    value: 'Loading...',
                    description: 'Checking resume library',
                    icon: FileSearch,
                    color: 'purple',
                },
                {
                    title: 'Skills Identified',
                    value: '0',
                    description: 'Extracted competencies',
                    icon: Target,
                    color: 'green',
                },
                {
                    title: 'Job Matches',
                    value: '0',
                    description: 'No job matches yet',
                    icon: BriefcaseBusiness,
                    color: 'blue',
                },
                {
                    title: 'Skill Gap Score',
                    value: 'Not analyzed',
                    description: 'Benchmark assessment',
                    icon: TrendingUp,
                    color: 'indigo',
                },
                {
                    title: 'Learning Progress',
                    value: '0%',
                    description: 'Your roadmap progress',
                    icon: BookOpen,
                    color: 'orange',
                },
                {
                    title: 'Mock Interviews',
                    value: '0 Done',
                    description: 'Practice interviews',
                    icon: MessageSquare,
                    color: 'emerald',
                },
            ]
        }

        const { resume, job_matching, skill_gap, learning_roadmap, mock_interview } = insights

        return [
            {
                title: 'Resume Status',
                value: resume.has_resume ? (resume.status === 'Parsed' ? 'Analyzed' : resume.status) : 'Not started',
                description: resume.has_resume ? (resume.display_name || 'Resume on file') : 'Upload your resume to begin',
                icon: FileSearch,
                color: 'purple',
            },
            {
                title: 'Skills Identified',
                value: resume.has_resume ? String(resume.total_skills ?? 0) : '0',
                description: resume.has_resume && resume.total_skills > 0
                    ? (resume.top_skills?.slice(0, 3).join(', ') || 'Extracted competencies')
                    : 'Upload resume to extract',
                icon: Target,
                color: 'green',
            },
            {
                title: 'Job Matches',
                value: job_matching.has_persisted_matches ? String(job_matching.total_matches_count) : '0',
                description: job_matching.status_message || 'No job matches yet',
                icon: BriefcaseBusiness,
                color: 'blue',
            },
            {
                title: 'Skill Gap Score',
                value: skill_gap.has_report && skill_gap.latest_score !== null
                    ? `${Math.round(skill_gap.latest_score)}%`
                    : 'Not analyzed yet',
                description: skill_gap.has_report && skill_gap.latest_role_title
                    ? `${skill_gap.latest_role_title} (${Math.round(skill_gap.required_coverage_pct || 0)}% coverage)`
                    : 'Run skill gap analysis',
                icon: TrendingUp,
                color: 'indigo',
            },
            {
                title: 'Learning Progress',
                value: learning_roadmap.has_roadmap
                    ? `${Math.round(learning_roadmap.progress_percentage)}%`
                    : 'No roadmap',
                description: learning_roadmap.has_roadmap
                    ? `${learning_roadmap.completed_topics_count}/${learning_roadmap.total_topics_count} topics • ${Math.round(learning_roadmap.remaining_hours)}h left`
                    : 'Create learning roadmap',
                icon: BookOpen,
                color: 'orange',
            },
            {
                title: 'Mock Interviews',
                value: mock_interview.has_interviews
                    ? `${mock_interview.total_completed_interviews} Done`
                    : '0 Done',
                description: mock_interview.has_interviews && mock_interview.average_score !== null
                    ? `Avg score: ${Math.round(mock_interview.average_score)}%`
                    : 'Practice interview questions',
                icon: MessageSquare,
                color: 'emerald',
            },
        ]
    }, [insights])

    // Derive actual data-driven step completion
    const step1Completed = Boolean(
        hasResume || (insights?.resume?.has_resume && insights?.resume?.status === 'Parsed')
    )
    const step2Completed = Boolean(
        reportsCount > 0 || (insights?.skill_gap?.has_report && insights?.skill_gap?.total_reports_count > 0)
    )
    const step3Completed = Boolean(
        roadmapsCount > 0 || insights?.learning_roadmap?.has_roadmap
    )

    let activeStep = 1
    if (step1Completed && !step2Completed) {
        activeStep = 2
    } else if (step1Completed && step2Completed && !step3Completed) {
        activeStep = 3
    } else if (step1Completed && step2Completed && step3Completed) {
        activeStep = 4
    }

    const candidateName = profile?.full_name || 'Candidate'
    const targetRole = profile?.primary_target_role || 'Target Role'
    const careerStatus = profile?.career_status || 'Career Explorer'

    return (
        <div className="dashboard-page">

            {/* Personalized Welcome Banner */}
            <motion.section
                className="welcome-banner glass-card"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <div className="welcome-content">
                    <div className="welcome-tag">
                        <Sparkles size={14} />
                        <span>{careerStatus.toUpperCase()} &bull; CAREER PROFILE ACTIVE</span>
                    </div>

                    <h1>
                        Welcome back,
                        <br />
                        <span className="gradient-text">{candidateName}.</span>
                    </h1>

                    <p>
                        Targeting <strong className="text-[var(--text-primary)]">{targetRole}</strong> &bull; {profile?.preferred_work_mode || 'Remote'} &bull; {profile?.degree || 'Technical Degree'}
                    </p>

                    <div className="flex flex-wrap items-center gap-3 pt-2">
                        <Link to="/resume" className="primary-button">
                            <FileSearch size={18} />
                            Analyze my resume
                            <ArrowUpRight size={17} />
                        </Link>
                        <Link
                            to="/onboarding?edit=true"
                            className="inline-flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-4 py-2.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
                        >
                            <Edit3 size={15} className="text-[var(--accent)]" />
                            <span>Edit Profile</span>
                        </Link>
                    </div>
                </div>

                <div className="welcome-decoration" aria-hidden="true">
                    <div className="welcome-illustration-glow" />
                    <div className="welcome-orbit-ring" />
                    <motion.img
                        src={careerHeroIllustration}
                        alt="Career Intelligence Platform"
                        className="welcome-illustration-img"
                        animate={{ y: [0, -6, 0] }}
                        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                    />
                </div>
            </motion.section>

            {/* Registered Career Profile Overview Card */}
            {profile && (
                <section className="dashboard-section">
                    <div className="glass-card rounded-2xl p-6 border border-[var(--border)] space-y-4">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border)] pb-3 gap-2">
                            <div className="flex items-center gap-2">
                                <UserCheck size={18} className="text-[var(--accent)]" />
                                <h3 className="text-sm font-bold text-[var(--text-primary)] uppercase tracking-wider">
                                    Registered Career Profile
                                </h3>
                                <span className="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400">
                                    Active &bull; Onboarded
                                </span>
                            </div>

                            <Link
                                to="/onboarding?edit=true"
                                className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--accent)] hover:underline self-start sm:self-center"
                            >
                                <Edit3 size={13} />
                                <span>Edit Profile Preferences</span>
                            </Link>
                        </div>

                        {/* Core Profile Attributes */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                            {/* Target Role & Status */}
                            <div className="space-y-1 rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3.5">
                                <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                    <Target size={11} className="text-[var(--accent)]" />
                                    <span>Target Role</span>
                                </span>
                                <div className="font-bold text-[var(--text-primary)] text-sm">
                                    {profile.primary_target_role}
                                </div>
                                <span className="text-[11px] text-[var(--text-secondary)] block">
                                    Status: {profile.career_status}
                                </span>
                            </div>

                            {/* Education */}
                            <div className="space-y-1 rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3.5">
                                <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                    <GraduationCap size={11} className="text-emerald-400" />
                                    <span>Highest Education</span>
                                </span>
                                <div className="font-bold text-[var(--text-primary)] truncate" title={profile.degree}>
                                    {profile.degree}
                                </div>
                                <span className="text-[11px] text-[var(--text-secondary)] truncate block" title={profile.institution}>
                                    {profile.institution} &bull; {profile.graduation_year}
                                </span>
                            </div>

                            {/* Job Style */}
                            <div className="space-y-1 rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3.5">
                                <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                    <Briefcase size={11} className="text-blue-400" />
                                    <span>Job Preference</span>
                                </span>
                                <div className="font-bold text-[var(--text-primary)]">
                                    {profile.preferred_job_type}
                                </div>
                                <span className="text-[11px] text-[var(--text-secondary)] block">
                                    Mode: {profile.preferred_work_mode}
                                </span>
                            </div>

                            {/* Locations */}
                            <div className="space-y-1 rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3.5">
                                <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                    <MapPin size={11} className="text-amber-400" />
                                    <span>Preferred Locations</span>
                                </span>
                                <div className="font-bold text-[var(--text-primary)] truncate" title={profile.preferred_locations?.join(', ')}>
                                    {profile.preferred_locations?.join(', ') || 'Anywhere'}
                                </div>
                                <span className="text-[11px] text-[var(--text-secondary)] block">
                                    {profile.preferred_locations?.length || 0} location(s)
                                </span>
                            </div>
                        </div>

                        {/* Verified Parsed Resume Competencies Summary */}
                        {insights?.resume?.has_resume && (
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-[var(--border)] text-xs">
                                <div className="rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                        <Code2 size={11} className="text-emerald-400" />
                                        <span>Technical Skills</span>
                                    </span>
                                    <div className="font-bold text-[var(--text-primary)] text-sm mt-0.5">
                                        {insights.resume.total_skills} Skills
                                    </div>
                                    <span className="text-[11px] text-[var(--text-secondary)] truncate block" title={insights.resume.top_skills?.join(', ')}>
                                        {insights.resume.top_skills?.slice(0, 3).join(', ') || 'Extracted'}
                                    </span>
                                </div>

                                <div className="rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                        <FolderGit2 size={11} className="text-blue-400" />
                                        <span>Verified Projects</span>
                                    </span>
                                    <div className="font-bold text-[var(--text-primary)] text-sm mt-0.5">
                                        {insights.resume.project_count} {insights.resume.project_count === 1 ? 'Project' : 'Projects'}
                                    </div>
                                    <span className="text-[11px] text-[var(--text-secondary)] block">
                                        {insights.resume.project_count > 0 ? 'From parsed resume' : 'None recorded'}
                                    </span>
                                </div>

                                <div className="rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                        <Award size={11} className="text-amber-400" />
                                        <span>Certifications</span>
                                    </span>
                                    <div className="font-bold text-[var(--text-primary)] text-sm mt-0.5">
                                        {insights.resume.certification_count} {insights.resume.certification_count === 1 ? 'Cert' : 'Certs'}
                                    </div>
                                    <span className="text-[11px] text-[var(--text-secondary)] block">
                                        {insights.resume.certification_count > 0 ? 'Verified credentials' : 'Not provided'}
                                    </span>
                                </div>

                                <div className="rounded-xl bg-[var(--surface-solid)]/70 border border-[var(--border)] p-3">
                                    <span className="text-[10px] font-semibold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1">
                                        <Clock3 size={11} className="text-purple-400" />
                                        <span>Experience Summary</span>
                                    </span>
                                    <div className="font-bold text-[var(--text-primary)] text-sm mt-0.5">
                                        {insights.career_profile.total_experience_summary}
                                    </div>
                                    <span className="text-[11px] text-[var(--text-secondary)] block">
                                        {insights.resume.experience_count > 0 ? `${insights.resume.experience_count} role(s) on file` : 'Entry level'}
                                    </span>
                                </div>
                            </div>
                        )}

                        {profile.career_objective && (
                            <div className="rounded-xl bg-[var(--surface-hover)]/40 p-3 text-xs text-[var(--text-secondary)] leading-relaxed">
                                <strong className="font-semibold text-[var(--text-primary)] mr-1">Objective:</strong>
                                <span>{profile.career_objective}</span>
                            </div>
                        )}
                    </div>
                </section>
            )}

            {/* Career Overview Section */}
            <section className="dashboard-section">
                <div className="section-heading">
                    <div>
                        <h2>Career Overview</h2>
                        <p>Your career intelligence at a glance</p>
                    </div>

                    {insights?.resume?.status === 'Parsed' ? (
                        <span className="demo-label bg-emerald-500/15 border-emerald-500/30 text-emerald-600 dark:text-emerald-400 font-semibold">
                            <CheckCircle2 size={13} />
                            Resume Analyzed ({insights.resume.total_skills} Skills)
                        </span>
                    ) : insights?.resume?.has_resume ? (
                        <span className="demo-label bg-amber-500/15 border-amber-500/30 text-amber-600 dark:text-amber-400 font-semibold">
                            <Clock3 size={13} />
                            Resume Uploaded ({insights.resume.status})
                        </span>
                    ) : (
                        <span className="demo-label">
                            <Clock3 size={13} />
                            Awaiting your resume
                        </span>
                    )}
                </div>

                <div className="stats-grid">
                    {stats.map((stat, index) => {
                        const Icon = stat.icon

                        return (
                            <motion.article
                                key={stat.title}
                                className="stat-card glass-card"
                                initial={{ opacity: 0, y: 15 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                            >
                                <div className={`stat-icon ${stat.color}`}>
                                    <Icon size={21} />
                                </div>

                                <div className="stat-content">
                                    <p className="stat-title">{stat.title}</p>
                                    <h3>{stat.value}</h3>
                                    <span className="stat-desc">{stat.description}</span>
                                </div>
                            </motion.article>
                        )
                    })}
                </div>
            </section>

            {/* Quick Actions */}
            <section className="dashboard-section">
                <div className="section-heading">
                    <div>
                        <h2>Quick Actions</h2>
                        <p>Choose where you want to begin</p>
                    </div>
                </div>

                <div className="actions-grid">
                    {baseActions.map((action) => {
                        const Icon = action.icon

                        return (
                            <motion.div
                                key={action.title}
                                whileHover={{ y: -5 }}
                                transition={{ duration: 0.2 }}
                            >
                                <Link
                                    to={action.path}
                                    className="action-card glass-card"
                                >
                                    <div className="action-icon">
                                        <Icon size={23} />
                                    </div>

                                    <div className="action-body">
                                        <h3>{action.title}</h3>
                                        <p className="action-desc">{action.description}</p>
                                    </div>

                                    <span className="action-link">
                                        <span className="action-link-text">Get started</span>
                                        <ArrowUpRight size={15} />
                                    </span>
                                </Link>
                            </motion.div>
                        )
                    })}
                </div>
            </section>

            {/* Your Next Steps */}
            <section className="dashboard-section">
                <div className="section-heading">
                    <div>
                        <h2>Your Next Steps</h2>
                        <p>Complete these steps to get started</p>
                    </div>
                </div>

                {/* Desktop / Tablet View (> 450px) */}
                <div className="activity-card glass-card desktop-next-steps">
                    {activities.map((activity, idx) => {
                        const Icon = activity.icon
                        const isDone = idx === 0 ? step1Completed : idx === 1 ? step2Completed : step3Completed

                        return (
                            <div className="activity-item" key={activity.title}>
                                <div className="activity-icon">
                                    <Icon size={19} />
                                </div>

                                <div className="activity-info">
                                    <strong>{activity.title}</strong>
                                    <p>{activity.description}</p>
                                </div>

                                <span className={`status-pill ${isDone ? 'completed' : 'pending'}`}>
                                    {isDone ? 'Completed' : 'Pending'}
                                </span>
                            </div>
                        )
                    })}
                </div>

                {/* Compact Horizontal Progress Stepper (Screens <= 450px) */}
                <div className="mobile-timeline-card glass-card">
                    <div className="timeline-track">
                        {/* Step 1: Upload Resume */}
                        <div className="timeline-step">
                            <Link to="/resume" className={`timeline-bubble ${step1Completed ? 'completed' : activeStep === 1 ? 'active' : 'pending'}`}>
                                {step1Completed ? <Check size={14} strokeWidth={2.5} /> : '1'}
                            </Link>
                            <span className="timeline-label">Upload Resume</span>
                        </div>

                        {/* Connector 1 -> 2 */}
                        <div className={`timeline-line ${step1Completed ? 'completed' : 'pending'}`} />

                        {/* Step 2: Analyze Skills */}
                        <div className="timeline-step">
                            <Link to="/skills" className={`timeline-bubble ${step2Completed ? 'completed' : activeStep === 2 ? 'active' : 'pending'}`}>
                                {step2Completed ? <Check size={14} strokeWidth={2.5} /> : '2'}
                            </Link>
                            <span className="timeline-label">Analyze Skills</span>
                        </div>

                        {/* Connector 2 -> 3 */}
                        <div className={`timeline-line ${step2Completed ? 'completed' : 'pending'}`} />

                        {/* Step 3: Start Learning */}
                        <div className="timeline-step">
                            <Link to="/roadmap" className={`timeline-bubble ${step3Completed ? 'completed' : activeStep === 3 ? 'active' : 'pending'}`}>
                                {step3Completed ? <Check size={14} strokeWidth={2.5} /> : '3'}
                            </Link>
                            <span className="timeline-label">Start Learning</span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}
