import { useState } from 'react'
import { ArrowLeft, AlertTriangle } from 'lucide-react'
import InterviewProgress from './InterviewProgress'
import InterviewQuestionCard from './InterviewQuestionCard'
import InterviewAnswerEditor from './InterviewAnswerEditor'
import AnswerEvaluationPanel from './AnswerEvaluationPanel'

export default function InterviewSessionWorkspace({
  session,
  onSubmitAnswer,
  onCompleteSession,
  onExitSession,
}) {
  const questions = session?.questions || []
  const totalQuestions = session?.total_questions || questions.length || 5

  const [activeQuestionIndex, setActiveQuestionIndex] = useState(() => {
    const idx = questions.findIndex((q) => !q.is_answered)
    return idx !== -1 ? idx : Math.max(0, questions.length - 1)
  })

  const [activeEvaluation, setActiveEvaluation] = useState(() => {
    const idx = questions.findIndex((q) => !q.is_answered)
    if (idx === -1 && questions.length > 0) {
      return questions[questions.length - 1]?.answer?.evaluation || null
    }
    return null
  })

  const [lastSubmittedAnswerText, setLastSubmittedAnswerText] = useState(() => {
    const idx = questions.findIndex((q) => !q.is_answered)
    if (idx === -1 && questions.length > 0) {
      return questions[questions.length - 1]?.answer?.answer_text || ''
    }
    return ''
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)

  const currentQ = questions[activeQuestionIndex] || null
  const isCurrentAnswered = currentQ?.is_answered || activeEvaluation !== null
  const hasNextQuestion = activeQuestionIndex < totalQuestions - 1
  const isLastQuestion = activeQuestionIndex === totalQuestions - 1

  const handleSubmitAnswer = async (answerText) => {
    if (!currentQ) return
    setIsSubmitting(true)
    setErrorMsg(null)

    try {
      setLastSubmittedAnswerText(answerText)
      const answerResponse = await onSubmitAnswer({
        question_id: currentQ.id,
        answer_text: answerText,
      })

      if (answerResponse?.evaluation) {
        setActiveEvaluation(answerResponse.evaluation)
      }
    } catch (err) {
      setErrorMsg(
        err.response?.data?.detail ||
          err.message ||
          'Failed to submit answer. Please check your network and try again.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleNextQuestion = () => {
    setActiveEvaluation(null)
    setLastSubmittedAnswerText('')
    setErrorMsg(null)

    const nextIdx = activeQuestionIndex + 1
    if (nextIdx < totalQuestions) {
      setActiveQuestionIndex(nextIdx)
    }
  }

  const handleComplete = async () => {
    setIsCompleting(true)
    setErrorMsg(null)
    try {
      await onCompleteSession()
    } catch (err) {
      setErrorMsg(
        err.response?.data?.detail ||
          err.message ||
          'Failed to generate final report. Please try again.'
      )
      setIsCompleting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Workspace Navigation Bar */}
      <div className="flex items-center justify-between gap-3 pb-3 border-b border-[var(--border)]">
        <button
          type="button"
          onClick={onExitSession}
          className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
        >
          <ArrowLeft size={14} />
          <span>Exit Workspace</span>
        </button>

        <div className="text-xs text-[var(--text-muted)] font-mono">
          Session ID: {session?.id?.slice(0, 8)}...
        </div>
      </div>

      {/* Progress Telemetry */}
      <InterviewProgress
        currentQuestionIndex={activeQuestionIndex}
        totalQuestions={totalQuestions}
        questions={questions}
        roleTitle={session?.role_title}
        interviewType={session?.interview_type}
        difficulty={session?.difficulty}
      />

      {/* Error Alert */}
      {errorMsg && (
        <div className="flex items-start gap-2.5 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-3.5 text-xs text-rose-600 dark:text-rose-400">
          <AlertTriangle size={16} className="shrink-0 mt-0.5" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Active Question Display */}
      <InterviewQuestionCard
        question={currentQ}
        sequenceOrder={activeQuestionIndex + 1}
        totalQuestions={totalQuestions}
      />

      {/* Dynamic State: Answer Input vs Evaluation Results */}
      {!isCurrentAnswered ? (
        <InterviewAnswerEditor
          onSubmit={handleSubmitAnswer}
          isSubmitting={isSubmitting}
          interviewType={session?.interview_type}
        />
      ) : (
        <AnswerEvaluationPanel
          evaluation={activeEvaluation || currentQ?.answer?.evaluation}
          answerText={lastSubmittedAnswerText || currentQ?.answer?.answer_text || ''}
          hasNextQuestion={hasNextQuestion}
          isLastQuestion={isLastQuestion}
          onNextQuestion={handleNextQuestion}
          onCompleteInterview={handleComplete}
          isCompleting={isCompleting}
          suggestedPoints={currentQ?.suggested_answer_points || []}
        />
      )}
    </div>
  )
}
