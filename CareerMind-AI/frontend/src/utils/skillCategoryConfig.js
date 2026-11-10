import {
    Code2,
    Layout,
    Server,
    Database,
    BarChart3,
    Brain,
    Cpu,
    Cloud,
    Wrench,
    Boxes,
} from 'lucide-react'

export const SKILL_CATEGORIES = {
    programming_languages: {
        label: 'Programming Languages',
        shortLabel: 'Languages',
        icon: Code2,
        color: '#8b5cf6',
        badgeClass: 'bg-violet-50 text-violet-700 border-violet-200 dark:bg-violet-500/10 dark:text-violet-300 dark:border-violet-500/20',
    },
    frontend: {
        label: 'Frontend Technologies',
        shortLabel: 'Frontend',
        icon: Layout,
        color: '#3b82f6',
        badgeClass: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-300 dark:border-blue-500/20',
    },
    backend: {
        label: 'Backend Technologies',
        shortLabel: 'Backend',
        icon: Server,
        color: '#10b981',
        badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:border-emerald-500/20',
    },
    databases: {
        label: 'Databases',
        shortLabel: 'Databases',
        icon: Database,
        color: '#f59e0b',
        badgeClass: 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:border-amber-500/20',
    },
    data_analytics: {
        label: 'Data Analytics & BI',
        shortLabel: 'Analytics',
        icon: BarChart3,
        color: '#ec4899',
        badgeClass: 'bg-pink-50 text-pink-700 border-pink-200 dark:bg-pink-500/10 dark:text-pink-300 dark:border-pink-500/20',
    },
    machine_learning: {
        label: 'Machine Learning',
        shortLabel: 'ML',
        icon: Brain,
        color: '#6366f1',
        badgeClass: 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-500/10 dark:text-indigo-300 dark:border-indigo-500/20',
    },
    deep_learning: {
        label: 'Deep Learning & AI',
        shortLabel: 'AI & DL',
        icon: Cpu,
        color: '#d946ef',
        badgeClass: 'bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200 dark:bg-fuchsia-500/10 dark:text-fuchsia-300 dark:border-fuchsia-500/20',
    },
    cloud_devops: {
        label: 'Cloud & DevOps',
        shortLabel: 'Cloud/DevOps',
        icon: Cloud,
        color: '#0ea5e9',
        badgeClass: 'bg-sky-50 text-sky-700 border-sky-200 dark:bg-sky-500/10 dark:text-sky-300 dark:border-sky-500/20',
    },
    tools: {
        label: 'Tools & Platforms',
        shortLabel: 'Tools',
        icon: Wrench,
        color: '#f97316',
        badgeClass: 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-500/10 dark:text-orange-300 dark:border-orange-500/20',
    },
    other: {
        label: 'Other Concepts',
        shortLabel: 'Other',
        icon: Boxes,
        color: '#64748b',
        badgeClass: 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-500/10 dark:text-slate-300 dark:border-slate-500/20',
    },
}

export function getCategoryMeta(key) {
    if (!key) {
        return {
            label: 'Other Concepts',
            shortLabel: 'Other',
            icon: Boxes,
            color: '#64748b',
            badgeClass: 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-500/10 dark:text-slate-300 dark:border-slate-500/20',
        }
    }
    const normalizedKey = String(key).toLowerCase().trim()
    return (
        SKILL_CATEGORIES[normalizedKey] || {
            label: key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
            shortLabel: key,
            icon: Boxes,
            color: '#8b5cf6',
            badgeClass: 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-500/10 dark:text-purple-300 dark:border-purple-500/20',
        }
    )
}

