import {
    Sun,
    Moon,
    Search,
    Bell,
    UserCheck,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import { useCareerProfile } from '../../context/CareerProfileContext'
import MindyMascot from '../common/MindyMascot'

export default function Topbar({ onMenuClick }) {
    const { theme, toggleTheme } = useTheme()
    const { profile } = useCareerProfile()

    const displayName = profile?.full_name || 'Career Explorer'
    const displayRole = profile?.primary_target_role || 'Workspace User'
    const avatarLetter = (displayName.charAt(0) || 'U').toUpperCase()

    return (
        <header className="topbar">
            <div className="topbar-left">
                <Link to="/" className="topbar-brand-mobile" title="CareerMind AI Home">
                    <div className="brand-icon relative overflow-hidden bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] !w-9 !h-9 !min-w-[36px] !rounded-xl">
                        <MindyMascot expression="chatbot" size="xs" alt="CareerMind Logo" className="scale-125 translate-y-0.5" />
                    </div>
                </Link>

                <div className="topbar-greeting">
                    <span>Workspace</span>
                    <small>Career Intelligence Platform</small>
                </div>
            </div>

            <div className="topbar-actions">
                <label className="topbar-search">
                    <Search size={17} />
                    <input
                        type="search"
                        placeholder="Search anything..."
                        aria-label="Search anything"
                    />
                    <kbd>⌘ K</kbd>
                </label>

                <button
                    className="icon-button theme-toggle"
                    onClick={toggleTheme}
                    aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
                    title="Toggle theme"
                >
                    {theme === 'dark' ? <Sun size={19} /> : <Moon size={19} />}
                </button>

                <button
                    className="icon-button notification-button"
                    aria-label="Notifications"
                >
                    <Bell size={19} />
                    <span className="notification-dot" />
                </button>

                <div className="topbar-divider" />

                <Link
                    to="/onboarding?edit=true"
                    className="profile-button text-left"
                    title="Click to edit your career profile"
                >
                    <div className="profile-avatar">{avatarLetter}</div>

                    <div className="profile-info">
                        <strong>{displayName}</strong>
                        <span className="truncate max-w-[120px]">{displayRole}</span>
                    </div>

                    <UserCheck size={14} className="text-[var(--text-muted)] ml-1" />
                </Link>
            </div>
        </header>
    )
}
