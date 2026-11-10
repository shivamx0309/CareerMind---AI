import {
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Check,
  ArrowRight,
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { useState } from 'react'
import EvaluationScoreBreakdown from './EvaluationScoreBreakdown'

export default function AnswerEvaluationPanel({
  evaluation,
  answerText = '',
  hasNextQuestion = false,
  onNextQuestion,
  onCompleteInterview,
  isCompleting = false,
  suggestedPoints = [],
}) {
  const [showAnswerDraft, setShowAnswerDraft] = useState(false)
  const [showModelAnswer, setShowModelAnswer] = useState(false)

  if (!evaluation) return null

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* 1. Score Breakdown */}
      <EvaluationScoreBreakdown
        overallScore={evaluation.overall_score}
        relevanceScore={evaluation.relevance_score}
        conceptCoverageScore={evaluation.concept_coverage_score}
        completenessScore={evaluation.completeness_score}
        structureScore={evaluation.structure_score}
      />

      {/* 2. Concepts Matrix: Identified vs Missing */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Identified Concepts */}
        <div className="rounded-3xl border border-emerald-500/20 bg-emerald-500/5 p-5 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-emerald-700 dark:text-emerald-400">
            <span className="flex items-center gap-1.5 uppercase tracking-wider">
              <CheckCircle2 size={15} /> Identified Concepts ({evaluation.identified_concepts?.length || 0})
            </span>
          </div>
          {evaluation.identified_concepts?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {evaluation.identified_concepts.map((concept) => (
                <span
                  key={concept}
                  className="rounded-xl border border-emerald-500/30 bg-emerald-500/15 px-2.5 py-1 text-xs font-semibold text-emerald-800 dark:text-emerald-300"
                >
                  {concept}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[var(--text-muted)] italic">
              No target technical concepts were matched in this response.
            </p>
          )}
        </div>

        {/* Missing Concepts */}
        <div className="rounded-3xl border border-amber-500/20 bg-amber-500/5 p-5 space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-amber-700 dark:text-amber-400">
            <span className="flex items-center gap-1.5 uppercase tracking-wider">
              <AlertTriangle size={15} /> Missing Key Concepts ({evaluation.missing_concepts?.length || 0})
            </span>
          </div>
          {evaluation.missing_concepts?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {evaluation.missing_concepts.map((concept) => (
                <span
                  key={concept}
                  className="rounded-xl border border-amber-500/30 bg-amber-500/15 px-2.5 py-1 text-xs font-semibold text-amber-800 dark:text-amber-300"
                >
                  {concept}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
              Excellent! All expected target concepts were successfully covered.
            </p>
          )}
        </div>
      </div>

      {/* 3. Strengths & Improvement Suggestions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 space-y-3 shadow-xs">
          <h4 className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] flex items-center gap-2">
            <Check size={14} className="text-emerald-500" />
            <span>Demonstrated Strengths</span>
          </h4>
          <ul className="space-y-2 text-xs text-[var(--text-primary)] leading-relaxed">
            {evaluation.strengths?.map((str, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-500 shrink-0 mt-0.5">•</span>
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Improvement Suggestions */}
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-5 space-y-3 shadow-xs">
          <h4 className="text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)] flex items-center gap-2">
            <Lightbulb size={14} className="text-amber-500" />
            <span>Actionable Suggestions</span>
          </h4>
          <ul className="space-y-2 text-xs text-[var(--text-primary)] leading-relaxed">
            {evaluation.improvement_suggestions?.map((sugg, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-amber-500 shrink-0 mt-0.5">•</span>
                <span>{sugg}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 4. Feedback Rationale Box */}
      <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 md:p-5 space-y-2 text-xs">
        <div className="flex items-center justify-between text-[var(--text-secondary)] font-semibold">
          <span className="flex items-center gap-1.5">
            <Info size={14} className="text-[var(--accent)]" />
            <span>Evaluation Rationale</span>
          </span>
          <span className="font-mono text-[10px] text-[var(--text-muted)] bg-[var(--surface-hover)] px-2 py-0.5 rounded-md border border-[var(--border)]">
            Method: {evaluation.evaluator_method}
          </span>
        </div>
        <p className="text-[var(--text-primary)] leading-relaxed">
          {evaluation.feedback_rationale}
        </p>
      </div>

      {/* 5. Collapsible: Review Submitted Answer */}
      {answerText && (
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] overflow-hidden">
          <button
            type="button"
            onClick={() => setShowAnswerDraft(!showAnswerDraft)}
            className="w-full flex items-center justify-between p-3.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
          >
            <span>Review Your Submitted Response</span>
            {showAnswerDraft ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {showAnswerDraft && (
            <div className="p-4 pt-1 text-xs text-[var(--text-primary)] border-t border-[var(--border)] whitespace-pre-wrap leading-relaxed font-sans bg-[var(--surface-solid)]">
              {answerText}
            </div>
          )}
        </div>
      )}

      {/* 6. Collapsible: Suggested Answer Points (Only shown post-submission) */}
      {suggestedPoints && suggestedPoints.length > 0 && (
        <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 overflow-hidden">
          <button
            type="button"
            onClick={() => setShowModelAnswer(!showModelAnswer)}
            className="w-full flex items-center justify-between p-3.5 text-xs font-semibold text-purple-700 dark:text-purple-300 hover:bg-purple-500/10 transition-all"
          >
            <span className="flex items-center gap-2">
              <Sparkles size={14} /> Suggested Interview Answer Points
            </span>
            {showModelAnswer ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          {showModelAnswer && (
            <div className="p-4 pt-1 text-xs text-[var(--text-primary)] border-t border-purple-500/20 space-y-2 bg-[var(--surface-solid)]">
              {suggestedPoints.map((pt, i) => (
                <div key={i} className="flex items-start gap-2 leading-relaxed">
                  <span className="text-purple-500 shrink-0 font-bold">•</span>
                  <span>{pt}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 7. Primary Next Action */}
      <div className="pt-2 flex items-center justify-end">
        {hasNextQuestion ? (
          <button
            type="button"
            onClick={onNextQuestion}
            className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-3 text-sm font-bold text-white shadow-md hover:from-purple-500 hover:to-indigo-500 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <span>Proceed to Next Question</span>
            <ArrowRight size={16} />
          </button>
        ) : (
          <button
            type="button"
            onClick={onCompleteInterview}
            disabled={isCompleting}
            className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 px-7 py-3 text-sm font-bold text-white shadow-lg hover:from-emerald-500 hover:to-teal-500 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
          >
            {isCompleting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Compiling Final Performance Report...</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Finish Interview & View Final Report</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  )
}
