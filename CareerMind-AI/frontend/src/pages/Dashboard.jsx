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
    CircleCheck,
    Upload,
    MessageSquare,
    UserCheck,
    GraduationCap,
    MapPin,
    Briefcase,
    Edit3,
} from 'lucide-react'
import { useCareerProfile } from '../context/CareerProfileContext'

const stats = [
    {
        title: 'Resume Analysis',
        value: 'Not started',
        description: 'Upload your resume to begin',
        icon: FileSearch,
        color: 'purple',
    },
    {
        title: 'Jobs Matched',
        value: '0',
        description: 'Analyze job descriptions',
        icon: BriefcaseBusiness,
        color: 'blue',
    },
    {
        title: 'Skills Identified',
        value: '0',
        description: 'Discover your skill profile',
        icon: Target,
        color: 'green',
    },
    {
        title: 'Learning Progress',
        value: '0%',
        description: 'Your roadmap progress',
        icon: BookOpen,
        color: 'orange',
    },
]

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

                <div className="welcome-decoration">
                    <div className="orbit orbit-one" />
                    <div className="orbit orbit-two" />
                    <div className="welcome-sparkle">
                        <Sparkles size={54} />
                    </div>
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

                        {profile.career_objective && (
                            <div className="rounded-xl bg-[var(--surface-hover)]/40 p-3 text-xs text-[var(--text-secondary)] leading-relaxed">
                                <strong className="font-semibold text-[var(--text-primary)] mr-1">Objective:</strong>
                                <span>{profile.career_objective}</span>
                            </div>
                        )}
                    </div>
                </section>
            )}

            <section className="dashboard-section">
                <div className="section-heading">
                    <div>
                        <h2>Career Overview</h2>
                        <p>Your career intelligence at a glance</p>
                    </div>

                    <span className="demo-label">
                        <Clock3 size={13} />
                        Awaiting your resume
                    </span>
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
                                transition={{ delay: index * 0.08 }}
                            >
                                <div className={`stat-icon ${stat.color}`}>
                                    <Icon size={21} />
                                </div>

                                <p className="stat-title">{stat.title}</p>
                                <h3>{stat.value}</h3>
                                <span>{stat.description}</span>
                            </motion.article>
                        )
                    })}
                </div>
            </section>

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

                                    <h3>{action.title}</h3>
                                    <p>{action.description}</p>

                                    <span className="action-link">
                                        Get started <ArrowUpRight size={15} />
                                    </span>
                                </Link>
                            </motion.div>
                        )
                    })}
                </div>
            </section>

            <section className="dashboard-section">
                <div className="section-heading">
                    <div>
                        <h2>Your Next Steps</h2>
                        <p>Complete these steps to get started</p>
                    </div>
                </div>

                <div className="activity-card glass-card">
                    {activities.map((activity) => {
                        const Icon = activity.icon

                        return (
                            <div className="activity-item" key={activity.title}>
                                <div className="activity-icon">
                                    <Icon size={19} />
                                </div>

                                <div className="activity-info">
                                    <strong>{activity.title}</strong>
                                    <span>{activity.description}</span>
                                </div>

                                <span className="activity-status">
                                    <CircleCheck size={16} />
                                    Pending
                                </span>
                            </div>
                        )
                    })}
                </div>
            </section>

            <footer className="dashboard-footer">
                <Sparkles size={15} />
                CareerMind AI — Your intelligent career companion.
            </footer>

        </div>
    )
}
