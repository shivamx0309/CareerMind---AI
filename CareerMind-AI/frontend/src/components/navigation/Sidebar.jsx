
import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard,
    FileSearch,
    BriefcaseBusiness,
    ChartNoAxesCombined,
    Route,
    MessageSquare,
    Sparkles,
    ChevronLeft,
    ChevronRight,
    X,
} from 'lucide-react'
import { motion } from 'framer-motion'

const navigation = [
    {
        title: 'OVERVIEW',
        items: [
            { label: 'Dashboard', path: '/', icon: LayoutDashboard },
        ],
    },
    {
        title: 'CAREER TOOLS',
        items: [
            { label: 'Resume Analyzer', path: '/resume', icon: FileSearch },
            { label: 'Job Matcher', path: '/jobs', icon: BriefcaseBusiness },
            { label: 'Skill Gap', path: '/skills', icon: ChartNoAxesCombined },
            { label: 'Learning Roadmap', path: '/roadmap', icon: Route },
            { label: 'AI Interview', path: '/interview', icon: MessageSquare },
        ],
    },
]

export default function Sidebar({
    collapsed,
    setCollapsed,
    mobileOpen,
    setMobileOpen,
}) {
    return (
        <>
            {mobileOpen && (
                <button
                    className="sidebar-overlay"
                    onClick={() => setMobileOpen(false)}
                    aria-label="Close navigation"
                />
            )}

            <motion.aside
                initial={false}
                animate={{ width: collapsed ? 88 : 260 }}
                className={`sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}
            >
                <div className="sidebar-brand">
                    <div className="brand-icon">
                        <Sparkles size={23} />
                    </div>

                    {!collapsed && (
                        <div className="brand-name">
                            <span>CareerMind</span>
                            <small>AI CAREER INTELLIGENCE</small>
                        </div>
                    )}

                    <button
                        className="mobile-close"
                        onClick={() => setMobileOpen(false)}
                        aria-label="Close sidebar"
                    >
                        <X size={19} />
                    </button>
                </div>

                <div className="sidebar-navigation">
                    {navigation.map((group) => (
                        <div className="nav-group" key={group.title}>
                            {!collapsed && (
                                <p className="nav-group-title">{group.title}</p>
                            )}

                            {group.items.map((item) => {
                                const Icon = item.icon

                                return (
                                    <NavLink
                                        to={item.path}
                                        end={item.path === '/'}
                                        key={item.path}
                                        onClick={() => setMobileOpen(false)}
                                        className={({ isActive }) =>
                                            `nav-item ${isActive ? 'active' : ''}`
                                        }
                                        title={collapsed ? item.label : undefined}
                                    >
                                        <Icon size={19} strokeWidth={1.8} />
                                        {!collapsed && <span>{item.label}</span>}
                                    </NavLink>
                                )
                            })}
                        </div>
                    ))}
                </div>

                <div className="sidebar-bottom">
                    {!collapsed && (
                        <div className="sidebar-upgrade">
                            <Sparkles size={20} />
                            <strong>Career growth starts here</strong>
                            <p>Build skills. Prepare. Get hired.</p>
                        </div>
                    )}

                    <button
                        className="collapse-button"
                        onClick={() => setCollapsed(!collapsed)}
                        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                    >
                        {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                        {!collapsed && <span>Collapse sidebar</span>}
                    </button>
                </div>
            </motion.aside>
        </>
    )
}
