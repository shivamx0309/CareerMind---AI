import { useState } from 'react'
import { Sparkles, ShieldCheck, Layers, Zap } from 'lucide-react'
import {
    FEATURES_DATA,
    INITIAL_FEATURED_ID,
    INITIAL_SMALL_CARD_IDS,
} from '../../data/featuresData'
import FeaturedCard from './FeaturedCard'
import SmallFeatureCard from './SmallFeatureCard'

export default function FeaturesSection() {
    // Current featured card on the left
    const [featuredId, setFeaturedId] = useState(INITIAL_FEATURED_ID)

    // Current 4 small cards in the 2x2 grid on the right
    const [smallCardIds, setSmallCardIds] = useState(INITIAL_SMALL_CARD_IDS)

    /**
     * Feature Swapping Handler:
     * 1. Clicked feature moves into the large left featured-card position.
     * 2. Currently featured card moves into the exact position previously occupied by clicked card.
     * 3. Remaining three cards stay in their original positions.
     */
    const handleSwap = (clickedId) => {
        const clickedIndex = smallCardIds.indexOf(clickedId)
        if (clickedIndex === -1) return

        const previousFeaturedId = featuredId

        // Set clicked feature as active featured
        setFeaturedId(clickedId)

        // Swap previously featured into the exact slot clicked
        setSmallCardIds((prev) => {
            const next = [...prev]
            next[clickedIndex] = previousFeaturedId
            return next
        })
    }

    const featuredFeature = FEATURES_DATA[featuredId] || FEATURES_DATA[INITIAL_FEATURED_ID]

    return (
        <section id="features" className="py-20 sm:py-24 border-t border-[var(--border)] relative overflow-hidden">
            {/* Ambient Background Aura */}
            <div className="pointer-events-none absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[450px] bg-gradient-to-tr from-[#6D28D9]/10 via-[#8B5CF6]/10 to-[#C4B5FD]/10 rounded-full blur-3xl -z-10" />

            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
                {/* 1. Header & Subtitle */}
                <div className="text-center space-y-3.5 max-w-2xl mx-auto">
                    <div className="inline-flex items-center gap-1.5 rounded-full border border-[#8B5CF6]/30 bg-[#8B5CF6]/10 dark:bg-[#8B5CF6]/20 px-4 py-1 text-xs font-bold text-[#6D28D9] dark:text-[#C4B5FD] shadow-sm">
                        <Sparkles size={13} className="text-[#8B5CF6]" />
                        <span>Platform Features</span>
                    </div>

                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-[#17172E] dark:text-[#F8FAFC]">
                        Powerful Tools for Your{' '}
                        <span className="purple-gradient-text">Career Growth</span>
                    </h2>

                    <p className="text-sm sm:text-base text-[#64748B] dark:text-[#C4B5FD]/90 leading-relaxed">
                        A complete set of AI-powered tools to analyze, plan and accelerate your career journey.
                    </p>
                </div>

                {/* 2. Asymmetric Bento Grid: Large Featured Card (Left) + 2x2 Small Grid (Right) */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
                    {/* Left: Large Featured Feature Card (Desktop ~42% width) */}
                    <div className="lg:col-span-5 h-full">
                        <FeaturedCard feature={featuredFeature} />
                    </div>

                    {/* Right: 2x2 Grid of 4 Smaller Feature Cards (Desktop ~58% width) */}
                    <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-5 h-full">
                        {smallCardIds.map((cardId) => {
                            const feature = FEATURES_DATA[cardId]
                            if (!feature) return null

                            return (
                                <SmallFeatureCard
                                    key={feature.id}
                                    feature={feature}
                                    onSwap={handleSwap}
                                />
                            )
                        })}
                    </div>
                </div>

                {/* 3. Horizontal Bottom Trust Indicators Bar */}
                <div className="rounded-2xl border border-purple-200/70 dark:border-purple-500/30 bg-white/85 dark:bg-[#191333]/85 backdrop-blur-md py-4 px-6 sm:px-10 flex flex-wrap items-center justify-around gap-4 text-xs font-bold text-[#17172E] dark:text-[#F8FAFC] shadow-sm">
                    <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#8B5CF6]/15 text-[#6D28D9] dark:text-[#C4B5FD]">
                            <ShieldCheck size={17} />
                        </div>
                        <span>Local-First &amp; Private</span>
                    </div>

                    <div className="hidden md:block h-4 w-px bg-purple-200 dark:bg-purple-800/60" />

                    <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#8B5CF6]/15 text-[#6D28D9] dark:text-[#C4B5FD]">
                            <Layers size={17} />
                        </div>
                        <span>Explainable Scoring Engine</span>
                    </div>

                    <div className="hidden md:block h-4 w-px bg-purple-200 dark:bg-purple-800/60" />

                    <div className="flex items-center gap-2.5">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#8B5CF6]/15 text-[#6D28D9] dark:text-[#C4B5FD]">
                            <Zap size={17} />
                        </div>
                        <span>Zero External LLM APIs</span>
                    </div>
                </div>
            </div>
        </section>
    )
}
