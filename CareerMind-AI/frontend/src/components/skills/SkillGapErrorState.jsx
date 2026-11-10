import { AlertCircle, XCircle } from 'lucide-react'

export default function SkillGapErrorState({ error, onDismiss }) {
    if (!error) return null

    return (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 sm:p-5 shadow-sm space-y-2">
            <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                    <AlertCircle size={20} className="mt-0.5 shrink-0 text-rose-400" />
                    <div className="space-y-1">
                        <h4 className="text-sm font-bold text-rose-300">
                            Skill Gap Analysis Error
                        </h4>
                        <p className="text-xs text-rose-200 leading-relaxed">
                            {error}
                        </p>
                    </div>
                </div>

                {onDismiss && (
                    <button
                        type="button"
                        onClick={onDismiss}
                        className="text-rose-300 hover:text-white transition-colors cursor-pointer"
                        aria-label="Dismiss error"
                    >
                        <XCircle size={18} />
                    </button>
                )}
            </div>
        </div>
    )
}

