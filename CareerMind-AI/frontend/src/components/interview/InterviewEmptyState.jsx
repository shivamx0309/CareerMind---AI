import { Sparkles } from 'lucide-react'
import MindyMascot from '../common/MindyMascot'

export default function InterviewEmptyState({ onStartNew }) {
  return (
    <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-solid)] p-8 md:p-12 text-center max-w-xl mx-auto space-y-4 shadow-sm">
      <div className="flex justify-center">
        <MindyMascot expression="thinking" size="md" alt="Mindy Ready to Interview" />
      </div>

      <div className="space-y-1.5">
        <h3 className="text-lg md:text-xl font-black text-[var(--text-primary)]">
          No Mock Interviews Yet
        </h3>
        <p className="text-xs md:text-sm text-[var(--text-secondary)] leading-relaxed">
          Configure a personalized session to practice realistic engineering interview questions.
          Select your target role and get instant rubric feedback on concept coverage and structure.
        </p>
      </div>

      <div className="pt-2">
        <button
          type="button"
          onClick={onStartNew}
          className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-3 text-sm font-bold text-white shadow-md hover:from-purple-500 hover:to-indigo-500 transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <Sparkles size={16} />
          <span>Configure Your First Session</span>
        </button>
      </div>
    </div>
  )
}
