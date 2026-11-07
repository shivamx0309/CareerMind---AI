import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import {
    Sparkles,
    ShieldCheck,
    AlertCircle,
    RefreshCw,
    FileCheck2,
    BriefcaseBusiness,
    ArrowRight,
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
        <div className="mx-auto w-full max-w-6xl space-y-8">
            {/* Page Header */}
            <div>
                <div className="mb-2.5 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[var(--accent)]">
                    <Sparkles size={16} />
                    <span>Career Intelligence Engine</span>
                </div>

                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <h1 className="text-3xl font-extrabold tracking-tight text-[var(--text-primary)] sm:text-4xl">
                            Resume Intelligence Dashboard
                        </h1>
                        <p className="mt-1 text-sm text-[var(--text-secondary)]">
                            AI-driven resume parsing, technical competency taxonomy, and career milestones.
                        </p>
                    </div>

                    {status === 'parsed' && (
                        <div className="flex flex-wrap items-center gap-2.5">
                            <span className="inline-flex items-center gap-1.5 rounded-full border border-[var(--success)]/30 bg-[var(--success)]/10 px-3 py-1 text-xs font-semibold text-[var(--success)]">
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
                <div className="space-y-8 animate-fadeIn">
                    {/* Candidate Profile Overview Card */}
                    <CandidateProfile
                        personalInfo={candidate.personal_information}
                        fileId={fileId}
                        isEdited={isEdited}
                        onEdit={() => setIsEditorOpen(true)}
                        onUploadAnother={handleUploadAnother}
                    />

                    {/* Professional Summary */}
                    <ProfessionalSummary
                        summary={candidate.professional_summary}
                    />

                    {/* Technical Skills Categorization Dashboard */}
                    <SkillsOverview
                        skills={candidate.technical_skills}
                    />

                    {/* Work Experience Timeline */}
                    <ExperienceTimeline
                        experience={candidate.experience}
                    />

                    {/* Education Credentials Timeline */}
                    <EducationTimeline
                        education={candidate.education}
                    />

                    {/* Featured Projects Portfolio */}
                    <ProjectsSection
                        projects={candidate.projects}
                    />

                    {/* Certifications & Achievements */}
                    <CertificationsSection
                        certifications={candidate.certifications}
                        achievements={candidate.achievements}
                    />
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
