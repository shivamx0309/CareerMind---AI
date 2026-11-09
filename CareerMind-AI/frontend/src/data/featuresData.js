import { FileText, Briefcase, Target, BookOpen, Monitor } from 'lucide-react'

/**
 * CareerMind AI — Platform Features Data Catalog (5 Interactive Features)
 */
export const FEATURES_LIST = [
    {
        id: 'resume-intelligence',
        index: 0,
        number: '01',
        title: 'Resume Intelligence',
        selectorTitle: 'Resume Intelligence',
        icon: FileText,
        description: 'Upload your resume and automatically extract skills, experience, education, projects and certifications.',
        benefits: [
            'Skill & experience extraction',
            'Project and tenure analysis',
            'Clean, structured profile',
        ],
        status: 'Available',
        ctaLabel: 'Analyze Resume',
        destination: '/resume',
        isImplemented: true,
    },
    {
        id: 'job-matching',
        index: 1,
        number: '02',
        title: 'Job Description Matching',
        selectorTitle: 'Job Matching',
        icon: Briefcase,
        description: 'Compare your resume with job descriptions and understand your professional alignment.',
        benefits: [
            'Multi-dimensional score breakdown',
            'Direct & canonical alias matching',
            'Actionable gap recommendations',
        ],
        status: 'Available',
        ctaLabel: 'Match Job Description',
        destination: '/jobs',
        isImplemented: true,
    },
    {
        id: 'skill-gap',
        index: 2,
        number: '03',
        title: 'Skill Gap Analysis',
        selectorTitle: 'Skill Gap Analysis',
        icon: Target,
        description: 'Identify your existing skills and discover the areas you need to improve.',
        benefits: [
            'Granular proficiency evaluation',
            'Market requirement comparison',
            'Priority gap ranking',
        ],
        status: 'Available',
        ctaLabel: 'Explore Skill Gaps',
        destination: null,
        isImplemented: false,
    },
    {
        id: 'learning-roadmap',
        index: 3,
        number: '04',
        title: 'Personalized Learning Roadmap',
        selectorTitle: 'Learning Roadmap',
        icon: BookOpen,
        description: 'Build a structured learning path based on your career goals and target job requirements.',
        benefits: [
            'Milestone-driven study roadmap',
            'Curated open-source resources',
            'Skill acquisition tracking',
        ],
        status: 'Available',
        ctaLabel: 'View Learning Roadmap',
        destination: null,
        isImplemented: false,
    },
    {
        id: 'ai-interview',
        index: 4,
        number: '05',
        title: 'AI Interview Preparation',
        selectorTitle: 'AI Interview',
        icon: Monitor,
        description: 'Practice relevant interview questions and evaluate your preparation.',
        benefits: [
            'Role-specific mock interview questions',
            'Instant answer feedback & scoring',
            'Behavioral & technical readiness',
        ],
        status: 'Available',
        ctaLabel: 'Prepare for Interview',
        destination: null,
        isImplemented: false,
    },
]

export const FEATURES_DATA = FEATURES_LIST.reduce((acc, feat) => {
    acc[feat.id] = feat
    return acc
}, {})

export const INITIAL_FEATURED_ID = 'resume-intelligence'
export const INITIAL_SMALL_CARD_IDS = [
    'job-matching',
    'skill-gap',
    'learning-roadmap',
    'ai-interview',
]
