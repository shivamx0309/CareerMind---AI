
import {
    Menu,
    Sun,
    Moon,
    Search,
    Bell,
    ChevronDown,
} from 'lucide-react'

import { useTheme } from '../../context/ThemeContext'

export default function Topbar({ onMenuClick }) {
    const { theme, toggleTheme } = useTheme()

    return (
        <header className="topbar">
            <div className="topbar-left">
                <button
                    className="icon-button mobile-menu-button"
                    onClick={onMenuClick}
                    aria-label="Open navigation"
                >
                    <Menu size={21} />
                </button>

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

                <button className="profile-button">
                    <div className="profile-avatar">S</div>

                    <div className="profile-info">
                        <strong>Shivam</strong>
                        <span>Career Explorer</span>
                    </div>

                    <ChevronDown size={16} />
                </button>
            </div>
        </header>
    )
}
