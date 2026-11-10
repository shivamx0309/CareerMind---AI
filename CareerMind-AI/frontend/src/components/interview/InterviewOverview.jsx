import { Sparkles, Trophy, CheckCircle2, History, TrendingUp, Info } from 'lucide-react'
import MindyMascot from '../common/MindyMascot'

export default function InterviewOverview({
  sessions = [],
  onStartNew,
  onViewHistory,
}) {
  // Aggregate real stats from completed sessions only
  const completedSessions = sessions.filter(
    (s) => s.status === 'completed' && typeof s.overall_score === 'number'
  )
  const totalCompleted = completedSessions.length

  const avgScore =
    totalCompleted > 0
      ? Math.round(
          completedSessions.reduce((acc, s) => acc + s.overall_score, 0) /
            totalCompleted
        )
      : null

  const bestScore =
    totalCompleted > 0
      ? Math.round(
          Math.max(...completedSessions.map((s) => s.overall_score))
        )
      : null

  const latestSession = sessions.length > 0 ? sessions[0] : null
  const latestDate = latestSession?.started_at
    ? new Date(latestSession.started_at).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      })
    : null

  return (
    <div className="space-y-6">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-gradient-to-br from-[var(--surface-solid)] via-[var(--surface)] to-[var(--surface-hover)] p-6 md:p-8 shadow-sm">
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="max-w-2xl text-center md:text-left space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-hover)] px-3 py-1 text-xs font-semibold text-[var(--accent)]">
              <Sparkles size={13} />
              <span>Deterministic Rubric Assessment</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-[var(--text-primary)] tracking-tight">
              AI Mock Interview Simulator
            </h1>
            <p className="text-sm md:text-base text-[var(--text-secondary)] leading-relaxed">
              Test your engineering readiness with realistic questions tailored to
              your target role, format, and personal skill gaps. Receive instant,
              explainable rubric scores across concept coverage, relevance, and structure.
            </p>
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 pt-2">
              <button
                type="button"
                onClick={onStartNew}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-5 py-2.5 text-sm font-bold text-white shadow-md hover:from-purple-500 hover:to-indigo-500 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <Sparkles size={16} />
                <span>Start New Interview</span>
              </button>
              {sessions.length > 0 && (
                <button
                  type="button"
                  onClick={onViewHistory}
                  className="inline-flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
                >
                  <History size={16} />
                  <span>Session History ({sessions.length})</span>
                </button>
              )}
            </div>
          </div>

          <div className="shrink-0 flex items-center justify-center">
            <MindyMascot
              expression="chatbot"
              size="md"
              alt="Mindy Interview Guide"
              className="drop-shadow-xl"
            />
          </div>
        </div>

        {/* Ambient Gradient Glow */}
        <div className="pointer-events-none absolute -bottom-12 -right-12 h-64 w-64 rounded-full bg-purple-500/10 blur-3xl" />
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Completed */}
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--text-secondary)]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Completed
            </span>
            <CheckCircle2 size={18} className="text-emerald-500" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-[var(--text-primary)]">
              {totalCompleted}
            </div>
            <div className="text-xs text-[var(--text-muted)] mt-0.5">
              of {sessions.length} sessions
            </div>
          </div>
        </div>

        {/* Metric 2: Average Score */}
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--text-secondary)]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Average Score
            </span>
            <TrendingUp size={18} className="text-indigo-500" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-[var(--text-primary)]">
              {avgScore !== null ? `${avgScore}%` : '—'}
            </div>
            <div className="text-xs text-[var(--text-muted)] mt-0.5">
              {totalCompleted > 0 ? 'Across completed' : 'No scored sessions'}
            </div>
          </div>
        </div>

        {/* Metric 3: Best Score */}
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--text-secondary)]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Best Score
            </span>
            <Trophy size={18} className="text-amber-500" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-[var(--text-primary)]">
              {bestScore !== null ? `${bestScore}%` : '—'}
            </div>
            <div className="text-xs text-[var(--text-muted)] mt-0.5">
              Highest performance
            </div>
          </div>
        </div>

        {/* Metric 4: Latest Activity */}
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-[var(--text-secondary)]">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Recent Activity
            </span>
            <History size={18} className="text-purple-500" />
          </div>
          <div className="mt-3">
            <div className="text-2xl font-black text-[var(--text-primary)] truncate">
              {latestDate || '—'}
            </div>
            <div className="text-xs text-[var(--text-muted)] mt-0.5 truncate">
              {latestSession?.role_title || 'No recent activity'}
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Transparency Disclaimer */}
      <div className="flex items-start gap-3 rounded-2xl border border-indigo-500/20 bg-indigo-500/5 dark:bg-indigo-500/10 p-4 text-xs text-[var(--text-secondary)] leading-relaxed">
        <Info size={16} className="text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-[var(--text-primary)]">Assessment Disclaimer: </span>
          Evaluation is based on a deterministic rubric and concept matching. It provides
          structured practice guidance, not human or LLM-level semantic judgment, and does
          not guarantee interview success.
        </div>
      </div>
    </div>
  )
}

