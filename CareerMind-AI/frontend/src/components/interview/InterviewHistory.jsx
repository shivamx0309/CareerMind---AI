import { useState } from 'react'
import {
  History,
  Play,
  FileText,
  Trash2,
  Calendar,
  Sparkles,
} from 'lucide-react'

export default function InterviewHistory({
  sessions = [],
  onSelectSession,
  onDeleteSession,
  onStartNew,
  isLoading = false,
}) {
  const [statusFilter, setStatusFilter] = useState('all')

  const filtered = sessions.filter((s) => {
    if (statusFilter === 'all') return true
    return s.status === statusFilter
  })

  const getScoreBadgeClass = (score) => {
    if (typeof score !== 'number') return 'bg-[var(--surface-hover)] text-[var(--text-muted)] border-[var(--border)]'
    if (score >= 75) return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30'
    if (score >= 50) return 'bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30'
    return 'bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30'
  }

  return (
    <div className="space-y-4">
      {/* Header and Filter Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          <History size={18} className="text-[var(--accent)]" />
          <h2 className="text-lg font-bold text-[var(--text-primary)]">
            Interview History
          </h2>
          <span className="rounded-full bg-[var(--surface-hover)] px-2.5 py-0.5 text-xs font-bold text-[var(--text-secondary)] border border-[var(--border)]">
            {sessions.length}
          </span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 self-start sm:self-auto bg-[var(--surface-solid)] p-1 rounded-xl border border-[var(--border)] text-xs font-semibold">
          <button
            type="button"
            onClick={() => setStatusFilter('all')}
            className={`px-3 py-1 rounded-lg transition-all ${
              statusFilter === 'all'
                ? 'bg-purple-600 text-white shadow-xs'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            All ({sessions.length})
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter('completed')}
            className={`px-3 py-1 rounded-lg transition-all ${
              statusFilter === 'completed'
                ? 'bg-purple-600 text-white shadow-xs'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            Completed ({sessions.filter((s) => s.status === 'completed').length})
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter('in_progress')}
            className={`px-3 py-1 rounded-lg transition-all ${
              statusFilter === 'in_progress'
                ? 'bg-purple-600 text-white shadow-xs'
                : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            In Progress ({sessions.filter((s) => s.status === 'in_progress').length})
          </button>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="py-12 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 rounded-full border-2 border-[var(--accent)] border-t-transparent animate-spin" />
          <p className="text-xs text-[var(--text-muted)]">Loading past interview sessions...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-3xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-8 text-center space-y-3">
          <History size={32} className="mx-auto text-[var(--text-muted)]" />
          <div className="text-sm font-bold text-[var(--text-primary)]">
            {statusFilter === 'all'
              ? 'No mock interview sessions yet'
              : `No ${statusFilter.replace('_', ' ')} interviews found`}
          </div>
          <p className="text-xs text-[var(--text-secondary)] max-w-sm mx-auto">
            {statusFilter === 'all'
              ? 'Start your first personalized mock interview to practice answering technical and behavioral questions.'
              : 'Try changing the filter or launch a new session.'}
          </p>
          {statusFilter === 'all' && (
            <button
              type="button"
              onClick={onStartNew}
              className="mt-2 inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:from-purple-500 hover:to-indigo-500"
            >
              <Sparkles size={14} />
              <span>Start First Interview</span>
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {filtered.map((s) => {
            const isCompleted = s.status === 'completed'
            const dateStr = s.started_at
              ? new Date(s.started_at).toLocaleDateString(undefined, {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })
              : 'Recent'

            return (
              <div
                key={s.id}
                className="group rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 hover:border-purple-500/40 hover:bg-[var(--surface-hover)] transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xs"
              >
                {/* Left meta */}
                <div className="space-y-1.5 max-w-md">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-bold text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors">
                      {s.role_title}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold border ${getScoreBadgeClass(
                        s.overall_score
                      )}`}
                    >
                      {typeof s.overall_score === 'number'
                        ? `${Math.round(s.overall_score)}% Score`
                        : isCompleted
                        ? 'Completed'
                        : 'In Progress'}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)] flex-wrap">
                    <span className="capitalize">{s.interview_type}</span>
                    <span>•</span>
                    <span className="capitalize">{s.difficulty}</span>
                    <span>•</span>
                    <span>
                      {s.questions_answered} of {s.total_questions} answered
                    </span>
                    <span>•</span>
                    <span className="text-[var(--text-muted)] flex items-center gap-1">
                      <Calendar size={11} /> {dateStr}
                    </span>
                  </div>
                </div>

                {/* Right Actions */}
                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <button
                    type="button"
                    onClick={() => onSelectSession(s.id)}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:border-purple-500/40 hover:bg-purple-500/10 transition-all"
                  >
                    {isCompleted ? (
                      <>
                        <FileText size={13} className="text-purple-600 dark:text-purple-400" />
                        <span>View Report</span>
                      </>
                    ) : (
                      <>
                        <Play size={13} className="text-emerald-600 dark:text-emerald-400" />
                        <span>Resume</span>
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => onDeleteSession(s.id)}
                    className="rounded-xl border border-transparent p-2 text-[var(--text-muted)] hover:text-rose-600 hover:border-rose-500/30 hover:bg-rose-500/10 transition-all"
                    title="Delete interview session"
                    aria-label={`Delete interview session for ${s.role_title}`}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
