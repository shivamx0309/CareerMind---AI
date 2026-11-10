import { useState } from 'react'
import {
  Award,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  Sparkles,
  BarChart2,
  Layers,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Info,
  Calendar,
} from 'lucide-react'
import InterviewCategoryChart from './InterviewCategoryChart'

export default function InterviewReport({
  report,
  session,
  onStartNew,
  onBackToOverview,
}) {
  const [showQuestionReview, setShowQuestionReview] = useState(false)

  if (!report) return null

  const getScoreColor = (score) => {
    if (score >= 75) return 'text-emerald-600 dark:text-emerald-400'
    if (score >= 50) return 'text-amber-600 dark:text-amber-400'
    return 'text-rose-600 dark:text-rose-400'
  }

  const getScoreBg = (score) => {
    if (score >= 75) return 'from-emerald-600/20 to-teal-600/10 border-emerald-500/30'
    if (score >= 50) return 'from-amber-600/20 to-orange-600/10 border-amber-500/30'
    return 'from-rose-600/20 to-pink-600/10 border-rose-500/30'
  }

  const dateStr = report.created_at
    ? new Date(report.created_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'Recently'

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* 1. Header Trophy Card */}
      <div
        className={`relative overflow-hidden rounded-3xl border bg-gradient-to-br ${getScoreBg(
          report.overall_score
        )} p-6 md:p-8 shadow-sm`}
      >
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-3 text-center md:text-left">
            <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-1 text-xs font-bold text-[var(--accent)]">
              <Award size={14} />
              <span>Official Interview Assessment Report</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-[var(--text-primary)]">
              {session?.role_title || 'Engineering Mock Interview'}
            </h2>
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 text-xs text-[var(--text-secondary)] font-medium">
              <span className="capitalize">{session?.interview_type || 'Technical'} Format</span>
              <span>•</span>
              <span className="capitalize">{session?.difficulty || 'Intermediate'} Tier</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar size={12} /> {dateStr}
              </span>
            </div>
          </div>

          {/* Overall Score Dial */}
          <div className="flex flex-col items-center justify-center rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-6 shadow-md min-w-[160px] text-center">
            <div className={`text-4xl md:text-5xl font-black ${getScoreColor(report.overall_score)}`}>
              {Math.round(report.overall_score)}%
            </div>
            <span className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider mt-1">
              Overall Score
            </span>
            <span className="text-[10px] text-[var(--text-muted)] mt-0.5">
              Attempted {report.questions_attempted} of {report.total_questions}
            </span>
          </div>
        </div>

        {/* Ambient background decoration */}
        <div className="pointer-events-none absolute -bottom-10 -right-10 h-48 w-48 rounded-full bg-purple-500/10 blur-2xl" />
      </div>

      {/* 2. Key Stats Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4">
          <div className="text-xs text-[var(--text-muted)] font-semibold uppercase tracking-wider">
            Attempted
          </div>
          <div className="text-2xl font-bold text-[var(--text-primary)] mt-1">
            {report.questions_attempted} / {report.total_questions}
          </div>
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4">
          <div className="text-xs text-[var(--text-muted)] font-semibold uppercase tracking-wider">
            Average Answer Score
          </div>
          <div className="text-2xl font-bold text-[var(--text-primary)] mt-1">
            {Math.round(report.average_answer_score)}%
          </div>
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4">
          <div className="text-xs text-[var(--text-muted)] font-semibold uppercase tracking-wider">
            Strong Domains
          </div>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
            {report.strong_areas?.length || 0}
          </div>
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4">
          <div className="text-xs text-[var(--text-muted)] font-semibold uppercase tracking-wider">
            Focus Areas
          </div>
          <div className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">
            {report.weak_areas?.length || 0}
          </div>
        </div>
      </div>

      {/* 3. Performance Summary Narrative */}
      <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 md:p-6 space-y-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
          Executive Summary
        </h3>
        <p className="text-xs md:text-sm text-[var(--text-primary)] leading-relaxed">
          {report.performance_summary}
        </p>
      </div>

      {/* 4. Category Breakdown Visual Chart */}
      <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 md:p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <h3 className="text-sm font-bold text-[var(--text-primary)] flex items-center gap-2">
              <BarChart2 size={16} className="text-[var(--accent)]" />
              <span>Category Assessment Breakdown</span>
            </h3>
            <p className="text-xs text-[var(--text-muted)]">
              Evaluated across technical topics covered in this interview
            </p>
          </div>
        </div>

        <InterviewCategoryChart categoryScores={report.category_scores} />
      </div>

      {/* 5. Strong Areas & Weak Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strong Areas */}
        <div className="rounded-3xl border border-emerald-500/20 bg-emerald-500/5 p-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
            <CheckCircle2 size={15} />
            <span>Strong Performance Areas</span>
          </h3>
          {report.strong_areas?.length > 0 ? (
            <ul className="space-y-2 text-xs text-[var(--text-primary)]">
              {report.strong_areas.map((area, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-emerald-500 font-bold">•</span>
                  <span className="font-medium">{area}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-[var(--text-muted)] italic">
              Continue practicing to establish consistent mastery in tested categories.
            </p>
          )}
        </div>

        {/* Weak Areas */}
        <div className="rounded-3xl border border-rose-500/20 bg-rose-500/5 p-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-rose-700 dark:text-rose-400 flex items-center gap-2">
            <AlertTriangle size={15} />
            <span>Growth & Revision Opportunities</span>
          </h3>
          {report.weak_areas?.length > 0 ? (
            <ul className="space-y-2 text-xs text-[var(--text-primary)]">
              {report.weak_areas.map((area, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">•</span>
                  <span className="font-medium">{area}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
              No severe knowledge deficits identified in this session.
            </p>
          )}
        </div>
      </div>

      {/* 6. Frequently Missed Concepts & Recommended Topics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Frequently Missed Concepts */}
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] flex items-center gap-2">
            <AlertTriangle size={14} className="text-amber-500" />
            <span>Frequently Missed Concepts</span>
          </h3>
          {report.frequently_missed_concepts?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {report.frequently_missed_concepts.map((concept) => (
                <span
                  key={concept}
                  className="rounded-xl border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-800 dark:text-amber-300"
                >
                  {concept}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
              Zero recurring concept omissions detected.
            </p>
          )}
        </div>

        {/* Recommended Revision Topics */}
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] flex items-center gap-2">
            <BookOpen size={14} className="text-[var(--accent)]" />
            <span>Recommended Revision Topics</span>
          </h3>
          {report.recommended_topics?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {report.recommended_topics.map((topic) => (
                <span
                  key={topic}
                  className="rounded-xl border border-purple-500/30 bg-purple-500/10 px-2.5 py-1 text-xs font-semibold text-purple-700 dark:text-purple-300"
                >
                  {topic}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[var(--text-muted)] italic">
              All tested categories scored above standard benchmark thresholds.
            </p>
          )}
        </div>
      </div>

      {/* 7. Actionable Improvement Feedback */}
      {report.actionable_feedback?.length > 0 && (
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 md:p-6 space-y-3 shadow-xs">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] flex items-center gap-2">
            <Sparkles size={14} className="text-[var(--accent)]" />
            <span>Key Takeaways for Future Interviews</span>
          </h3>
          <ul className="space-y-2 text-xs md:text-sm text-[var(--text-primary)] leading-relaxed">
            {report.actionable_feedback.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5">
                <span className="text-[var(--accent)] font-bold shrink-0 mt-0.5">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 8. Collapsible Question-by-Question Review */}
      {session?.questions && session.questions.length > 0 && (
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] overflow-hidden shadow-xs">
          <button
            type="button"
            onClick={() => setShowQuestionReview(!showQuestionReview)}
            className="w-full flex items-center justify-between p-5 md:p-6 text-left hover:bg-[var(--surface-hover)] transition-all"
          >
            <div className="space-y-0.5">
              <span className="text-sm font-bold text-[var(--text-primary)] flex items-center gap-2">
                <Layers size={16} className="text-[var(--accent)]" />
                <span>Question-by-Question Review ({session.questions.length})</span>
              </span>
              <p className="text-xs text-[var(--text-muted)]">
                Inspect your submitted responses, rubric scores, and model answer points
              </p>
            </div>
            {showQuestionReview ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>

          {showQuestionReview && (
            <div className="p-5 md:p-6 pt-0 border-t border-[var(--border)] space-y-4">
              {session.questions.map((q, idx) => {
                const evalData = q.answer?.evaluation
                const score = evalData?.overall_score

                return (
                  <div
                    key={q.id || idx}
                    className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 space-y-3"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">
                          Question {q.sequence_order || idx + 1} • {q.category?.replace(/_/g, ' ')}
                        </span>
                        <h4 className="text-xs md:text-sm font-bold text-[var(--text-primary)] mt-0.5">
                          {q.question_text}
                        </h4>
                      </div>

                      {typeof score === 'number' && (
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-black shrink-0 ${
                            score >= 75
                              ? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                              : score >= 50
                              ? 'bg-amber-500/15 text-amber-700 dark:text-amber-300'
                              : 'bg-rose-500/15 text-rose-700 dark:text-rose-300'
                          }`}
                        >
                          {Math.round(score)}%
                        </span>
                      )}
                    </div>

                    {/* Candidate Answer */}
                    {q.answer?.answer_text && (
                      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3 text-xs text-[var(--text-secondary)] leading-relaxed">
                        <span className="font-bold text-[var(--text-primary)] block mb-1">
                          Your Answer:
                        </span>
                        <p className="whitespace-pre-wrap">{q.answer.answer_text}</p>
                      </div>
                    )}

                    {/* Strengths & Missing */}
                    {evalData && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                        {evalData.identified_concepts?.length > 0 && (
                          <div className="rounded-xl bg-emerald-500/10 p-2.5 text-emerald-800 dark:text-emerald-300">
                            <span className="font-bold block mb-1">Covered Concepts:</span>
                            <span>{evalData.identified_concepts.join(', ')}</span>
                          </div>
                        )}
                        {evalData.missing_concepts?.length > 0 && (
                          <div className="rounded-xl bg-amber-500/10 p-2.5 text-amber-800 dark:text-amber-300">
                            <span className="font-bold block mb-1">Missing Concepts:</span>
                            <span>{evalData.missing_concepts.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* 9. Mandatory Assessment Disclaimer */}
      <div className="flex items-start gap-3 rounded-2xl border border-indigo-500/20 bg-indigo-500/5 dark:bg-indigo-500/10 p-4 text-xs text-[var(--text-secondary)] leading-relaxed">
        <Info size={16} className="text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-[var(--text-primary)]">Assessment Disclaimer: </span>
          Evaluation is based on a deterministic rubric and concept matching. It provides
          practice guidance, not human or LLM-level semantic judgment, and does not guarantee
          interview success.
        </div>
      </div>

      {/* 10. Bottom Action Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-[var(--border)]">
        <button
          type="button"
          onClick={onBackToOverview}
          className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] px-5 py-2.5 text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all w-full sm:w-auto"
        >
          Return to Overview
        </button>

        <button
          type="button"
          onClick={onStartNew}
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-md hover:from-purple-500 hover:to-indigo-500 transition-all hover:scale-[1.02] active:scale-[0.98] w-full sm:w-auto"
        >
          <RotateCcw size={14} />
          <span>Start Another Interview</span>
        </button>
      </div>
    </div>
  )
}
