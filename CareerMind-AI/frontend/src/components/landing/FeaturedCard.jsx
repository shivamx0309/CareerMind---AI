import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Check, ArrowRight, Sparkles, Clock3 } from 'lucide-react'

export default function FeaturedCard({ feature }) {
    const Icon = feature.icon
    const isAvailable = feature.status === 'Available'

    return (
        <motion.div
            key={feature.id}
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            className="relative h-full flex flex-col justify-between rounded-3xl p-7 sm:p-9 bg-gradient-to-br from-[#6D28D9] via-[#7C3AED] to-[#8B5CF6] text-white shadow-2xl shadow-purple-900/30 border border-purple-400/30 overflow-hidden"
        >
            {/* Ambient Background Glow Effect */}
            <div className="pointer-events-none absolute -top-16 -right-16 w-48 h-48 rounded-full bg-white/10 blur-2xl" />

            <div>
                {/* Top Row: Icon Container, Number Badge & Status Pill */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 border border-white/25 text-white shadow-inner backdrop-blur-md">
                            <Icon size={28} strokeWidth={2.2} />
                        </div>
                        <span className="inline-flex items-center justify-center px-2.5 py-1 rounded-xl bg-white/20 border border-white/30 text-white text-xs font-black tracking-wider">
                            #{feature.number}
                        </span>
                    </div>

                    <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[11px] font-bold backdrop-blur-md ${
                            isAvailable
                                ? 'bg-emerald-500/20 text-emerald-200 border border-emerald-400/40'
                                : 'bg-amber-400/20 text-amber-200 border border-amber-300/40'
                        }`}
                    >
                        {isAvailable ? <Sparkles size={12} /> : <Clock3 size={12} />}
                        <span>{feature.status}</span>
                    </span>
                </div>

                {/* Number Subtitle & Main Title */}
                <div className="mb-3">
                    <span className="text-[11px] font-black uppercase tracking-widest text-purple-200 block mb-1">
                        Feature {feature.number} of 05
                    </span>
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                        {feature.title}
                    </h3>
                </div>

                <p className="text-sm text-purple-100/90 leading-relaxed mb-8">
                    {feature.description}
                </p>

                {/* Three Key Benefits */}
                <div className="space-y-3.5 mb-8">
                    {feature.benefits.map((benefit, idx) => (
                        <div key={idx} className="flex items-center gap-3 text-xs sm:text-sm font-medium text-white/95">
                            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white/20 text-white shrink-0 shadow-sm">
                                <Check size={12} strokeWidth={3} />
                            </span>
                            <span>{benefit}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Bottom Action Button with Guaranteed Contrast in Light & Dark Themes */}
            <div className="pt-2">
                {isAvailable && feature.destination ? (
                    <Link
                        to={feature.destination}
                        className="featured-card-cta w-full inline-flex items-center justify-center gap-2 rounded-2xl font-extrabold px-6 py-3.5 text-sm cursor-pointer group"
                    >
                        <span>{feature.ctaLabel}</span>
                        <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                    </Link>
                ) : (
                    <div className="w-full flex items-center justify-center gap-2 rounded-2xl bg-white/20 border border-white/30 text-white font-bold px-6 py-3.5 text-xs sm:text-sm backdrop-blur-md">
                        <Clock3 size={15} />
                        <span>{feature.ctaLabel}</span>
                    </div>
                )}
            </div>
        </motion.div>
    )
}

