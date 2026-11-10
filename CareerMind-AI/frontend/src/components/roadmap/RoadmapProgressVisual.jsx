import { useMemo } from 'react'
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip,
} from 'recharts'
import { Flame, Zap, Sparkles, Award } from 'lucide-react'

export default function RoadmapProgressVisual({ skills = [], progressPct = 0 }) {
    const { chartData, highHours, medHours, lowHours } = useMemo(() => {
        let h = 0
        let m = 0
        let l = 0

        skills.forEach((sk) => {
            if (sk.priority === 'high') h += sk.estimated_hours || 0
            else if (sk.priority === 'medium') m += sk.estimated_hours || 0
            else if (sk.priority === 'low') l += sk.estimated_hours || 0
        })

        const data = [
            { name: 'High Priority (Core)', value: Math.round(h * 10) / 10, color: '#f43f5e' },
            { name: 'Medium Priority (Bridge)', value: Math.round(m * 10) / 10, color: '#f59e0b' },
            { name: 'Low Priority (Bonus)', value: Math.round(l * 10) / 10, color: '#0ea5e9' },
        ].filter((d) => d.value > 0)

        return {
            chartData: data,
            highHours: Math.round(h * 10) / 10,
            medHours: Math.round(m * 10) / 10,
            lowHours: Math.round(l * 10) / 10,
        }
    }, [skills])

    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-card)] p-5 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--border)]">
                <div>
                    <h4 className="text-sm font-bold text-[var(--text-primary)]">
                        Curriculum Effort Distribution
                    </h4>
                    <p className="text-xs text-[var(--text-secondary)]">
                        Allocation of estimated study hours across priority tiers
                    </p>
                </div>
                <span className="rounded-full bg-[var(--accent-soft)] px-2.5 py-0.5 text-xs font-bold text-[var(--accent)]">
                    {Math.round(progressPct)}% Complete
                </span>
            </div>

            <div className="mt-4 flex flex-col md:flex-row items-center gap-6">
                {/* Donut Chart */}
                <div className="h-44 w-44 shrink-0 relative flex items-center justify-center">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={50}
                                outerRadius={70}
                                paddingAngle={3}
                                dataKey="value"
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value) => [`${value} hrs`, 'Estimated']}
                                contentStyle={{
                                    backgroundColor: 'var(--surface-card)',
                                    borderColor: 'var(--border)',
                                    borderRadius: '0.75rem',
                                    fontSize: '11px',
                                    color: 'var(--text-primary)',
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                        <Award size={18} className="text-[var(--accent)] mb-0.5" />
                        <span className="text-xs font-bold text-[var(--text-primary)]">
                            {Math.round(progressPct)}%
                        </span>
                    </div>
                </div>

                {/* Legend & Details */}
                <div className="flex-1 grid grid-cols-1 sm:grid-cols-3 gap-3 w-full">
                    {/* High */}
                    <div className="rounded-xl border border-rose-500/20 bg-rose-500/[0.04] p-3">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-rose-600 dark:text-rose-400">
                            <Flame size={14} />
                            High Priority
                        </div>
                        <div className="mt-1.5 text-base font-black text-[var(--text-primary)]">
                            {highHours}h
                        </div>
                        <div className="mt-0.5 text-[10px] text-[var(--text-secondary)]">
                            Mandatory core gaps
                        </div>
                    </div>

                    {/* Medium */}
                    <div className="rounded-xl border border-amber-500/20 bg-amber-500/[0.04] p-3">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-amber-600 dark:text-amber-400">
                            <Zap size={14} />
                            Medium Priority
                        </div>
                        <div className="mt-1.5 text-base font-black text-[var(--text-primary)]">
                            {medHours}h
                        </div>
                        <div className="mt-0.5 text-[10px] text-[var(--text-secondary)]">
                            Related bridge skills
                        </div>
                    </div>

                    {/* Low */}
                    <div className="rounded-xl border border-sky-500/20 bg-sky-500/[0.04] p-3">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-sky-600 dark:text-sky-400">
                            <Sparkles size={14} />
                            Low Priority
                        </div>
                        <div className="mt-1.5 text-base font-black text-[var(--text-primary)]">
                            {lowHours}h
                        </div>
                        <div className="mt-0.5 text-[10px] text-[var(--text-secondary)]">
                            Bonus competencies
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

