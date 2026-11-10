import { useMemo } from 'react'
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    CartesianGrid,
} from 'recharts'
import { BarChart3 } from 'lucide-react'
import { getCategoryMeta } from '../../utils/skillCategoryConfig'

export default function SkillCategoryBreakdown({ categoryBreakdown = [] }) {
    // Transform API category breakdown for Recharts
    const chartData = useMemo(() => {
        if (!categoryBreakdown) return []
        return categoryBreakdown.map((item) => {
            const meta = getCategoryMeta(item.category)
            return {
                rawCategory: item.category,
                categoryName: meta.shortLabel || meta.label,
                fullName: meta.label,
                Matched: item.matched_count,
                Related: item.related_count,
                Missing: item.missing_count,
                total: item.total_skills,
                coverage: item.coverage_percentage,
            }
        })
    }, [categoryBreakdown])

    if (!categoryBreakdown || categoryBreakdown.length === 0) {
        return null
    }

    return (
        <div className="glass-card rounded-2xl p-5 sm:p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                        <BarChart3 size={18} className="text-[var(--accent)]" />
                        <h3 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                            Category-wise Competency Breakdown
                        </h3>
                    </div>
                    <p className="text-xs text-[var(--text-muted)]">
                        Domain-level skill distribution across benchmark expectations
                    </p>
                </div>
            </div>

            {/* Recharts Stacked Horizontal Bar Chart */}
            <div className="h-64 sm:h-72 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                        data={chartData}
                        layout="vertical"
                        margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                    >
                        <CartesianGrid
                            strokeDasharray="3 3"
                            horizontal={false}
                            stroke="rgba(167, 139, 250, 0.12)"
                        />
                        <XAxis
                            type="number"
                            allowDecimals={false}
                            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                            axisLine={{ stroke: 'var(--border)' }}
                            tickLine={false}
                        />
                        <YAxis
                            dataKey="categoryName"
                            type="category"
                            width={110}
                            tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontWeight: 500 }}
                            axisLine={{ stroke: 'var(--border)' }}
                            tickLine={false}
                        />
                        <Tooltip
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    const data = payload[0].payload
                                    return (
                                        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 shadow-lg space-y-1 text-xs">
                                            <div className="font-bold text-[var(--text-primary)] pb-1 border-b border-[var(--border)]">
                                                {data.fullName}
                                            </div>
                                            <div className="flex items-center justify-between gap-4 text-emerald-500 font-medium">
                                                <span>Matched (1.0x):</span>
                                                <strong>{data.Matched}</strong>
                                            </div>
                                            <div className="flex items-center justify-between gap-4 text-amber-500 font-medium">
                                                <span>Related (0.6x):</span>
                                                <strong>{data.Related}</strong>
                                            </div>
                                            <div className="flex items-center justify-between gap-4 text-rose-500 font-medium">
                                                <span>Missing:</span>
                                                <strong>{data.Missing}</strong>
                                            </div>
                                            <div className="pt-1 border-t border-[var(--border)] flex items-center justify-between text-[var(--text-primary)] font-bold">
                                                <span>Coverage:</span>
                                                <span>{data.coverage}%</span>
                                            </div>
                                        </div>
                                    )
                                }
                                return null
                            }}
                        />
                        <Legend
                            wrapperStyle={{ paddingTop: 10, fontSize: 12 }}
                            formatter={(value) => (
                                <span className="text-[var(--text-secondary)] font-medium">
                                    {value}
                                </span>
                            )}
                        />
                        <Bar
                            dataKey="Matched"
                            stackId="a"
                            fill="#10b981"
                            radius={[0, 0, 0, 0]}
                        />
                        <Bar
                            dataKey="Related"
                            stackId="a"
                            fill="#f59e0b"
                            radius={[0, 0, 0, 0]}
                        />
                        <Bar
                            dataKey="Missing"
                            stackId="a"
                            fill="#f43f5e"
                            radius={[0, 4, 4, 0]}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* Category Metric Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
                {categoryBreakdown.map((catItem) => {
                    const meta = getCategoryMeta(catItem.category)
                    const Icon = meta.icon

                    return (
                        <div
                            key={catItem.category}
                            className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3.5 space-y-2.5 hover:border-[var(--accent)]/30 transition-colors"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Icon size={16} style={{ color: meta.color }} />
                                    <h4 className="text-xs font-bold text-[var(--text-primary)]">
                                        {meta.label}
                                    </h4>
                                </div>
                                <span className="text-xs font-black text-[var(--text-primary)]">
                                    {catItem.coverage_percentage}%
                                </span>
                            </div>

                            {/* Mini Progress */}
                            <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--surface-hover)]">
                                <div
                                    className="h-full rounded-full transition-all duration-500"
                                    style={{
                                        width: `${Math.min(Math.max(catItem.coverage_percentage, 0), 100)}%`,
                                        backgroundColor: meta.color,
                                    }}
                                />
                            </div>

                            {/* Quick Metrics */}
                            <div className="flex items-center justify-between text-[11px] text-[var(--text-muted)] pt-0.5">
                                <span className="text-emerald-500 font-medium">
                                    {catItem.matched_count} matched
                                </span>
                                {catItem.related_count > 0 && (
                                    <span className="text-amber-500 font-medium">
                                        {catItem.related_count} related
                                    </span>
                                )}
                                <span className="text-rose-400 font-medium">
                                    {catItem.missing_count} missing
                                </span>
                                <span className="font-semibold text-[var(--text-secondary)]">
                                    Total: {catItem.total_skills}
                                </span>
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
