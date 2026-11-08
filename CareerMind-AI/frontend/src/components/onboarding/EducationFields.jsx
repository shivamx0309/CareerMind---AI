import { GraduationCap } from 'lucide-react'

const EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "Doctorate / Ph.D.",
    "Associate Degree",
    "Diploma / Certification",
    "High School",
]

export default function EducationFields({ formData, onChange, errors = {}, hideHeader = false }) {
    return (
        <section className="space-y-4">
            {!hideHeader && (
                <div className="border-b border-[var(--border)] pb-2.5">
                    <h3 className="text-sm font-bold uppercase tracking-wider text-[var(--accent)] flex items-center gap-2">
                        <GraduationCap size={15} />
                        <span>Educational Background</span>
                    </h3>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Your highest qualification helps match education requirements in job postings.
                    </p>
                </div>
            )}

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {/* Highest Education Level */}
                <div className="space-y-1.5">
                    <label htmlFor="highest_education" className="block text-xs font-semibold text-[var(--text-primary)]">
                        Highest Education Level <span className="text-rose-500">*</span>
                    </label>
                    <div className="relative">
                        <select
                            id="highest_education"
                            name="highest_education"
                            value={formData.highest_education}
                            onChange={(e) => onChange('highest_education', e.target.value)}
                            className={`w-full rounded-xl border bg-[var(--surface-solid)] px-3.5 py-2.5 text-xs text-[var(--text-primary)] focus:outline-none transition-all ${
                                errors.highest_education
                                    ? 'border-rose-500 focus:border-rose-500'
                                    : 'border-[var(--border)] focus:border-[var(--accent)]'
                            }`}
                        >
                            <option value="">Select qualification level...</option>
                            {EDUCATION_LEVELS.map((lvl) => (
                                <option key={lvl} value={lvl}>
                                    {lvl}
                                </option>
                            ))}
                        </select>
                    </div>
                    {errors.highest_education && (
                        <p className="text-[11px] font-medium text-rose-500">{errors.highest_education}</p>
                    )}
                </div>

                {/* Degree / Qualification Specialization */}
                <div className="space-y-1.5">
                    <label htmlFor="degree" className="block text-xs font-semibold text-[var(--text-primary)]">
                        Degree / Specialization <span className="text-rose-500">*</span>
                    </label>
                    <div className="relative">
                        <input
                            id="degree"
                            type="text"
                            name="degree"
                            value={formData.degree}
                            onChange={(e) => onChange('degree', e.target.value)}
                            placeholder="e.g. B.Tech Computer Science, B.S. Data Science"
                            maxLength={150}
                            className={`w-full rounded-xl border bg-[var(--surface-solid)] px-3.5 py-2.5 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none transition-all ${
                                errors.degree
                                    ? 'border-rose-500 focus:border-rose-500'
                                    : 'border-[var(--border)] focus:border-[var(--accent)]'
                            }`}
                        />
                    </div>
                    {errors.degree && (
                        <p className="text-[11px] font-medium text-rose-500">{errors.degree}</p>
                    )}
                </div>

                {/* Institution */}
                <div className="space-y-1.5">
                    <label htmlFor="institution" className="block text-xs font-semibold text-[var(--text-primary)]">
                        Institution / University <span className="text-rose-500">*</span>
                    </label>
                    <div className="relative">
                        <input
                            id="institution"
                            type="text"
                            name="institution"
                            value={formData.institution}
                            onChange={(e) => onChange('institution', e.target.value)}
                            placeholder="e.g. University of California, Berkeley"
                            maxLength={200}
                            className={`w-full rounded-xl border bg-[var(--surface-solid)] px-3.5 py-2.5 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none transition-all ${
                                errors.institution
                                    ? 'border-rose-500 focus:border-rose-500'
                                    : 'border-[var(--border)] focus:border-[var(--accent)]'
                            }`}
                        />
                    </div>
                    {errors.institution && (
                        <p className="text-[11px] font-medium text-rose-500">{errors.institution}</p>
                    )}
                </div>

                {/* Graduation Year */}
                <div className="space-y-1.5">
                    <label htmlFor="graduation_year" className="block text-xs font-semibold text-[var(--text-primary)]">
                        Graduation Year (or Expected) <span className="text-rose-500">*</span>
                    </label>
                    <div className="relative">
                        <input
                            id="graduation_year"
                            type="number"
                            name="graduation_year"
                            value={formData.graduation_year || ''}
                            onChange={(e) => {
                                const val = e.target.value ? parseInt(e.target.value, 10) : ''
                                onChange('graduation_year', val)
                            }}
                            placeholder="e.g. 2025"
                            min={1970}
                            max={2040}
                            className={`w-full rounded-xl border bg-[var(--surface-solid)] px-3.5 py-2.5 text-xs text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none transition-all ${
                                errors.graduation_year
                                    ? 'border-rose-500 focus:border-rose-500'
                                    : 'border-[var(--border)] focus:border-[var(--accent)]'
                            }`}
                        />
                    </div>
                    {errors.graduation_year && (
                        <p className="text-[11px] font-medium text-rose-500">{errors.graduation_year}</p>
                    )}
                </div>
            </div>
        </section>
    )
}
