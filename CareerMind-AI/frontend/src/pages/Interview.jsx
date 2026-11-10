import { useState, useEffect } from 'react'
import {
  getInterviewMetadata,
  startInterviewSession,
  getInterviewHistory,
  getInterviewSession,
  submitAnswer,
  completeInterview,
  getInterviewReport,
  deleteInterviewSession,
} from '../services/interviewService'

import InterviewOverview from '../components/interview/InterviewOverview'
import InterviewHistory from '../components/interview/InterviewHistory'
import InterviewSessionWorkspace from '../components/interview/InterviewSessionWorkspace'
import InterviewReport from '../components/interview/InterviewReport'
import InterviewSetupModal from '../components/interview/InterviewSetupModal'
import InterviewConfirmModal from '../components/interview/InterviewConfirmModal'
import InterviewErrorState from '../components/interview/InterviewErrorState'

export default function Interview() {
  // Page Mode: 'overview' | 'workspace' | 'report'
  const [viewMode, setViewMode] = useState('overview')

  // Main Data States
  const [metadata, setMetadata] = useState(null)
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [activeReport, setActiveReport] = useState(null)

  // Loading & Error States
  const [isLoadingInitial, setIsLoadingInitial] = useState(true)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [pageError, setPageError] = useState(null)

  // Modals
  const [isSetupModalOpen, setIsSetupModalOpen] = useState(false)
  const [deleteSessionId, setDeleteSessionId] = useState(null)
  const [isConfirmExitOpen, setIsConfirmExitOpen] = useState(false)

  // Initial Load: Fetch metadata and past sessions
  useEffect(() => {
    let isMounted = true

    async function initInterviewPage() {
      try {
        const [meta, hist] = await Promise.all([
          getInterviewMetadata().catch((err) => {
            console.warn('Metadata fetch warning:', err)
            return null
          }),
          getInterviewHistory().catch((err) => {
            console.warn('History fetch warning:', err)
            return []
          }),
        ])

        if (!isMounted) return
        setMetadata(meta)
        setSessions(Array.isArray(hist) ? hist : [])
      } catch (err) {
        if (!isMounted) return
        setPageError(
          err.userMessage ||
            err.message ||
            'Failed to initialize interview simulator. Please refresh.'
        )
      } finally {
        if (isMounted) setIsLoadingInitial(false)
      }
    }

    initInterviewPage()

    return () => {
      isMounted = false
    }
  }, [])

  // Refresh sessions history
  const refreshHistory = async () => {
    setIsLoadingHistory(true)
    try {
      const hist = await getInterviewHistory()
      setSessions(Array.isArray(hist) ? hist : [])
    } catch (err) {
      console.warn('Failed to refresh history:', err)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  // Handle Starting a New Interview Session
  const handleStartSession = async (payload) => {
    const newSession = await startInterviewSession(payload)
    setActiveSession(newSession)
    setActiveReport(null)
    setViewMode('workspace')
    refreshHistory()
  }

  // Handle Selecting a Session from History (Resume or View Report)
  const handleSelectSession = async (sessionId) => {
    setPageError(null)
    try {
      const session = await getInterviewSession(sessionId)
      setActiveSession(session)

      if (session.status === 'completed') {
        const report = await getInterviewReport(sessionId)
        setActiveReport(report)
        setViewMode('report')
      } else {
        setActiveReport(null)
        setViewMode('workspace')
      }
    } catch (err) {
      setPageError(
        err.response?.data?.detail ||
          err.message ||
          'Failed to load selected interview session.'
      )
    }
  }

  // Handle Submitting an Answer to Active Session
  const handleSubmitAnswer = async ({ question_id, answer_text }) => {
    if (!activeSession) return null

    const answerResponse = await submitAnswer(activeSession.id, {
      question_id,
      answer_text,
    })

    // Update activeSession question snapshot locally to keep state fresh
    setActiveSession((prev) => {
      if (!prev) return prev
      const updatedQuestions = prev.questions.map((q) => {
        if (q.id === question_id) {
          return {
            ...q,
            is_answered: true,
            answer: answerResponse,
          }
        }
        return q
      })
      return {
        ...prev,
        current_question_index: Math.min(
          prev.total_questions,
          prev.current_question_index + 1
        ),
        questions: updatedQuestions,
      }
    })

    return answerResponse
  }

  // Handle Finalizing the Active Session
  const handleCompleteSession = async () => {
    if (!activeSession) return

    const report = await completeInterview(activeSession.id)
    setActiveReport(report)

    // Refresh session details to show completed status
    const refreshedSession = await getInterviewSession(activeSession.id).catch(
      () => activeSession
    )
    setActiveSession(refreshedSession)
    setViewMode('report')
    refreshHistory()
  }

  // Handle Deleting a Session
  const handleConfirmDelete = async () => {
    if (!deleteSessionId) return
    try {
      await deleteInterviewSession(deleteSessionId)
      if (activeSession?.id === deleteSessionId) {
        setActiveSession(null)
        setActiveReport(null)
        setViewMode('overview')
      }
      setDeleteSessionId(null)
      refreshHistory()
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          err.message ||
          'Failed to delete interview session.'
      )
      setDeleteSessionId(null)
    }
  }

  // Exit Workspace flow
  const handleExitWorkspace = () => {
    if (activeSession?.status === 'in_progress') {
      setIsConfirmExitOpen(true)
    } else {
      setViewMode('overview')
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-20 md:pb-12 px-3 sm:px-6">
      {/* Global Error Banner */}
      {pageError && (
        <InterviewErrorState
          message={pageError}
          onRetry={refreshHistory}
        />
      )}

      {/* Main Mode Switching */}
      {isLoadingInitial ? (
        <div className="min-h-[400px] flex flex-col items-center justify-center space-y-3">
          <div className="w-10 h-10 border-3 border-[var(--accent)] border-t-transparent rounded-full animate-spin" />
          <p className="text-xs font-semibold text-[var(--text-secondary)]">
            Loading Mock Interview Workspace...
          </p>
        </div>
      ) : viewMode === 'workspace' && activeSession ? (
        /* Workspace Screen */
        <InterviewSessionWorkspace
          key={activeSession.id}
          session={activeSession}
          onSubmitAnswer={handleSubmitAnswer}
          onCompleteSession={handleCompleteSession}
          onExitSession={handleExitWorkspace}
        />
      ) : viewMode === 'report' && activeReport ? (
        /* Report Screen */
        <InterviewReport
          report={activeReport}
          session={activeSession}
          onStartNew={() => setIsSetupModalOpen(true)}
          onBackToOverview={() => {
            setViewMode('overview')
            setActiveReport(null)
          }}
        />
      ) : (
        /* Overview & History Screen */
        <div className="space-y-8">
          <InterviewOverview
            sessions={sessions}
            onStartNew={() => setIsSetupModalOpen(true)}
            onViewHistory={() => {
              const histEl = document.getElementById('interview-history-section')
              histEl?.scrollIntoView({ behavior: 'smooth' })
            }}
          />

          <div id="interview-history-section">
            <InterviewHistory
              sessions={sessions}
              onSelectSession={handleSelectSession}
              onDeleteSession={(sessionId) => setDeleteSessionId(sessionId)}
              onStartNew={() => setIsSetupModalOpen(true)}
              isLoading={isLoadingHistory}
            />
          </div>
        </div>
      )}

      {/* Setup Modal */}
      <InterviewSetupModal
        isOpen={isSetupModalOpen}
        onClose={() => setIsSetupModalOpen(false)}
        metadata={metadata}
        onStartSession={handleStartSession}
      />

      {/* Delete Confirmation Modal */}
      <InterviewConfirmModal
        isOpen={deleteSessionId !== null}
        title="Delete Interview Session"
        message="Are you sure you want to delete this mock interview session? All questions, submitted answers, rubric evaluations, and reports will be permanently removed."
        confirmLabel="Delete Session"
        isDestructive={true}
        onConfirm={handleConfirmDelete}
        onCancel={() => setDeleteSessionId(null)}
      />

      {/* Exit In-Progress Session Confirmation Modal */}
      <InterviewConfirmModal
        isOpen={isConfirmExitOpen}
        title="Pause Interview Session"
        message="Your interview session is currently in progress. Your submitted answers are saved, and you can resume this session anytime from the history list."
        confirmLabel="Exit to Dashboard"
        cancelLabel="Continue Interview"
        isDestructive={false}
        onConfirm={() => {
          setIsConfirmExitOpen(false)
          setViewMode('overview')
        }}
        onCancel={() => setIsConfirmExitOpen(false)}
      />
    </div>
  )
}
