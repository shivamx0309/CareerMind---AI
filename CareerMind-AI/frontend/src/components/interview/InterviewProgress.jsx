export default function InterviewProgress({
  currentQuestionIndex = 0,
  totalQuestions = 5,
  questions = [],
  roleTitle = 'Engineering Interview',
  interviewType = 'technical',
  difficulty = 'intermediate',
}) {
  const answeredCount = questions.filter((q) => q.is_answered).length
  const progressPercent =
    totalQuestions > 0 ? Math.round((answeredCount / totalQuestions) * 100) : 0

  return (
    <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 md:p-5 space-y-3 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-extrabold text-[var(--text-primary)]">
              {roleTitle}
            </span>
            <span className="rounded-full border border-purple-500/30 bg-purple-500/10 px-2.5 py-0.5 text-[10px] font-bold text-purple-700 dark:text-purple-300 capitalize">
              {interviewType}
            </span>
            <span className="rounded-full border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-0.5 text-[10px] font-bold text-indigo-700 dark:text-indigo-300 capitalize">
              {difficulty}
            </span>
          </div>
          <div className="text-xs text-[var(--text-secondary)]">
            Question {Math.min(currentQuestionIndex + 1, totalQuestions)} of {totalQuestions}
          </div>
        </div>

        <div className="flex items-center gap-3 self-end sm:self-auto">
          <div className="text-right">
            <div className="text-xs font-bold text-[var(--text-primary)]">
              {progressPercent}% Complete
            </div>
            <div className="text-[10px] text-[var(--text-muted)]">
              {answeredCount} of {totalQuestions} answered
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--surface-hover)] border border-[var(--border)]">
        <div
          className="h-full bg-gradient-to-r from-purple-600 via-indigo-600 to-emerald-500 transition-all duration-500 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Question Stepper Dots */}
      <div className="flex items-center gap-1.5 overflow-x-auto py-1 scrollbar-none">
        {questions.map((q, idx) => {
          const isCurrent = idx === currentQuestionIndex
          const isAnswered = q.is_answered

          return (
            <div
              key={q.id || idx}
              title={`Question ${idx + 1}: ${isAnswered ? 'Answered' : isCurrent ? 'Active' : 'Upcoming'}`}
              className={`h-2 rounded-full transition-all flex-1 min-w-[14px] ${
                isAnswered
                  ? 'bg-emerald-500'
                  : isCurrent
                  ? 'bg-purple-600 ring-2 ring-purple-500/30 animate-pulse'
                  : 'bg-[var(--surface-hover)] border border-[var(--border)]'
              }`}
            />
          )
        })}
      </div>
    </div>
  )
}
