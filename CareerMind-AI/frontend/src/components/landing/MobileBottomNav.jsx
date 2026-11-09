import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Layers, Workflow, UserPlus } from 'lucide-react'

export default function MobileBottomNav() {
    const location = useLocation()
    const isOnboarding = location.pathname === '/onboarding'
    const [scrollTab, setScrollTab] = useState('home')

    const activeTab = isOnboarding ? 'get-started' : scrollTab

    useEffect(() => {
        if (isOnboarding) return

        const handleScroll = () => {
            const scrollPos = window.scrollY || document.documentElement.scrollTop

            const featuresEl = document.getElementById('features')
            const howItWorksEl = document.getElementById('how-it-works')

            const offset = 200

            if (howItWorksEl && scrollPos >= howItWorksEl.offsetTop - offset) {
                setScrollTab('how-it-works')
            } else if (featuresEl && scrollPos >= featuresEl.offsetTop - offset) {
                setScrollTab('features')
            } else {
                setScrollTab('home')
            }
        }

        window.addEventListener('scroll', handleScroll, { passive: true })
        handleScroll()

        return () => window.removeEventListener('scroll', handleScroll)
    }, [isOnboarding])

    const handleHomeClick = (e) => {
        setScrollTab('home')
        if (location.pathname === '/') {
            e.preventDefault()
            window.scrollTo({ top: 0, behavior: 'smooth' })
        }
    }

    const handleAnchorClick = (tabId) => {
        setScrollTab(tabId)
    }

    const NAV_ITEMS = [
        {
            id: 'home',
            label: 'Home',
            icon: Home,
            href: '/',
            onClick: handleHomeClick,
            isLink: true,
        },
        {
            id: 'features',
            label: 'Features',
            icon: Layers,
            href: '#features',
            onClick: () => handleAnchorClick('features'),
            isLink: false,
        },
        {
            id: 'how-it-works',
            label: 'How It Works',
            icon: Workflow,
            href: '#how-it-works',
            onClick: () => handleAnchorClick('how-it-works'),
            isLink: false,
        },
        {
            id: 'get-started',
            label: 'Get Started',
            icon: UserPlus,
            href: '/onboarding',
            onClick: () => handleAnchorClick('get-started'),
            isLink: true,
        },
    ]

    return (
        <nav
            aria-label="Mobile Bottom Navigation"
            className="fixed bottom-0 left-0 right-0 z-50 md:hidden border-t border-purple-200/80 dark:border-purple-900/40 bg-white/95 dark:bg-[#0D0A1A]/95 backdrop-blur-xl shadow-[0_-4px_20px_rgba(109,40,217,0.06)] dark:shadow-[0_-4px_20px_rgba(0,0,0,0.5)] transition-colors duration-200 pb-[calc(env(safe-area-inset-bottom,0px)+2px)]"
        >
            <div className="grid grid-cols-4 w-full max-w-md mx-auto items-stretch h-14 sm:h-16">
                {NAV_ITEMS.map((item) => {
                    const Icon = item.icon
                    const isActive = activeTab === item.id

                    const content = (
                        <div className="relative flex flex-col items-center justify-center w-full h-full py-1 px-1 transition-transform active:scale-95">
                            {/* Subtle Active Indicator Pill */}
                            {isActive && (
                                <span className="absolute top-0 w-8 h-1 rounded-full bg-gradient-to-r from-[#6D28D9] to-[#8B5CF6] dark:from-[#8B5CF6] dark:to-[#C4B5FD] shadow-sm shadow-purple-500/50" />
                            )}

                            <div
                                className={`flex items-center justify-center transition-colors duration-200 ${
                                    isActive
                                        ? 'text-[#6D28D9] dark:text-[#A78BFA] scale-105'
                                        : 'text-[#64748B] dark:text-[#8E8AA7] hover:text-[#6D28D9] dark:hover:text-[#C4B5FD]'
                                }`}
                            >
                                <Icon size={19} strokeWidth={isActive ? 2.4 : 2} />
                            </div>

                            <span
                                className={`text-[10px] sm:text-[11px] tracking-tight leading-tight mt-1 whitespace-nowrap transition-colors duration-200 ${
                                    isActive
                                        ? 'font-bold text-[#6D28D9] dark:text-[#A78BFA]'
                                        : 'font-semibold text-[#64748B] dark:text-[#8E8AA7]'
                                }`}
                            >
                                {item.label}
                            </span>
                        </div>
                    )

                    return item.isLink ? (
                        <Link
                            key={item.id}
                            to={item.href}
                            onClick={item.onClick}
                            aria-label={item.label}
                            aria-current={isActive ? 'page' : undefined}
                            className="flex items-center justify-center focus:outline-none"
                        >
                            {content}
                        </Link>
                    ) : (
                        <a
                            key={item.id}
                            href={item.href}
                            onClick={item.onClick}
                            aria-label={item.label}
                            aria-current={isActive ? 'true' : undefined}
                            className="flex items-center justify-center focus:outline-none"
                        >
                            {content}
                        </a>
                    )
                })}
            </div>
        </nav>
    )
}
