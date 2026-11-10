import { useState, useEffect } from 'react'
import {
  X,
  Sparkles,
  Briefcase,
  Layers,
  Gauge,
  HelpCircle,
  FileText,
  AlertTriangle,
  ChevronRight,
} from 'lucide-react'
import { getResumeLibrary, getReports } from '../../services/skillGapService'

export default function InterviewSetupModal({
  isOpen,
  onClose,
  metadata,
  onStartSession,
}) {
  // Config state
  const [targetRole, setTargetRole] = useState('sde')
  const [interviewType, setInterviewType] = useState('technical')
  const [difficulty, setDifficulty] = useState('intermediate')
  const [questionCount, setQuestionCount] = useState(5)
  const [resumeId, setResumeId] = useState('')
  const [skillGapReportId, setSkillGapReportId] = useState('')

  // Aux data
  const [resumes, setResumes] = useState([])
  const [gapReports, setGapReports] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)

  // Fetch candidate resumes and skill gap reports when modal opens
  useEffect(() => {
    if (!isOpen) return

    let isMounted = true

    Promise.all([
      getResumeLibrary().catch(() => []),
      getReports().catch(() => []),
    ]).then(([resList, repList]) => {
      if (!isMounted) return
      setResumes(Array.isArray(resList) ? resList : [])
      setGapReports(Array.isArray(repList) ? repList : [])

      // Auto-select default resume if available
      const defaultRes = (resList || []).find((r) => r.is_default)
      if (defaultRes) {
        setResumeId(defaultRes.id)
      }
    })

    return () => {
      isMounted = false
    }
  }, [isOpen])

  if (!isOpen) return null

  // Fallback defaults if metadata is still loading
  const roles = metadata?.roles || [
    { role_id: 'sde', title: 'Software Development Engineer (SDE)' },
    { role_id: 'backend_developer', title: 'Backend Developer' },
    { role_id: 'frontend_developer', title: 'Frontend Developer' },
    { role_id: 'full_stack_developer', title: 'Full Stack Developer' },
    { role_id: 'data_analyst', title: 'Data Analyst' },
    { role_id: 'data_scientist', title: 'Data Scientist' },
    { role_id: 'machine_learning_engineer', title: 'Machine Learning Engineer' },
    { role_id: 'python_developer', title: 'Python Developer' },
  ]

  const interviewTypes = metadata?.interview_types || [
    { type_id: 'technical', title: 'Technical Interview', description: 'Core CS, algorithms, syntax & frameworks' },
    { type_id: 'behavioral', title: 'HR & Behavioral', description: 'STAR rubric, leadership & communication' },
    { type_id: 'project', title: 'Project-Based', description: 'Architecture, trade-offs & practical decisions' },
    { type_id: 'mixed', title: 'Mixed Interview', description: 'Balanced blend of technical, project & HR' },
  ]

  const difficulties = metadata?.difficulties || [
    { difficulty_id: 'beginner', title: 'Beginner' },
    { difficulty_id: 'intermediate', title: 'Intermediate' },
    { difficulty_id: 'advanced', title: 'Advanced' },
  ]

  const questionCounts = metadata?.question_counts || [5, 10, 15, 20]

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setErrorMessage(null)

    try {
      const payload = {
        target_role: targetRole,
        interview_type: interviewType,
        difficulty: difficulty,
        question_count: parseInt(questionCount, 10),
      }
      if (resumeId) payload.resume_id = resumeId
      if (skillGapReportId) payload.skill_gap_report_id = skillGapReportId

      await onStartSession(payload)
      onClose()
    } catch (err) {
      setErrorMessage(
        err.response?.data?.detail ||
          err.message ||
          'Failed to configure mock interview. Please verify selections.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const selectedRoleObj = roles.find((r) => r.role_id === targetRole)

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="setup-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto animate-in fade-in duration-200"
    >
      <div className="relative w-full max-w-2xl my-8 rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] shadow-2xl p-6 md:p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[var(--border)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 text-purple-600 dark:text-purple-400 flex items-center justify-center">
              <Sparkles size={20} />
            </div>
            <div>
              <h2
                id="setup-modal-title"
                className="text-lg md:text-xl font-bold text-[var(--text-primary)]"
              >
                Configure Mock Interview
              </h2>
              <p className="text-xs text-[var(--text-secondary)]">
                Tailor your session by target role, format, depth, and candidate gaps.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="rounded-xl p-2 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all"
            aria-label="Close modal"
          >
            <X size={20} />
          </button>
        </div>

        {/* Error message */}
        {errorMessage && (
          <div className="flex items-start gap-2.5 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-3.5 text-xs text-rose-600 dark:text-rose-400">
            <AlertTriangle size={16} className="shrink-0 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Section 1: Target Role */}
          <div className="space-y-2">
            <label
              htmlFor="target-role-select"
              className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]"
            >
              <Briefcase size={14} className="text-[var(--accent)]" />
              <span>1. Target Engineering Role</span>
            </label>
            <select
              id="target-role-select"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
            >
              {roles.map((r) => (
                <option key={r.role_id} value={r.role_id} className="bg-[var(--surface-solid)]">
                  {r.title}
                </option>
              ))}
            </select>
          </div>

          {/* Section 2: Format & Difficulty */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Interview Format */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                <Layers size={14} className="text-[var(--accent)]" />
                <span>2. Interview Format</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                {interviewTypes.map((t) => (
                  <button
                    key={t.type_id}
                    type="button"
                    onClick={() => setInterviewType(t.type_id)}
                    className={`flex flex-col items-start p-3 rounded-2xl border text-left transition-all ${
                      interviewType === t.type_id
                        ? 'border-purple-500 bg-purple-500/15 text-[var(--text-primary)] shadow-sm'
                        : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]'
                    }`}
                  >
                    <span className="text-xs font-bold leading-tight">{t.title}</span>
                    <span className="text-[10px] text-[var(--text-muted)] line-clamp-1 mt-0.5">
                      {t.description || t.type_id}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Difficulty Tier */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                <Gauge size={14} className="text-[var(--accent)]" />
                <span>3. Difficulty Tier</span>
              </label>
              <div className="grid grid-cols-3 gap-2">
                {difficulties.map((d) => (
                  <button
                    key={d.difficulty_id}
                    type="button"
                    onClick={() => setDifficulty(d.difficulty_id)}
                    className={`py-3 px-2 rounded-2xl border text-center transition-all ${
                      difficulty === d.difficulty_id
                        ? 'border-indigo-500 bg-indigo-500/15 text-[var(--text-primary)] font-bold shadow-sm'
                        : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]'
                    }`}
                  >
                    <span className="text-xs">{d.title}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Section 3: Question Count */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
              <HelpCircle size={14} className="text-[var(--accent)]" />
              <span>4. Question Count</span>
            </label>
            <div className="grid grid-cols-4 gap-2">
              {questionCounts.map((cnt) => (
                <button
                  key={cnt}
                  type="button"
                  onClick={() => setQuestionCount(cnt)}
                  className={`py-2.5 rounded-2xl border text-center text-xs font-bold transition-all ${
                    questionCount === cnt
                      ? 'border-purple-500 bg-purple-500/20 text-purple-600 dark:text-purple-300 shadow-sm'
                      : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]'
                  }`}
                >
                  {cnt} Questions
                </button>
              ))}
            </div>
          </div>

          {/* Section 4: Optional Personalization */}
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-primary)] flex items-center gap-1.5">
                <FileText size={14} className="text-[var(--accent)]" />
                <span>Optional Personalization</span>
              </span>
              <span className="text-[10px] text-[var(--text-muted)] font-medium">
                Uses existing resumes & reports
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              {/* Resume Selector */}
              <div>
                <label className="block font-semibold text-[var(--text-secondary)] mb-1">
                  Resume Linkage
                </label>
                <select
                  value={resumeId}
                  onChange={(e) => setResumeId(e.target.value)}
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-2 text-xs font-medium text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
                >
                  <option value="">None (Standard Role Practice)</option>
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.original_filename} {r.is_default ? '(Default)' : ''}
                    </option>
                  ))}
                </select>
              </div>

              {/* Skill Gap Report Selector */}
              <div>
                <label className="block font-semibold text-[var(--text-secondary)] mb-1">
                  Skill Gap Bias
                </label>
                <select
                  value={skillGapReportId}
                  onChange={(e) => setSkillGapReportId(e.target.value)}
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-2 text-xs font-medium text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
                >
                  <option value="">None (General Question Pool)</option>
                  {gapReports.map((rep) => (
                    <option key={rep.id} value={rep.id}>
                      {rep.role_title} ({rep.overall_score ?? '—'}% match)
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Configuration Summary Card */}
          <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 p-4 flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="text-xs font-bold text-[var(--text-primary)]">
                {selectedRoleObj?.title || targetRole}
              </div>
              <div className="text-[11px] text-[var(--text-secondary)]">
                {interviewType.toUpperCase()} • {difficulty.toUpperCase()} • {questionCount} Questions
                {skillGapReportId ? ' • Prioritizing Skill Gaps' : ''}
              </div>
            </div>
            <div className="text-xs font-bold text-purple-600 dark:text-purple-400 flex items-center gap-1">
              Ready <ChevronRight size={14} />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-md hover:from-purple-500 hover:to-indigo-500 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Preparing Questions...</span>
                </>
              ) : (
                <>
                  <Sparkles size={14} />
                  <span>Launch Interview Session</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
