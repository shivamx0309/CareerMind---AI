import { FileText, Briefcase, Target, BookOpen, BarChart3 } from 'lucide-react'

/**
 * CareerMind AI — Platform Features Data Catalog
 *
 * Distinct data structure for interactive feature swapping:
 * - 2 Available features (routed to /resume and /jobs)
 * - 3 Planned features (with planned indicators and non-functional safeguards)
 */
export const FEATURES_DATA = {
    'resume-intelligence': {
        id: 'resume-intelligence',
        number: '01',
        title: 'Resume Intelligence',
        icon: FileText,
        description: 'Upload your resume and automatically extract key skills, experience and education.',
        benefits: [
            'Skill & experience extraction',
            'Project and tenure analysis',
            'Clean, structured insights',
        ],
        status: 'Available',
        ctaLabel: 'Analyze Resume',
        destination: '/resume',
    },
    'job-matching': {
        id: 'job-matching',
        number: '02',
        title: 'Job Description Matching',
        icon: Briefcase,
        description: 'Compare your profile with job descriptions and find the best matching opportunities.',
        benefits: [
            'Multi-dimensional score breakdown',
            'Direct & canonical alias matching',
            'Actionable gap recommendations',
        ],
        status: 'Available',
        ctaLabel: 'Run Job Matcher',
        destination: '/jobs',
    },
    'skill-gap': {
        id: 'skill-gap',
        number: '03',
        title: 'Skill Gap Analysis',
        icon: Target,
        description: 'Identify the skills you have and the key areas to improve for your target roles.',
        benefits: [
            'Granular proficiency evaluation',
            'Market requirement comparison',
            'Priority gap ranking',
        ],
        status: 'Planned',
        ctaLabel: 'Coming in Future Phase',
        destination: null,
    },
    'learning-path': {
        id: 'learning-path',
        number: '04',
        title: 'Learning Path',
        icon: BookOpen,
        description: 'Get a personalized learning plan to build the skills you need for your target roles.',
        benefits: [
            'Milestone-driven study roadmap',
            'Curated open-source resources',
            'Skill acquisition tracking',
        ],
        status: 'Planned',
        ctaLabel: 'Coming in Future Phase',
        destination: null,
    },
    'career-insights': {
        id: 'career-insights',
        number: '05',
        title: 'Career Insights',
        icon: BarChart3,
        description: 'Explore role trends, required skills and career opportunities in your domain.',
        benefits: [
            'Role competency benchmarks',
            'Salary & experience trajectories',
            'Domain growth trajectories',
        ],
        status: 'Planned',
        ctaLabel: 'Coming in Future Phase',
        destination: null,
    },
}

/**
 * Initial showcase layout state:
 * - Left large card: 'resume-intelligence'
 * - Right 2x2 grid: ['job-matching', 'skill-gap', 'learning-path', 'career-insights']
 */
export const INITIAL_FEATURED_ID = 'resume-intelligence'

export const INITIAL_SMALL_CARD_IDS = [
    'job-matching',
    'skill-gap',
    'learning-path',
    'career-insights',
]

