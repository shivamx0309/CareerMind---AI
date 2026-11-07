import { useState } from 'react'
import {
    Briefcase,
    Building2,
    MapPin,
    FileText,
    Sparkles,
    AlertCircle,
    RotateCcw,
    Send,
} from 'lucide-react'

const SAMPLE_JDS = [
    {
        label: 'Python Backend Developer',
        title: 'Python Backend Developer',
        company: 'NovaTech Solutions',
        location: 'Remote / Bangalore',
        description: `We are looking for a skilled Python Backend Developer to join our core platform engineering team.
Requirements:
- 2+ years of professional software engineering experience.
- Strong proficiency in Python, PostgreSQL, Redis, and RESTful APIs.
- Experience with Docker, Kubernetes, CI/CD pipelines, and cloud deployment.
- Bachelor's degree in Computer Science, Software Engineering, or related quantitative field.
- Preferred qualifications: Familiarity with Kafka or Celery, AWS microservices, and GraphQL.
Responsibilities:
- Design, test, and maintain robust API services and data ingestion pipelines.
- Collaborate with frontend engineers to integrate performant endpoints.
- Write unit tests and maintain clean, self-documenting code.`,
    },
    {
        label: 'Data Analyst',
        title: 'Junior Data Analyst',
        company: 'InsightAnalytics Corp',
        location: 'Hybrid / Mumbai',
        description: `InsightAnalytics is seeking an enthusiastic Data Analyst with hands-on technical skills.
Requirements:
- Bachelor's degree in Computer Science, Statistics, Mathematics, or Data Science.
- Strong proficiency in SQL, Python, Excel, and Power BI or Tableau.
- Solid understanding of Exploratory Data Analysis (EDA) and data visualization principles.
- Minimum 1 year of analytical experience or relevant internship/project portfolio.
- Preferred: Experience with PostgreSQL, Pandas, NumPy, and statistical hypothesis testing.
Responsibilities:
- Transform raw datasets into actionable executive dashboards.
- Write optimized SQL queries across analytical data warehouses.
- Partner with product managers to monitor core business KPIs.`,
    },
]

export default function JobDescriptionForm({
    onSubmit,
    isLoading,
    initialValues = {},
}) {
    const [jobTitle, setJobTitle] = useState(initialValues.job_title || '')
    const [company, setCompany] = useState(initialValues.company || '')
    const [location, setLocation] = useState(initialValues.location || '')
    const [jobDescription, setJobDescription] = useState(initialValues.job_description || '')
    const [validationError, setValidationError] = useState('')

    const charCount = jobDescription.length
    const isTooShort = charCount > 0 && charCount < 50
    const isTooLong = charCount > 30000

    function handleReset() {
        setJobTitle('')
        setCompany('')
        setLocation('')
        setJobDescription('')
        setValidationError('')
    }

    function handleLoadSample(sample) {
        setJobTitle(sample.title)
        setCompany(sample.company)
        setLocation(sample.location)
        setJobDescription(sample.description)
        setValidationError('')
    }

    function handleSubmit(e) {
        e.preventDefault()

        if (isLoading) return

        const cleanedJD = jobDescription.trim()

        if (!cleanedJD) {
            setValidationError('Please enter a job description to analyze.')
            return
        }

        if (cleanedJD.length < 50) {
            setValidationError(
                `Job description must be at least 50 characters (currently ${cleanedJD.length}). Please paste a realistic job description.`
            )
            return
        }

        if (cleanedJD.length > 30000) {
            setValidationError(
                `Job description exceeds the 30,000 character maximum (${cleanedJD.length} characters).`
            )
            return
        }

        const words = cleanedJD.split(/\s+/).filter(Boolean)
        if (words.length < 8) {
            setValidationError(
                'Job description must contain at least 8 recognizable words for meaningful requirement extraction.'
            )
            return
        }

        setValidationError('')
        onSubmit({
            job_title: jobTitle.trim() || undefined,
            company: company.trim() || undefined,
            location: location.trim() || undefined,
            job_description: cleanedJD,
        })
    }

    return (
        <form
            onSubmit={handleSubmit}
            className="glass-card relative overflow-hidden rounded-2xl p-6 sm:p-8"
        >
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[var(--border)] pb-5">
                <div>
                    <h2 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2">
                        <FileText size={18} className="text-[var(--accent)]" />
                        <span>Target Job Posting</span>
                    </h2>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                        Paste the full job description. Our engine will extract required technical skills, experience tenure, and education credentials.
                    </p>
                </div>

                {/* Sample Fill Shortcuts */}
                <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-[var(--text-muted)] hidden lg:inline">Quick Fill:</span>
                    {SAMPLE_JDS.map((sample) => (
                        <button
                            key={sample.label}
                            type="button"
                            onClick={() => handleLoadSample(sample)}
                            disabled={isLoading}
                            className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] bg-[var(--surface-solid)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)] transition-all hover:border-[var(--accent)] hover:text-[var(--text-primary)] disabled:opacity-50"
                        >
                            <Sparkles size={12} className="text-[var(--accent)]" />
                            <span>{sample.label}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Optional Metadata Fields */}
            <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-3">
                {/* Job Title */}
                <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">
                        Job Title <span className="text-[var(--text-muted)] font-normal">(Optional)</span>
                    </label>
                    <div className="relative">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[var(--text-muted)]">
                            <Briefcase size={15} />
                        </div>
                        <input
                            type="text"
                            value={jobTitle}
                            onChange={(e) => setJobTitle(e.target.value)}
                            disabled={isLoading}
                            placeholder="e.g. Senior Backend Engineer"
                            className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] py-2 pl-9 pr-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none transition-all disabled:opacity-50"
                        />
                    </div>
                </div>

                {/* Company Name */}
                <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">
                        Company Name <span className="text-[var(--text-muted)] font-normal">(Optional)</span>
                    </label>
                    <div className="relative">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[var(--text-muted)]">
                            <Building2 size={15} />
                        </div>
                        <input
                            type="text"
                            value={company}
                            onChange={(e) => setCompany(e.target.value)}
                            disabled={isLoading}
                            placeholder="e.g. Stripe, Google, Startup"
                            className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] py-2 pl-9 pr-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none transition-all disabled:opacity-50"
                        />
                    </div>
                </div>

                {/* Location */}
                <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">
                        Location / Work Mode <span className="text-[var(--text-muted)] font-normal">(Optional)</span>
                    </label>
                    <div className="relative">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-[var(--text-muted)]">
                            <MapPin size={15} />
                        </div>
                        <input
                            type="text"
                            value={location}
                            onChange={(e) => setLocation(e.target.value)}
                            disabled={isLoading}
                            placeholder="e.g. Remote, Hybrid, New York"
                            className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] py-2 pl-9 pr-3 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none transition-all disabled:opacity-50"
                        />
                    </div>
                </div>
            </div>

            {/* Job Description Textarea */}
            <div className="mt-5">
                <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-semibold text-[var(--text-primary)]">
                        Job Description Text <span className="text-red-400">*</span>
                    </label>
                    <div className="text-xs">
                        <span
                            className={`font-mono ${
                                isTooShort
                                    ? 'text-amber-400 font-semibold'
                                    : isTooLong
                                    ? 'text-red-400 font-semibold'
                                    : 'text-[var(--text-muted)]'
                            }`}
                        >
                            {charCount.toLocaleString()} / 30,000 chars
                        </span>
                        {isTooShort && (
                            <span className="text-amber-400 ml-1.5 text-[11px]">(min 50)</span>
                        )}
                    </div>
                </div>

                <textarea
                    rows={8}
                    value={jobDescription}
                    onChange={(e) => {
                        setJobDescription(e.target.value)
                        if (validationError) setValidationError('')
                    }}
                    disabled={isLoading}
                    placeholder="Paste the full job posting text here (responsibilities, required qualifications, minimum years of experience, preferred tools)..."
                    className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] p-3.5 text-sm leading-relaxed text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none transition-all disabled:opacity-50 resize-y min-h-[160px]"
                />
            </div>

            {/* Validation Error Banner */}
            {validationError && (
                <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300">
                    <AlertCircle size={16} className="mt-0.5 shrink-0 text-red-400" />
                    <span>{validationError}</span>
                </div>
            )}

            {/* Form Footer Actions */}
            <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between border-t border-[var(--border)] pt-5">
                <button
                    type="button"
                    onClick={handleReset}
                    disabled={isLoading || (!jobTitle && !company && !location && !jobDescription)}
                    className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-4 py-2.5 text-xs font-medium text-[var(--text-secondary)] transition-all hover:bg-[var(--surface-hover)] disabled:opacity-40"
                >
                    <RotateCcw size={14} />
                    <span>Clear Form</span>
                </button>

                <button
                    type="submit"
                    disabled={isLoading || isTooShort || isTooLong}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-6 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-500/20 transition-all hover:opacity-95 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isLoading ? (
                        <>
                            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                            <span>Analyzing Job Match...</span>
                        </>
                    ) : (
                        <>
                            <Send size={15} />
                            <span>Run Match Engine</span>
                        </>
                    )}
                </button>
            </div>
        </form>
    )
}

