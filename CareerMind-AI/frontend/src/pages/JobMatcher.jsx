import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
    BriefcaseBusiness,
    Sparkles,
    FileSearch,
    AlertCircle,
    RotateCcw,
    FileText,
    ShieldCheck,
    Cpu,
    BarChart3,
    Code2,
    Briefcase,
    GraduationCap,
    Route,
    ChevronDown,
    ChevronUp,
} from 'lucide-react'

import { useCandidate } from '../context/CandidateContext'
import { matchJob } from '../services/jobService'

import JobDescriptionForm from '../components/job-matcher/JobDescriptionForm'
import MatchScoreCard from '../components/job-matcher/MatchScoreCard'
import ScoreBreakdown from '../components/job-matcher/ScoreBreakdown'
import MatchedSkills from '../components/job-matcher/MatchedSkills'
import RelatedSkills from '../components/job-matcher/RelatedSkills'
import MissingSkills from '../components/job-matcher/MissingSkills'
import ExperienceMatch from '../components/job-matcher/ExperienceMatch'
import EducationMatch from '../components/job-matcher/EducationMatch'
import Recommendations from '../components/job-matcher/Recommendations'
import ErrorBoundary from '../components/common/ErrorBoundary'

const JOB_MATCHER_TABS = [
    {
        id: 'overview',
        label: 'Overview',
        icon: BarChart3,
    },
    {
        id: 'skills',
        label: 'Skills',
        icon: Code2,
    },
    {
        id: 'experience',
        label: 'Experience',
        icon: Briefcase,
    },
    {
        id: 'education',
        label: 'Education',
        icon: GraduationCap,
    },
    {
        id: 'roadmap',
        label: 'Roadmap',
        icon: Route,
    },
]

export default function JobMatcher() {
    const { fileId, hasResume } = useCandidate()

    const [isLoading, setIsLoading] = useState(false)
    const [matchResult, setMatchResult] = useState(null)
    const [errorMessage, setErrorMessage] = useState('')
    const [lastSubmission, setLastSubmission] = useState(null)
    const [isFormCollapsed, setIsFormCollapsed] = useState(false)
    const [activeTab, setActiveTab] = useState('overview')

    async function handleRunMatch(formData) {
        if (!fileId) {
            setErrorMessage('No active resume found. Please upload your resume first.')
            return
        }

        setIsLoading(true)
        setErrorMessage('')
        setLastSubmission(formData)

        try {
            const payload = {
                file_id: fileId,
                job_description: formData.job_description,
                job_title: formData.job_title,
                company: formData.company,
                location: formData.location,
            }

            const response = await matchJob(payload)
            setMatchResult(response)
            setIsFormCollapsed(true)
            setActiveTab('overview')
        } catch (err) {
            setErrorMessage(
                err.userMessage ||
                err.message ||
                'An error occurred during job description matching. Please try again.'
            )
        } finally {
            setIsLoading(false)
        }
    }

    function handleResetAnalysis() {
        setMatchResult(null)
        setErrorMessage('')
        setIsFormCollapsed(false)
        setActiveTab('overview')
    }

    function handleTabClick(tabId) {
        setActiveTab(tabId)
        const dashboardContent = document.querySelector('.dashboard-content')
        if (dashboardContent) {
            dashboardContent.scrollTo({ top: 0, behavior: 'smooth' })
        }
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    return (
        <div className="mx-auto w-full max-w-6xl space-y-6 sm:space-y-8 animate-fadeIn">
            {/* Page Header */}
            <div>
                <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--accent)]">
                    <Sparkles size={16} />
                    <span>Explainable Matching Engine</span>
                </div>

                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <h1 className="text-2xl font-extrabold tracking-tight text-[var(--text-primary)] sm:text-3xl md:text-4xl flex items-center gap-2.5">
                            <BriefcaseBusiness className="text-[var(--accent)] shrink-0" size={28} />
                            <span>Job Description Matcher</span>
                        </h1>
                        <p className="mt-1 text-xs sm:text-sm text-[var(--text-secondary)]">
                            Compare candidate skills, experience tenure, and education credentials against target job postings with explainable scoring.
                        </p>
                    </div>

                    {/* Active Resume Status Badge & Navigation */}
                    <div className="flex flex-wrap items-center gap-2.5 self-start sm:self-center">
                        {hasResume ? (
                            <div className="flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2 text-xs">
                                <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                                <span className="text-[var(--text-secondary)]">Active Resume:</span>
                                <span className="font-mono font-semibold text-[var(--text-primary)]">
                                    {fileId.slice(0, 8)}...{fileId.slice(-6)}
                                </span>
                                <Link
                                    to="/resume"
                                    className="ml-1 text-[var(--accent)] hover:underline font-medium"
                                    title="View or change resume"
                                >
                                    Change
                                </Link>
                            </div>
                        ) : (
                            <Link
                                to="/resume"
                                className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2 text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)] transition-all"
                            >
                                <FileSearch size={14} className="text-[var(--accent)]" />
                                <span>Go to Resume Analyzer</span>
                            </Link>
                        )}
                    </div>
                </div>
            </div>

            {/* State 1: No Resume Uploaded Error / Empty State */}
            {!hasResume && (
                <div className="glass-card rounded-2xl p-8 sm:p-12 text-center space-y-5">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <FileSearch size={32} />
                    </div>

                    <div className="max-w-md mx-auto space-y-2">
                        <h3 className="text-xl font-bold text-[var(--text-primary)]">
                            Upload a Resume to Begin Matching
                        </h3>
                        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                            CareerMind AI compares verified candidate skills, work tenure, and educational qualifications against structured job criteria. Please upload or analyze your resume first.
                        </p>
                    </div>

                    <div>
                        <Link
                            to="/resume"
                            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-6 py-3 text-sm font-semibold text-white shadow-md shadow-indigo-500/20 transition-all hover:opacity-95 hover:shadow-lg"
                        >
                            <FileSearch size={16} />
                            <span>Open Resume Analyzer</span>
                        </Link>
                    </div>

                    <div className="pt-4 max-w-lg mx-auto flex items-center justify-center gap-2 text-xs text-[var(--text-muted)]">
                        <ShieldCheck size={14} className="text-[var(--success)]" />
                        <span>All processing occurs securely in your local environment. Zero external LLM APIs.</span>
                    </div>
                </div>
            )}

            {/* Error Banner */}
            {errorMessage && (
                <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-5 shadow-sm space-y-2">
                    <div className="flex items-start gap-3">
                        <AlertCircle size={20} className="mt-0.5 shrink-0 text-red-400" />
                        <div className="space-y-1">
                            <h4 className="text-sm font-bold text-red-300">
                                Match Analysis Error
                            </h4>
                            <p className="text-xs text-red-200 leading-relaxed">
                                {errorMessage}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* State 2: Resume Available -> Show Form */}
            {hasResume && (
                <div className="space-y-4">
                    {/* Collapsible toggle if already matched */}
                    {matchResult && (
                        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                            <button
                                type="button"
                                onClick={() => setIsFormCollapsed(!isFormCollapsed)}
                                className="inline-flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                                aria-expanded={!isFormCollapsed}
                                aria-controls="job-description-form-section"
                            >
                                <FileText size={14} className="text-[var(--accent)]" />
                                <span>{isFormCollapsed ? 'Show Job Description' : 'Hide Job Description'}</span>
                                {isFormCollapsed ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
                            </button>

                            <button
                                type="button"
                                onClick={handleResetAnalysis}
                                className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)] transition-all cursor-pointer"
                            >
                                <RotateCcw size={13} />
                                <span>Match Another Job</span>
                            </button>
                        </div>
                    )}

                    {(!matchResult || !isFormCollapsed) && (
                        <div id="job-description-form-section">
                            <JobDescriptionForm
                                onSubmit={handleRunMatch}
                                isLoading={isLoading}
                                initialValues={lastSubmission || {}}
                            />
                        </div>
                    )}
                </div>
            )}

            {/* Honest Loading Indicator */}
            {isLoading && (
                <div className="glass-card rounded-2xl p-10 text-center space-y-4 animate-pulse">
                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <Cpu size={28} className="animate-spin text-[var(--accent)]" />
                    </div>
                    <div className="space-y-1">
                        <h4 className="text-base font-bold text-[var(--text-primary)]">
                            Analyzing your resume against this job description...
                        </h4>
                        <p className="text-xs text-[var(--text-secondary)] max-w-md mx-auto">
                            Evaluating required skills, experience tenure, and education credentials deterministically.
                        </p>
                    </div>
                </div>
            )}

            {/* State 3: Analysis Results View */}
            {matchResult && !isLoading && (
                <div className="space-y-6 sm:space-y-8 animate-fadeIn">
                    {/* MOBILE-ONLY 5-TAB NAVIGATION (< 450px) */}
                    <div className="mobile-job-tabs-container">
                        <div className="mobile-job-tabs-nav" role="tablist" aria-label="Match report sections">
                            {JOB_MATCHER_TABS.map((tab) => {
                                const Icon = tab.icon
                                const isActive = activeTab === tab.id

                                return (
                                    <button
                                        key={tab.id}
                                        type="button"
                                        role="tab"
                                        id={`tab-${tab.id}`}
                                        aria-selected={isActive}
                                        aria-controls={`panel-${tab.id}`}
                                        tabIndex={isActive ? 0 : -1}
                                        onClick={() => handleTabClick(tab.id)}
                                        className={`mobile-job-tab-btn ${isActive ? 'active' : ''}`}
                                    >
                                        <Icon size={15} strokeWidth={isActive ? 2.3 : 1.8} className="shrink-0" />
                                        <span className="mobile-job-tab-label">{tab.label}</span>
                                    </button>
                                )
                            })}
                        </div>
                    </div>

                    {/* 1. OVERVIEW PANEL */}
                    <div
                        id="panel-overview"
                        role="tabpanel"
                        aria-labelledby="tab-overview"
                        className={`job-match-tab-panel ${activeTab === 'overview' ? 'active-mobile-panel' : ''} space-y-6 sm:space-y-8`}
                    >
                        {/* Overall Match Score Card */}
                        <ErrorBoundary title="Match Score Summary">
                            <MatchScoreCard
                                matchScore={matchResult.match_score}
                                overallScore={matchResult.overall_score}
                                matchClassification={matchResult.match_classification}
                                targetTitle={matchResult.parsed_job?.job_title}
                                targetCompany={matchResult.parsed_job?.company}
                            />
                        </ErrorBoundary>

                        {/* Multi-Dimensional Score Breakdown */}
                        {matchResult.match_score?.components && (
                            <ErrorBoundary title="Score Breakdown">
                                <ScoreBreakdown
                                    components={matchResult.match_score.components}
                                />
                            </ErrorBoundary>
                        )}
                    </div>

                    {/* 2. SKILLS PANEL */}
                    <div
                        id="panel-skills"
                        role="tabpanel"
                        aria-labelledby="tab-skills"
                        className={`job-match-tab-panel ${activeTab === 'skills' ? 'active-mobile-panel' : ''} space-y-6 sm:space-y-8`}
                    >
                        {/* Matched Skills Overview */}
                        <ErrorBoundary title="Matched Skills">
                            <MatchedSkills
                                matchedSkills={matchResult.matched_skills || []}
                            />
                        </ErrorBoundary>

                        {/* Semantically Related Skills */}
                        {matchResult.related_skills && matchResult.related_skills.length > 0 && (
                            <ErrorBoundary title="Related Skills">
                                <RelatedSkills
                                    relatedSkills={matchResult.related_skills}
                                />
                            </ErrorBoundary>
                        )}

                        {/* Identified Skill Gaps */}
                        <ErrorBoundary title="Missing Skills Assessment">
                            <MissingSkills
                                missingRequired={matchResult.missing_required_skills || []}
                                missingPreferred={matchResult.missing_preferred_skills || []}
                            />
                        </ErrorBoundary>
                    </div>

                    {/* 3. EXPERIENCE PANEL */}
                    <div
                        id="panel-experience"
                        role="tabpanel"
                        aria-labelledby="tab-experience"
                        className={`job-match-tab-panel ${activeTab === 'experience' ? 'active-mobile-panel' : ''}`}
                    >
                        {matchResult.experience_match && (
                            <ErrorBoundary title="Experience Assessment">
                                <ExperienceMatch
                                    experienceMatch={matchResult.experience_match}
                                />
                            </ErrorBoundary>
                        )}
                    </div>

                    {/* 4. EDUCATION PANEL */}
                    <div
                        id="panel-education"
                        role="tabpanel"
                        aria-labelledby="tab-education"
                        className={`job-match-tab-panel ${activeTab === 'education' ? 'active-mobile-panel' : ''}`}
                    >
                        {matchResult.education_match && (
                            <ErrorBoundary title="Education Alignment">
                                <EducationMatch
                                    educationMatch={matchResult.education_match}
                                />
                            </ErrorBoundary>
                        )}
                    </div>

                    {/* 5. ROADMAP PANEL */}
                    <div
                        id="panel-roadmap"
                        role="tabpanel"
                        aria-labelledby="tab-roadmap"
                        className={`job-match-tab-panel ${activeTab === 'roadmap' ? 'active-mobile-panel' : ''}`}
                    >
                        {matchResult.recommendations && (
                            <ErrorBoundary title="Recommendations">
                                <Recommendations
                                    recommendations={matchResult.recommendations}
                                />
                            </ErrorBoundary>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
