import { User, GraduationCap, Briefcase, Sparkles } from 'lucide-react'

const CAREER_STATUS_OPTIONS = [
    {
        id: 'Student',
        label: 'Student',
        subtitle: 'Currently pursuing a degree',
        icon: GraduationCap,
    },
    {
        id: 'Fresher',
        label: 'Fresher',
        subtitle: 'Recent graduate / entry level',
        icon: Sparkles,
    },
    {
        id: 'Experienced',
        label: 'Experienced',
        subtitle: '1+ years professional tenure',
        icon: Briefcase,
    },
]

export default function PersonalInfoFields({ formData, onChange, errors = {}, hideHeader = false }) {
    return (
        <section className="space-y-4">
            {!hideHeader && (
                <div className="border-b border-[var(--border)] pb-2.5">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--accent)] flex items-center gap-2">
                        <User size={15} />
                        <span>Personal Information</span>
                    </h3>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Your name and current career stage to calibrate recommendations.
                    </p>
                </div>
            )}

            {/* Full Name */}
            <div className="space-y-1.5">
                <label htmlFor="full_name" className="block text-xs font-semibold text-[var(--text-primary)]">
                    Full Name <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                    <input
                        id="full_name"
                        type="text"
                        name="full_name"
                        value={formData.full_name}
                        onChange={(e) => onChange('full_name', e.target.value)}
                        placeholder="e.g. Alex Morgan"
                        maxLength={200}
                        className={`w-full rounded-xl border bg-[var(--surface-solid)] px-3.5 py-2.5 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none transition-all ${
                            errors.full_name
                                ? 'border-rose-500 focus:border-rose-500'
                                : 'border-[var(--border)] focus:border-[var(--accent)]'
                        }`}
                    />
                </div>
                {errors.full_name && (
                    <p className="text-[11px] font-medium text-rose-500">{errors.full_name}</p>
                )}
            </div>

            {/* Career Status Selection Cards */}
            <div className="space-y-1.5">
                <label className="block text-xs font-semibold text-[var(--text-primary)]">
                    Career Status <span className="text-rose-500">*</span>
                </label>
                <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-3">
                    {CAREER_STATUS_OPTIONS.map((opt) => {
                        const Icon = opt.icon
                        const isSelected = formData.career_status === opt.id

                        return (
                            <button
                                key={opt.id}
                                type="button"
                                onClick={() => onChange('career_status', opt.id)}
                                className={`flex flex-col items-start gap-1 rounded-xl border p-3 text-left transition-all cursor-pointer ${
                                    isSelected
                                        ? 'border-[var(--accent)] bg-[var(--accent-soft)] shadow-sm'
                                        : 'border-[var(--border)] bg-[var(--surface-solid)] hover:border-[var(--border-hover)] hover:bg-[var(--surface-hover)]'
                                }`}
                            >
                                <div className="flex items-center gap-2">
                                    <Icon
                                        size={16}
                                        className={isSelected ? 'text-[var(--accent)]' : 'text-[var(--text-secondary)]'}
                                    />
                                    <span
                                        className={`text-xs font-bold ${
                                            isSelected ? 'text-[var(--text-primary)]' : 'text-[var(--text-primary)]'
                                        }`}
                                    >
                                        {opt.label}
                                    </span>
                                </div>
                                <span className="text-[10px] text-[var(--text-secondary)] leading-tight">
                                    {opt.subtitle}
                                </span>
                            </button>
                        )
                    })}
                </div>
                {errors.career_status && (
                    <p className="text-[11px] font-medium text-rose-500">{errors.career_status}</p>
                )}
            </div>
        </section>
    )
}
