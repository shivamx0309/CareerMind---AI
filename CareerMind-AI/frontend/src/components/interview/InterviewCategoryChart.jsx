import { useMemo } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts'

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null
  const item = payload[0].payload

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 text-xs shadow-xl space-y-1">
      <div className="font-bold text-[var(--text-primary)]">{item.name}</div>
      <div className="text-[var(--text-secondary)]">
        Score: <span className="font-bold text-purple-600 dark:text-purple-400">{item.score}%</span>
      </div>
      <div className="text-[10px] text-[var(--text-muted)]">
        {item.attempted} of {item.total} questions assessed
      </div>
    </div>
  )
}

function getBarColor(score) {
  if (score >= 75) return '#10b981' // emerald
  if (score >= 50) return '#f59e0b' // amber
  return '#f43f5e' // rose
}

export default function InterviewCategoryChart({ categoryScores = {} }) {
  // Transform backend categoryScores map into chart data, omitting insufficient_data
  const chartData = useMemo(() => {
    if (!categoryScores || typeof categoryScores !== 'object') return []

    return Object.entries(categoryScores)
      .filter(([, data]) => data?.status !== 'insufficient_data' && typeof data?.average_score === 'number')
      .map(([key, data]) => {
        const formattedName = key
          .replace(/_/g, ' ')
          .replace(/\b\w/g, (c) => c.toUpperCase())

        return {
          categoryKey: key,
          name: formattedName,
          score: Math.round(data.average_score),
          attempted: data.attempted,
          total: data.total,
        }
      })
      .sort((a, b) => b.score - a.score)
  }, [categoryScores])

  if (chartData.length === 0) {
    return (
      <div className="py-8 text-center text-xs text-[var(--text-muted)] italic">
        Insufficient category data to render visual performance chart.
      </div>
    )
  }

  return (
    <div className="w-full h-64 md:h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 10, right: 25, left: 10, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} opacity={0.15} />
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
            unit="%"
          />
          <YAxis
            type="category"
            dataKey="name"
            width={120}
            tick={{ fontSize: 11, fill: 'var(--text-secondary)', fontWeight: 600 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="score" radius={[0, 6, 6, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
