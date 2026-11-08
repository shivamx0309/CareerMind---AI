import { motion } from 'framer-motion'
import { Sparkles, Clock3 } from 'lucide-react'

export default function SmallFeatureCard({ feature, onSwap }) {
    const Icon = feature.icon
    const isAvailable = feature.status === 'Available'

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onSwap(feature.id)
        }
    }

    return (
        <motion.div
            key={feature.id}
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            role="button"
            tabIndex={0}
            onClick={() => onSwap(feature.id)}
            onKeyDown={handleKeyDown}
            aria-label={`Select ${feature.title} to feature`}
            className="group relative flex flex-col justify-between rounded-3xl p-6 sm:p-7 bg-white dark:bg-[#191333] border border-purple-200/70 dark:border-purple-500/30 shadow-md hover:shadow-xl hover:border-[#8B5CF6] hover:-translate-y-1 active:translate-y-0 transition-all duration-300 cursor-pointer select-none"
        >
            <div>
                {/* Top Row: Icon Container + Number & Availability Badges */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2.5">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#8B5CF6]/10 dark:bg-[#8B5CF6]/20 text-[#6D28D9] dark:text-[#C4B5FD] border border-[#8B5CF6]/20 group-hover:scale-105 group-hover:bg-[#8B5CF6]/20 transition-all duration-200 shadow-sm">
                            <Icon size={22} strokeWidth={2.2} />
                        </div>
                        <span className="inline-flex items-center justify-center px-2 py-0.5 rounded-lg bg-[#8B5CF6]/10 dark:bg-[#8B5CF6]/25 text-[#6D28D9] dark:text-[#C4B5FD] text-[11px] font-black border border-[#8B5CF6]/25">
                            #{feature.number}
                        </span>
                    </div>

                    <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold border ${
                            isAvailable
                                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                                : 'border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400'
                        }`}
                    >
                        {isAvailable ? <Sparkles size={11} /> : <Clock3 size={11} />}
                        <span>{feature.status}</span>
                    </span>
                </div>

                {/* Title & Description with Feature Number */}
                <h4 className="text-base sm:text-lg font-bold text-[#17172E] dark:text-[#F8FAFC] group-hover:text-[#6D28D9] dark:group-hover:text-[#C4B5FD] transition-colors mb-2">
                    <span className="text-[#8B5CF6] dark:text-[#C4B5FD] mr-1.5 font-black text-sm">
                        {feature.number}.
                    </span>
                    {feature.title}
                </h4>
                <p className="text-xs text-[#64748B] dark:text-[#CBD5E1]/80 leading-relaxed line-clamp-2">
                    {feature.description}
                </p>
            </div>

            {/* Click to Swap Hint on Hover */}
            <div className="mt-4 pt-3 border-t border-purple-100 dark:border-purple-900/30 flex items-center justify-between text-[11px] font-semibold text-[#8B5CF6] opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <span>Click to explore feature</span>
                <span>&rarr;</span>
            </div>
        </motion.div>
    )
}

