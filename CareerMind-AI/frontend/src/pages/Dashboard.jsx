
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
} from 'lucide-react'

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

const actions = [
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
    return (
        <div className="dashboard-page">

            <motion.section
                className="welcome-banner glass-card"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <div className="welcome-content">
                    <div className="welcome-tag">
                        <Sparkles size={14} />
                        AI CAREER INTELLIGENCE
                    </div>

                    <h1>
                        Your career journey
                        <br />
                        starts <span className="gradient-text">here.</span>
                    </h1>

                    <p>
                        Analyze your skills, discover opportunities,
                        and build a smarter career path with AI.
                    </p>

                    <Link to="/resume" className="primary-button">
                        <FileSearch size={18} />
                        Analyze my resume
                        <ArrowUpRight size={17} />
                    </Link>
                </div>

                <div className="welcome-decoration">
                    <div className="orbit orbit-one" />
                    <div className="orbit orbit-two" />
                    <div className="welcome-sparkle">
                        <Sparkles size={54} />
                    </div>
                </div>
            </motion.section>

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
                    {actions.map((action) => {
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
