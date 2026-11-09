import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard,
    FileSearch,
    BriefcaseBusiness,
    ChartNoAxesCombined,
    Route,
    MessageSquare,
} from 'lucide-react'

const DASHBOARD_NAV_ITEMS = [
    {
        label: 'Dashboard',
        shortLabel: 'Dashboard',
        path: '/dashboard',
        icon: LayoutDashboard,
    },
    {
        label: 'Resume Analyzer',
        shortLabel: 'Resume',
        path: '/resume',
        icon: FileSearch,
    },
    {
        label: 'Job Matcher',
        shortLabel: 'Jobs',
        path: '/jobs',
        icon: BriefcaseBusiness,
    },
    {
        label: 'Skill Gap',
        shortLabel: 'Skills',
        path: '/skills',
        icon: ChartNoAxesCombined,
    },
    {
        label: 'Learning Roadmap',
        shortLabel: 'Roadmap',
        path: '/roadmap',
        icon: Route,
    },
    {
        label: 'AI Interview',
        shortLabel: 'Interview',
        path: '/interview',
        icon: MessageSquare,
    },
]

export default function DashboardBottomNav() {
    return (
        <nav
            aria-label="Mobile and Tablet Dashboard Navigation"
            className="dashboard-bottom-nav"
        >
            <div className="dashboard-bottom-nav-inner">
                {DASHBOARD_NAV_ITEMS.map((item) => {
                    const Icon = item.icon

                    return (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            end={item.path === '/dashboard'}
                            className={({ isActive }) =>
                                `dashboard-bottom-nav-item ${isActive ? 'active' : ''}`
                            }
                        >
                            {({ isActive }) => (
                                <>
                                    {/* Active top accent pill indicator */}
                                    {isActive && (
                                        <span className="dashboard-bottom-indicator" />
                                    )}

                                    {/* Icon container */}
                                    <div className="dashboard-bottom-icon-wrap">
                                        <Icon size={18} strokeWidth={isActive ? 2.3 : 1.8} />
                                    </div>

                                    {/* Item Label */}
                                    <span className="dashboard-bottom-label">
                                        {item.shortLabel}
                                    </span>
                                </>
                            )}
                        </NavLink>
                    )
                })}
            </div>
        </nav>
    )
}
