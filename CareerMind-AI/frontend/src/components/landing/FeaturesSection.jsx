import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Sparkles,
    Check,
    ChevronLeft,
    ChevronRight,
    ArrowRight,
    ShieldCheck,
    Layers,
    Zap,
    Info,
    X,
} from 'lucide-react'
import { FEATURES_LIST } from '../../data/featuresData'

export default function FeaturesSection() {
    const [currentIndex, setCurrentIndex] = useState(0)
    const [direction, setDirection] = useState(1) // 1 = right, -1 = left
    const [isPaused, setIsPaused] = useState(false)
    const [toastMessage, setToastMessage] = useState(null)

    // Touch swipe handling refs
    const touchStartX = useRef(null)
    const touchEndX = useRef(null)
    const selectorsContainerRef = useRef(null)

    const totalFeatures = FEATURES_LIST.length
    const currentFeature = FEATURES_LIST[currentIndex]

    const handleNext = useCallback(() => {
        setDirection(1)
        setCurrentIndex((prev) => (prev + 1) % totalFeatures)
        const landing = document.querySelector('.landing-page-container')
        if (landing && landing.scrollLeft !== 0) landing.scrollLeft = 0
        if (window.scrollX !== 0) window.scrollTo(0, window.scrollY)
    }, [totalFeatures])

    const handlePrev = useCallback(() => {
        setDirection(-1)
        setCurrentIndex((prev) => (prev - 1 + totalFeatures) % totalFeatures)
        const landing = document.querySelector('.landing-page-container')
        if (landing && landing.scrollLeft !== 0) landing.scrollLeft = 0
        if (window.scrollX !== 0) window.scrollTo(0, window.scrollY)
    }, [totalFeatures])

    const goToIndex = (idx) => {
        if (idx === currentIndex) return
        setDirection(idx > currentIndex ? 1 : -1)
        setCurrentIndex(idx)
        const landing = document.querySelector('.landing-page-container')
        if (landing && landing.scrollLeft !== 0) landing.scrollLeft = 0
        if (window.scrollX !== 0) window.scrollTo(0, window.scrollY)
    }

    // 4-Second Autoplay Timer
    useEffect(() => {
        if (isPaused) return

        const timer = setInterval(() => {
            handleNext()
        }, 4000)

        return () => clearInterval(timer)
    }, [isPaused, handleNext])

    // Auto-scroll ONLY the horizontal selectors container internally (NEVER the page/window)
    useEffect(() => {
        const container = selectorsContainerRef.current
        if (!container) return

        const activeSelector = container.children[currentIndex]
        if (activeSelector) {
            const containerWidth = container.clientWidth
            const selectorLeft = activeSelector.offsetLeft
            const selectorWidth = activeSelector.clientWidth
            const scrollTarget = selectorLeft - (containerWidth / 2) + (selectorWidth / 2)

            container.scrollTo({
                left: Math.max(0, scrollTarget),
                behavior: 'smooth',
            })
        }
    }, [currentIndex])

    // Prevent any horizontal viewport shift on mobile
    useEffect(() => {
        const landing = document.querySelector('.landing-page-container')
        const clampHorizontal = () => {
            if (landing && landing.scrollLeft !== 0) {
                landing.scrollLeft = 0
            }
            if (window.scrollX !== 0) {
                window.scrollTo(0, window.scrollY)
            }
        }

        if (landing) {
            landing.addEventListener('scroll', clampHorizontal, { passive: true })
        }
        window.addEventListener('scroll', clampHorizontal, { passive: true })

        return () => {
            if (landing) {
                landing.removeEventListener('scroll', clampHorizontal)
            }
            window.removeEventListener('scroll', clampHorizontal)
        }
    }, [])

    // Touch Swipe Handlers for Mobile
    const handleTouchStart = (e) => {
        touchStartX.current = e.targetTouches[0].clientX
        touchEndX.current = null
        setIsPaused(true)
    }

    const handleTouchMove = (e) => {
        touchEndX.current = e.targetTouches[0].clientX
    }

    const handleTouchEnd = () => {
        if (touchStartX.current !== null && touchEndX.current !== null) {
            const diff = touchStartX.current - touchEndX.current
            const minSwipe = 45 // min px threshold for swipe

            if (diff > minSwipe) {
                handleNext()
            } else if (diff < -minSwipe) {
                handlePrev()
            }
        }
        setIsPaused(false)
    }

    const handlePlaceholderCta = (featureTitle) => {
        setToastMessage({
            title: featureTitle,
            text: 'This feature is ready for calibration. Workspace sandbox preview is launching in the upcoming release!',
        })
        setTimeout(() => setToastMessage(null), 4500)
    }

    // Slide transition variants
    const slideVariants = {
        enter: (dir) => ({
            x: dir > 0 ? 80 : -80,
            opacity: 0,
            scale: 0.98,
        }),
        center: {
            x: 0,
            opacity: 1,
            scale: 1,
            transition: {
                x: { type: 'spring', stiffness: 300, damping: 30 },
                opacity: { duration: 0.28 },
                scale: { duration: 0.28 },
            },
        },
        exit: (dir) => ({
            x: dir > 0 ? -80 : 80,
            opacity: 0,
            scale: 0.98,
            transition: {
                x: { type: 'spring', stiffness: 300, damping: 30 },
                opacity: { duration: 0.2 },
            },
        }),
    }

    const Icon = currentFeature.icon

    return (
        <section
            id="features"
            className="py-10 sm:py-20 border-t border-purple-200/60 dark:border-purple-900/30 relative overflow-hidden"
        >
            {/* Ambient Background Aura */}
            <div className="pointer-events-none absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[450px] bg-gradient-to-tr from-[#6D28D9]/12 via-[#8B5CF6]/12 to-[#C4B5FD]/10 rounded-full blur-3xl -z-10" />

            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10 sm:space-y-12">
                {/* 1. Header & Subtitle */}
                <div className="text-center space-y-3.5 max-w-2xl mx-auto">
                    <div className="inline-flex items-center gap-1.5 rounded-full border border-purple-200/90 dark:border-purple-500/30 bg-[#EDE9FE] dark:bg-purple-950/40 px-4 py-1 text-xs font-bold text-[#6D28D9] dark:text-[#C4B5FD] shadow-sm">
                        <Sparkles size={13} className="text-[#6D28D9] dark:text-[#C4B5FD]" />
                        <span>Features</span>
                    </div>

                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-[#17172E] dark:text-[#F8FAFC]">
                        Powerful Features for{' '}
                        <span className="purple-gradient-text block sm:inline">
                            Your Career Growth
                        </span>
                    </h2>

                    <p className="text-sm sm:text-base text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed max-w-xl mx-auto">
                        A complete set of AI-powered tools to analyze, match, improve and prepare for your next opportunity.
                    </p>
                </div>

                {/* 2. Interactive Feature Carousel Container */}
                <div
                    className="relative max-w-2xl sm:max-w-3xl mx-auto"
                    onMouseEnter={() => setIsPaused(true)}
                    onMouseLeave={() => setIsPaused(false)}
                    onTouchStart={handleTouchStart}
                    onTouchMove={handleTouchMove}
                    onTouchEnd={handleTouchEnd}
                >
                    {/* Left & Right Visual Peek Cards (matching screenshot aesthetic) */}
                    <div className="pointer-events-none absolute -left-2 sm:-left-8 top-4 bottom-4 w-12 sm:w-20 rounded-3xl bg-gradient-to-r from-[#6D28D9]/40 to-[#8B5CF6]/20 blur-xs opacity-50 -z-0" />
                    <div className="pointer-events-none absolute -right-2 sm:-right-8 top-4 bottom-4 w-12 sm:w-20 rounded-3xl bg-gradient-to-l from-[#6D28D9]/40 to-[#8B5CF6]/20 blur-xs opacity-50 -z-0" />

                    {/* Navigation Arrow Controls */}
                    <button
                        type="button"
                        onClick={handlePrev}
                        aria-label="Previous feature"
                        className="absolute left-0 sm:-left-4 top-1/2 -translate-y-1/2 z-20 flex h-9 w-9 sm:h-11 sm:w-11 items-center justify-center rounded-full bg-white dark:bg-[#1E163B] text-[#6D28D9] dark:text-[#C4B5FD] shadow-xl border border-purple-200/90 dark:border-purple-700/50 hover:scale-110 active:scale-95 transition-all cursor-pointer"
                    >
                        <ChevronLeft size={20} strokeWidth={2.4} />
                    </button>

                    <button
                        type="button"
                        onClick={handleNext}
                        aria-label="Next feature"
                        className="absolute right-0 sm:-right-4 top-1/2 -translate-y-1/2 z-20 flex h-9 w-9 sm:h-11 sm:w-11 items-center justify-center rounded-full bg-white dark:bg-[#1E163B] text-[#6D28D9] dark:text-[#C4B5FD] shadow-xl border border-purple-200/90 dark:border-purple-700/50 hover:scale-110 active:scale-95 transition-all cursor-pointer"
                    >
                        <ChevronRight size={20} strokeWidth={2.4} />
                    </button>

                    {/* Main Active Feature Card */}
                    <div className="relative z-10 w-[92%] sm:w-[94%] mx-auto overflow-hidden rounded-3xl p-5 sm:p-8 bg-gradient-to-br from-[#6D28D9] via-[#7C3AED] to-[#8B5CF6] text-white shadow-2xl shadow-purple-900/35 border border-purple-400/35 min-h-[350px] sm:min-h-[400px] flex flex-col justify-between">
                        {/* Ambient Card Background Glow */}
                        <div className="pointer-events-none absolute -top-16 -right-16 w-48 h-48 rounded-full bg-white/10 blur-2xl" />

                        <AnimatePresence custom={direction} mode="wait">
                            <motion.div
                                key={currentFeature.id}
                                custom={direction}
                                variants={slideVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
                                className="flex flex-col justify-between h-full space-y-4 sm:space-y-6"
                            >
                                <div>
                                    {/* Top Row: Icon Container, Counter Pill & Available Badge */}
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex h-11 w-11 sm:h-13 sm:w-13 items-center justify-center rounded-2xl bg-white/15 border border-white/25 text-white shadow-inner backdrop-blur-md">
                                            <Icon size={24} strokeWidth={2.2} />
                                        </div>

                                        {/* Center Counter Pill */}
                                        <span className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-white/20 border border-white/30 text-white text-xs font-black tracking-wider backdrop-blur-md shadow-sm">
                                            {currentFeature.number} / 05
                                        </span>

                                        {/* Green Available Badge (on all 5 features) */}
                                        <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold bg-emerald-400/25 border border-emerald-300/40 text-emerald-100 backdrop-blur-md shadow-sm">
                                            <Check size={13} strokeWidth={3} />
                                            <span>Available</span>
                                        </span>
                                    </div>

                                    {/* Feature Title */}
                                    <h3 className="text-xl sm:text-3xl font-extrabold text-white tracking-tight mb-2">
                                        {currentFeature.title}
                                    </h3>

                                    {/* Description */}
                                    <p className="text-xs sm:text-sm text-purple-100/90 leading-relaxed mb-4">
                                        {currentFeature.description}
                                    </p>

                                    {/* Three Benefit Bullets */}
                                    <div className="space-y-2 sm:space-y-2.5">
                                        {currentFeature.benefits.map((benefit, idx) => (
                                            <div
                                                key={idx}
                                                className="flex items-center gap-2.5 text-xs sm:text-sm font-medium text-white/95"
                                            >
                                                <span className="flex h-4.5 w-4.5 items-center justify-center rounded-full bg-white/20 text-white shrink-0 shadow-sm">
                                                    <Check size={11} strokeWidth={3} />
                                                </span>
                                                <span>{benefit}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Full-Width White CTA Button */}
                                <div className="pt-2">
                                    {currentFeature.isImplemented && currentFeature.destination ? (
                                        <Link
                                            to={currentFeature.destination}
                                            style={{ backgroundColor: '#ffffff', color: '#4c1d95' }}
                                            className="featured-card-cta w-full inline-flex items-center justify-center gap-2 rounded-2xl font-extrabold px-6 py-3.5 text-sm cursor-pointer group shadow-lg transition-transform active:scale-98"
                                        >
                                            <span style={{ color: '#4c1d95' }} className="font-extrabold">
                                                {currentFeature.ctaLabel}
                                            </span>
                                            <ArrowRight
                                                size={16}
                                                style={{ color: '#4c1d95', stroke: '#4c1d95' }}
                                                className="group-hover:translate-x-1 transition-transform"
                                            />
                                        </Link>
                                    ) : (
                                        <button
                                            type="button"
                                            onClick={() => handlePlaceholderCta(currentFeature.title)}
                                            style={{ backgroundColor: '#ffffff', color: '#4c1d95' }}
                                            className="featured-card-cta w-full inline-flex items-center justify-center gap-2 rounded-2xl font-extrabold px-6 py-3.5 text-sm cursor-pointer group shadow-lg transition-transform active:scale-98"
                                        >
                                            <span style={{ color: '#4c1d95' }} className="font-extrabold">
                                                {currentFeature.ctaLabel}
                                            </span>
                                            <ArrowRight
                                                size={16}
                                                style={{ color: '#4c1d95', stroke: '#4c1d95' }}
                                                className="group-hover:translate-x-1 transition-transform"
                                            />
                                        </button>
                                    )}
                                </div>
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Progress Dots Indicator & Counter */}
                    <div className="flex items-center justify-between px-4 sm:px-6 mt-4">
                        <div className="flex items-center gap-1.5">
                            {FEATURES_LIST.map((_, idx) => (
                                <button
                                    key={idx}
                                    type="button"
                                    onClick={() => goToIndex(idx)}
                                    aria-label={`Go to feature ${idx + 1}`}
                                    className={`h-2 rounded-full transition-all duration-300 cursor-pointer ${
                                        idx === currentIndex
                                            ? 'w-7 bg-[#6D28D9] dark:bg-[#A78BFA]'
                                            : 'w-2 bg-purple-200 dark:bg-purple-800/60 hover:bg-purple-300'
                                    }`}
                                />
                            ))}
                        </div>

                        <span className="text-xs font-bold text-[#64748B] dark:text-[#C4B5FD]">
                            {currentIndex + 1} / {totalFeatures}
                        </span>
                    </div>
                </div>

                {/* 3. Horizontal Feature Selectors: Exactly 5 items in ONE row (horizontally scrollable on mobile) */}
                <div className="max-w-4xl mx-auto">
                    <div
                        ref={selectorsContainerRef}
                        className="flex md:grid md:grid-cols-5 gap-2.5 sm:gap-3 overflow-x-auto scrollbar-none py-2 px-1 snap-x"
                    >
                        {FEATURES_LIST.map((item, idx) => {
                            const ItemIcon = item.icon
                            const isActive = idx === currentIndex

                            return (
                                <button
                                    key={item.id}
                                    type="button"
                                    onClick={() => goToIndex(idx)}
                                    aria-label={`Select ${item.title}`}
                                    className={`min-w-[88px] sm:min-w-[110px] md:min-w-0 flex-1 flex flex-col items-center justify-between p-2.5 sm:p-3 rounded-2xl border transition-all duration-200 cursor-pointer select-none snap-start ${
                                        isActive
                                            ? 'border-2 border-[#8B5CF6] dark:border-[#A78BFA] bg-purple-50/90 dark:bg-[#2A1D52] shadow-md shadow-purple-500/20 scale-[1.03]'
                                            : 'border border-purple-200/80 dark:border-purple-800/40 bg-white dark:bg-[#191333] shadow-xs hover:border-[#8B5CF6] opacity-90 hover:opacity-100'
                                    }`}
                                >
                                    {/* Icon container */}
                                    <div
                                        className={`flex h-8 w-8 sm:h-9 sm:w-9 items-center justify-center rounded-xl mb-1.5 transition-colors ${
                                            isActive
                                                ? 'bg-[#8B5CF6] text-white shadow-sm shadow-purple-600/30'
                                                : 'bg-purple-100/80 dark:bg-purple-900/40 text-[#6D28D9] dark:text-[#C4B5FD]'
                                        }`}
                                    >
                                        <ItemIcon size={17} strokeWidth={2.2} />
                                    </div>

                                    {/* Number pill */}
                                    <span
                                        className={`px-2 py-0.5 rounded-md text-[10px] font-black tracking-wider mb-1 ${
                                            isActive
                                                ? 'bg-[#6D28D9] text-white'
                                                : 'bg-purple-100 dark:bg-purple-900/40 text-[#6D28D9] dark:text-[#C4B5FD]'
                                        }`}
                                    >
                                        {item.number}
                                    </span>

                                    {/* Selector title */}
                                    <span
                                        className={`block text-[10px] sm:text-[11px] font-bold leading-tight text-center line-clamp-2 mb-2 transition-colors ${
                                            isActive
                                                ? 'text-[#6D28D9] dark:text-[#C4B5FD]'
                                                : 'text-[#17172E] dark:text-[#F8FAFC]'
                                        }`}
                                    >
                                        {item.selectorTitle}
                                    </span>

                                    {/* Green Available badge on ALL FIVE selectors */}
                                    <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-100/90 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-500/25">
                                        <Check size={9} strokeWidth={3} />
                                        <span>Available</span>
                                    </span>
                                </button>
                            )
                        })}
                    </div>
                </div>

                {/* 4. Horizontal Bottom Trust Indicators Bar */}
                <div className="rounded-2xl border border-purple-200/80 dark:border-purple-800/40 bg-white/95 dark:bg-[#191333]/95 backdrop-blur-md py-4 px-6 sm:px-10 flex flex-wrap items-center justify-around gap-4 text-xs font-bold text-[#17172E] dark:text-[#F8FAFC] shadow-sm">
                    <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100 dark:bg-emerald-900/40 text-[#22C55E]">
                            <ShieldCheck size={17} />
                        </div>
                        <span>Local-First &amp; Private</span>
                    </div>

                    <div className="hidden md:block h-4 w-px bg-purple-200 dark:bg-purple-800/60" />

                    <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/40 text-[#8B5CF6]">
                            <Layers size={17} />
                        </div>
                        <span>Explainable Scoring Engine</span>
                    </div>

                    <div className="hidden md:block h-4 w-px bg-purple-200 dark:bg-purple-800/60" />

                    <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/40 text-[#6D28D9] dark:text-[#C4B5FD]">
                            <Zap size={17} />
                        </div>
                        <span>Zero External LLM APIs</span>
                    </div>
                </div>
            </div>

            {/* Informational Toast for Non-Implemented Features */}
            {toastMessage && (
                <div className="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 w-[90vw] max-w-md rounded-2xl border border-purple-300 dark:border-purple-600 bg-white/98 dark:bg-[#1C1536]/98 p-4 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-3">
                    <div className="flex items-start gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-100 dark:bg-purple-900/50 text-[#6D28D9] dark:text-[#C4B5FD] shrink-0">
                            <Info size={17} />
                        </div>
                        <div className="flex-1 text-left">
                            <h4 className="text-xs font-bold text-[#17172E] dark:text-[#F8FAFC]">
                                {toastMessage.title}
                            </h4>
                            <p className="text-[11px] text-[#64748B] dark:text-[#CBD5E1]/90 leading-relaxed mt-0.5">
                                {toastMessage.text}
                            </p>
                        </div>
                        <button
                            type="button"
                            onClick={() => setToastMessage(null)}
                            className="text-[#64748B] hover:text-[#17172E] dark:hover:text-white p-1"
                        >
                            <X size={15} />
                        </button>
                    </div>
                </div>
            )}
        </section>
    )
}
