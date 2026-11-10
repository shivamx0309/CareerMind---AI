import { useState, useEffect, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import {
    Sparkles,
    ShieldCheck,
    AlertCircle,
    RefreshCw,
    FileCheck2,
    BriefcaseBusiness,
    ArrowRight,
    Check,
    ChevronLeft,
    ChevronRight,
    CheckCircle2,
} from 'lucide-react'

import { useCandidate } from '../context/CandidateContext'
import { uploadResume, parseResume } from '../services/resumeService'
import ResumeUpload from '../components/resume/ResumeUpload'
import ResumeProcessing from '../components/resume/ResumeProcessing'
import CandidateProfile from '../components/resume/CandidateProfile'
import ProfessionalSummary from '../components/resume/ProfessionalSummary'
import SkillsOverview from '../components/resume/SkillsOverview'
import ExperienceTimeline from '../components/resume/ExperienceTimeline'
import EducationTimeline from '../components/resume/EducationTimeline'
import ProjectsSection from '../components/resume/ProjectsSection'
import CertificationsSection from '../components/resume/CertificationsSection'
import ProfileEditor from '../components/resume/ProfileEditor'

const RESUME_SECTIONS = [
    {
        id: 'profile',
        number: '01',
        tabLabel: '01 Profile',
        shortName: 'Profile',
        title: 'Candidate Profile & Summary',
        description: 'Candidate contact details, professional summary and core profile actions.',
    },
    {
        id: 'skills',
        number: '02',
        tabLabel: '02 Skills',
        shortName: 'Skills',
        title: 'Technical Skills Intelligence',
        description: 'Technical taxonomy, competency categories and extracted skills.',
    },
    {
        id: 'experience',
        number: '03',
        tabLabel: '03 Experience',
        shortName: 'Experience',
        title: 'Work Experience & Internships',
        description: 'Career history, internships, roles, tenure and responsibilities.',
    },
    {
        id: 'education',
        number: '04',
        tabLabel: '04 Education',
        shortName: 'Education',
        title: 'Education & Qualifications',
        description: 'Academic degrees, institutions, disciplines and academic timeline.',
    },
    {
        id: 'projects',
        number: '05',
        tabLabel: '05 Projects',
        shortName: 'Projects',
        title: 'Featured Projects & Portfolio',
        description: 'Technical projects, implementation stacks and project highlights.',
    },
    {
        id: 'achievements',
        number: '06',
        tabLabel: '06 Achievements',
        shortName: 'Achievements',
        title: 'Certifications & Achievements',
        description: 'Professional credentials, awards, milestones and certifications.',
    },
]

export default function ResumeAnalyzer() {
    const { fileId: globalFileId, setResumeFileId, clearResume: clearGlobalResume } = useCandidate()

    // File and workflow state
    const [file, setFile] = useState(null)
    const [fileId, setFileId] = useState(globalFileId)
    const [uploadProgress, setUploadProgress] = useState(0)

    // Status: 'idle' | 'uploading' | 'parsing' | 'parsed' | 'upload_error' | 'parse_error'
    const [status, setStatus] = useState('idle')
    const [errorMessage, setErrorMessage] = useState('')

    // Candidate data
    const [originalCandidate, setOriginalCandidate] = useState(null)
    const [candidate, setCandidate] = useState(null)
    const [isEdited, setIsEdited] = useState(false)
    const [isEditorOpen, setIsEditorOpen] = useState(false)

    // Mobile section pagination state (< 450px)
    const [currentSection, setCurrentSection] = useState(0)
    const [visitedSections, setVisitedSections] = useState(() => new Set([0]))
    const tabsRef = useRef(null)

    // Auto-scroll active tab into center view on mobile selector
    useEffect(() => {
        if (tabsRef.current) {
            const activeTabEl = tabsRef.current.querySelector(`[data-section-idx="${currentSection}"]`)
            if (activeTabEl && typeof activeTabEl.scrollIntoView === 'function') {
                activeTabEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
            }
        }
    }, [currentSection])

    const scrollToTop = useCallback(() => {
        const dashboardContent = document.querySelector('.dashboard-content')
        if (dashboardContent) {
            dashboardContent.scrollTo({ top: 0, behavior: 'smooth' })
        }
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }, [])

    const handleSelectSection = useCallback((idx) => {
        if (idx >= 0 && idx < RESUME_SECTIONS.length) {
            setCurrentSection(idx)
            setVisitedSections((prev) => new Set([...prev, idx]))
            setTimeout(scrollToTop, 50)
        }
    }, [scrollToTop])

    // Execute parsing given a valid file ID
    const executeParsing = useCallback(async (targetFileId) => {
        setStatus('parsing')
        setErrorMessage('')

        try {
            const parseRes = await parseResume(targetFileId)

            if (!parseRes?.candidate) {
                throw new Error('Parsing succeeded but candidate profile was missing.')
            }

            setFileId(targetFileId)
            setResumeFileId(targetFileId)
            setOriginalCandidate(parseRes.candidate)
            setCandidate(parseRes.candidate)
            setIsEdited(false)
            setCurrentSection(0)
            setVisitedSections(new Set([0]))
            setStatus('parsed')
        } catch (err) {
            setStatus('parse_error')
            const detailMsg =
                err.userMessage ||
                err.response?.data?.detail ||
                'Unable to parse resume information. The document text could not be processed.'
            setErrorMessage(detailMsg)

            if (err.response?.status === 404) {
                clearGlobalResume()
                setFileId(null)
            }
        }
    }, [clearGlobalResume, setResumeFileId])

    // Restore candidate profile on initial mount if a validated session fileId exists
    useEffect(() => {
        let isMounted = true

        if (globalFileId && !candidate && status === 'idle') {
            parseResume(globalFileId)
                .then((parseRes) => {
                    if (isMounted && parseRes?.candidate) {
                        setFileId(globalFileId)
                        setResumeFileId(globalFileId)
                        setOriginalCandidate(parseRes.candidate)
                        setCandidate(parseRes.candidate)
                        setCurrentSection(0)
                        setVisitedSections(new Set([0]))
                        setStatus('parsed')
                    }
                })
                .catch((err) => {
                    if (isMounted) {
                        setStatus('parse_error')
                        setErrorMessage(
                            err.userMessage ||
                            err.response?.data?.detail ||
                            'Unable to restore resume session.'
                        )
                        if (err.response?.status === 404) {
                            clearGlobalResume()
                            setFileId(null)
                        }
                    }
                })
        }

        return () => {
            isMounted = false
        }
    }, [globalFileId, candidate, status, clearGlobalResume, setResumeFileId])

    // Handle file selection from uploader
    function handleFileSelected(selectedFile) {
        setFile(selectedFile)
        setStatus('file_selected')
        setErrorMessage('')
    }

    // Clear file selection
    function handleClearFile() {
        setFile(null)
        setFileId(null)
        clearGlobalResume()
        setStatus('idle')
        setErrorMessage('')
        setUploadProgress(0)
        setCurrentSection(0)
        setVisitedSections(new Set([0]))
    }

    // Main upload & parse pipeline
    async function handleUploadAndAnalyze() {
        if (!file || status === 'uploading' || status === 'parsing') return

        setStatus('uploading')
        setErrorMessage('')
        setUploadProgress(0)

        let currentFileId = fileId

        // Step 1: Upload (if not already uploaded)
        if (!currentFileId) {
            try {
                const uploadRes = await uploadResume(file, (percent) => {
                    setUploadProgress(percent)
                })

                if (!uploadRes?.file_id) {
                    throw new Error('Upload succeeded but no file ID was returned.')
                }

                currentFileId = uploadRes.file_id
                setFileId(currentFileId)
                setResumeFileId(currentFileId)
                setUploadProgress(100)
            } catch (err) {
                setStatus('upload_error')
                setErrorMessage(
                    err.userMessage ||
                    err.response?.data?.detail ||
                    'Failed to upload resume. Please check the file and try again.'
                )
                return
            }
        }

        // Step 2: Parse candidate information
        await executeParsing(currentFileId)
    }

    // Retry parsing without re-uploading the file
    function handleRetryParsing() {
        if (fileId) {
            executeParsing(fileId)
        } else {
            handleUploadAndAnalyze()
        }
    }

    // Reset workflow to upload a fresh resume
    function handleUploadAnother() {
        setFile(null)
        setFileId(null)
        clearGlobalResume()
        setOriginalCandidate(null)
        setCandidate(null)
        setIsEdited(false)
        setStatus('idle')
        setErrorMessage('')
        setUploadProgress(0)
        setCurrentSection(0)
        setVisitedSections(new Set([0]))
    }

    // Save profile modifications locally
    function handleSaveEditedProfile(updatedCandidate) {
        setCandidate(updatedCandidate)
        setIsEdited(true)
        setIsEditorOpen(false)
    }

    // Restore to extracted profile
    function handleResetToExtracted() {
        if (originalCandidate) {
            setCandidate(originalCandidate)
            setIsEdited(false)
            setIsEditorOpen(false)
        }
    }

    return (
        <div className="mx-auto w-full max-w-6xl space-y-6 sm:space-y-8">
            {/* Page Header */}
            <div>
                <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--accent)]">
                    <Sparkles size={16} />
                    <span>Career Intelligence Engine</span>
                </div>

                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <h1 className="text-2xl font-extrabold tracking-tight text-[var(--text-primary)] sm:text-3xl md:text-4xl">
                            Resume Intelligence Dashboard
                        </h1>
                        <p className="mt-1 text-xs sm:text-sm text-[var(--text-secondary)]">
                            AI-driven resume parsing, technical competency taxonomy, and career milestones.
                        </p>
                    </div>

                    {status === 'parsed' && (
                        <div className="flex flex-wrap items-center gap-2.5">
                            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-400">
                                <FileCheck2 size={14} />
                                <span>Analysis Complete</span>
                            </span>

                            <Link
                                to="/jobs"
                                className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-3.5 py-1.5 text-xs font-semibold text-white shadow-md shadow-indigo-500/20 transition-all hover:opacity-95 hover:shadow-lg"
                            >
                                <BriefcaseBusiness size={14} />
                                <span>Match with Job</span>
                                <ArrowRight size={13} />
                            </Link>
                        </div>
                    )}
                </div>
            </div>

            {/* Error Banner with Retry */}
            {(status === 'upload_error' || status === 'parse_error') && errorMessage && (
                <div className="rounded-2xl border border-red-500/25 bg-red-500/10 p-5 shadow-sm">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex items-start gap-3">
                            <AlertCircle size={22} className="mt-0.5 shrink-0 text-red-500" />
                            <div>
                                <h3 className="text-sm font-bold text-red-400">
                                    {status === 'upload_error' ? 'Resume Upload Failed' : 'Resume Parsing Failed'}
                                </h3>
                                <p className="mt-1 text-xs text-red-300 leading-relaxed">
                                    {errorMessage}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2 self-end sm:self-center">
                            {status === 'parse_error' && fileId && (
                                <button
                                    type="button"
                                    onClick={handleRetryParsing}
                                    className="inline-flex items-center gap-1.5 rounded-xl bg-red-500/20 px-3.5 py-2 text-xs font-semibold text-red-200 transition-all hover:bg-red-500/30"
                                >
                                    <RefreshCw size={14} />
                                    <span>Retry Analysis</span>
                                </button>
                            )}
                            <button
                                type="button"
                                onClick={handleUploadAnother}
                                className="rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2 text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]"
                            >
                                Start Over
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Stage 1: File Upload (Idle, Selected, or Upload Error) */}
            {(status === 'idle' || status === 'file_selected' || status === 'upload_error' || status === 'uploading') && (
                <>
                    <ResumeUpload
                        selectedFile={file}
                        isUploading={status === 'uploading'}
                        uploadProgress={uploadProgress}
                        error={status === 'upload_error' ? errorMessage : ''}
                        onFileSelected={handleFileSelected}
                        onUpload={handleUploadAndAnalyze}
                        onClearFile={handleClearFile}
                    />

                    {/* Privacy & Engine Assurance Card */}
                    <div className="flex items-start gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-5">
                        <ShieldCheck size={22} className="mt-0.5 shrink-0 text-[var(--success)]" />
                        <div>
                            <h4 className="text-sm font-semibold text-[var(--text-primary)]">
                                Automated Validation & Privacy Protection
                            </h4>
                            <p className="mt-1 text-xs text-[var(--text-secondary)] leading-relaxed">
                                CareerMind AI analyzes your PDF securely in local environment.
                                Supports files up to 5 MB with strict file ID validation and zero third-party data transmission.
                            </p>
                        </div>
                    </div>
                </>
            )}

            {/* Stage 2: Processing State */}
            {status === 'parsing' && (
                <ResumeProcessing step="parsing" />
            )}

            {/* Stage 3: Full Resume Intelligence Dashboard */}
            {status === 'parsed' && candidate && (
                <div className="space-y-6 sm:space-y-8 animate-fadeIn">
                    {/* MOBILE-ONLY SECTION SELECTOR (< 450px) */}
                    <div
                        className="mobile-resume-nav-tabs"
                        ref={tabsRef}
                        role="tablist"
                        aria-label="Resume sections navigation"
                    >
                        {RESUME_SECTIONS.map((sec, idx) => {
                            const isActive = currentSection === idx
                            const isVisited = visitedSections.has(idx)

                            return (
                                <button
                                    key={sec.id}
                                    type="button"
                                    role="tab"
                                    aria-selected={isActive}
                                    data-section-idx={idx}
                                    onClick={() => handleSelectSection(idx)}
                                    className={`mobile-resume-tab-btn ${isActive ? 'active' : ''} ${isVisited && !isActive ? 'visited' : ''}`}
                                    aria-label={`Go to section ${sec.number}: ${sec.shortName}`}
                                >
                                    {isVisited && !isActive && (
                                        <Check size={11} className="text-emerald-500 dark:text-emerald-400 shrink-0" strokeWidth={3} />
                                    )}
                                    <span>{sec.tabLabel}</span>
                                </button>
                            )
                        })}
                    </div>

                    {/* MOBILE-ONLY SECTION BANNER (< 450px) */}
                    <div className="mobile-resume-section-banner">
                        <div className="flex items-center justify-between gap-2 mb-2">
                            <span className="section-badge">
                                SECTION {RESUME_SECTIONS[currentSection].number} / 06
                            </span>
                            <span className="section-progress-text">
                                {Math.round(((currentSection + 1) / RESUME_SECTIONS.length) * 100)}% Complete
                            </span>
                        </div>

                        {/* Visual Progress Bar */}
                        <div className="section-progress-track">
                            <div
                                className="section-progress-fill"
                                style={{ width: `${((currentSection + 1) / RESUME_SECTIONS.length) * 100}%` }}
                            />
                        </div>

                        <h2 className="section-title">
                            {RESUME_SECTIONS[currentSection].title}
                        </h2>
                        <p className="section-desc">
                            {RESUME_SECTIONS[currentSection].description}
                        </p>
                    </div>

                    {/* 01 — Profile (Candidate Profile Overview & Professional Summary) */}
                    <div className={`resume-section-item ${currentSection === 0 ? 'active-mobile-section' : ''} space-y-6 sm:space-y-8`}>
                        <CandidateProfile
                            personalInfo={candidate.personal_information}
                            fileId={fileId}
                            isEdited={isEdited}
                            onEdit={() => setIsEditorOpen(true)}
                            onUploadAnother={handleUploadAnother}
                        />
                        <ProfessionalSummary
                            summary={candidate.professional_summary}
                        />
                    </div>

                    {/* 02 — Skills (Technical Skills Categorization Dashboard) */}
                    <div className={`resume-section-item ${currentSection === 1 ? 'active-mobile-section' : ''}`}>
                        <SkillsOverview
                            skills={candidate.technical_skills}
                        />
                    </div>

                    {/* 03 — Experience (Work Experience Timeline) */}
                    <div className={`resume-section-item ${currentSection === 2 ? 'active-mobile-section' : ''}`}>
                        <ExperienceTimeline
                            experience={candidate.experience}
                        />
                    </div>

                    {/* 04 — Education (Education Credentials Timeline) */}
                    <div className={`resume-section-item ${currentSection === 3 ? 'active-mobile-section' : ''}`}>
                        <EducationTimeline
                            education={candidate.education}
                        />
                    </div>

                    {/* 05 — Projects (Featured Projects Portfolio) */}
                    <div className={`resume-section-item ${currentSection === 4 ? 'active-mobile-section' : ''}`}>
                        <ProjectsSection
                            projects={candidate.projects}
                        />
                    </div>

                    {/* 06 — Achievements (Certifications & Achievements) */}
                    <div className={`resume-section-item ${currentSection === 5 ? 'active-mobile-section' : ''}`}>
                        <CertificationsSection
                            certifications={candidate.certifications}
                            achievements={candidate.achievements}
                        />
                    </div>

                    {/* MOBILE-ONLY PREVIOUS / NEXT FOOTER CONTROLS (< 450px) */}
                    <div className="mobile-resume-pagination-footer">
                        <button
                            type="button"
                            onClick={() => handleSelectSection(currentSection - 1)}
                            disabled={currentSection === 0}
                            className="mobile-page-btn prev-btn"
                            aria-label="Previous section"
                        >
                            <ChevronLeft size={16} />
                            <span>Previous</span>
                        </button>

                        <div className="mobile-page-indicator">
                            <span>{RESUME_SECTIONS[currentSection].number}</span>
                            <span className="text-[var(--text-muted)] font-normal">/</span>
                            <span>06</span>
                        </div>

                        {currentSection < RESUME_SECTIONS.length - 1 ? (
                            <button
                                type="button"
                                onClick={() => handleSelectSection(currentSection + 1)}
                                className="mobile-page-btn next-btn"
                                aria-label="Next section"
                            >
                                <span>Next</span>
                                <ChevronRight size={16} />
                            </button>
                        ) : (
                            <button
                                type="button"
                                onClick={() => handleSelectSection(0)}
                                className="mobile-page-btn finish-btn"
                                aria-label="Finish and return to profile overview"
                            >
                                <CheckCircle2 size={16} />
                                <span>Finish</span>
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Profile Editor Modal */}
            {isEditorOpen && candidate && (
                <ProfileEditor
                    candidate={candidate}
                    onSave={handleSaveEditedProfile}
                    onClose={() => setIsEditorOpen(false)}
                    onResetToOriginal={handleResetToExtracted}
                />
            )}
        </div>
    )
}
