import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
    ChartNoAxesCombined,
    Sparkles,
    Loader2,
    ChevronDown,
    ChevronUp,
    ShieldCheck,
    Briefcase,
} from 'lucide-react'

import {
    getRoles,
    getResumeLibrary,
    analyzeSkills,
    getReports,
    getReportById,
    deleteReport,
} from '../services/skillGapService'

import ResumeSelector from '../components/skills/ResumeSelector'
import RoleSelector from '../components/skills/RoleSelector'
import OverallSkillScore from '../components/skills/OverallSkillScore'
import SkillCoverageCards from '../components/skills/SkillCoverageCards'
import MatchedSkillsPanel from '../components/skills/MatchedSkillsPanel'
import RelatedSkillsPanel from '../components/skills/RelatedSkillsPanel'
import MissingSkillsPanel from '../components/skills/MissingSkillsPanel'
import SkillCategoryBreakdown from '../components/skills/SkillCategoryBreakdown'
import SkillAnalysisHistory from '../components/skills/SkillAnalysisHistory'
import SkillGapEmptyState from '../components/skills/SkillGapEmptyState'
import SkillGapErrorState from '../components/skills/SkillGapErrorState'

export default function SkillGap() {
    // Initial fetch states
    const [roles, setRoles] = useState([])
    const [resumes, setResumes] = useState([])
    const [historyReports, setHistoryReports] = useState([])
    const [isLoadingInitial, setIsLoadingInitial] = useState(true)

    // Selection states
    const [selectedResumeId, setSelectedResumeId] = useState(null)
    const [selectedRoleId, setSelectedRoleId] = useState('')

    // Analysis & Active Report states
    const [activeReport, setActiveReport] = useState(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [errorMessage, setErrorMessage] = useState(null)
    const [isFormCollapsed, setIsFormCollapsed] = useState(false)

    // 1. Initial Data Fetch (Roles, Resume Library, Historical Reports)
    useEffect(() => {
        let isMounted = true

        async function initDashboard() {
            try {
                const [rolesData, resumesData, reportsData] = await Promise.all([
                    getRoles().catch((err) => {
                        console.error('Failed to load roles:', err)
                        return []
                    }),
                    getResumeLibrary().catch((err) => {
                        console.error('Failed to load resumes:', err)
                        return []
                    }),
                    getReports().catch((err) => {
                        console.error('Failed to load reports:', err)
                        return []
                    }),
                ])

                if (!isMounted) return

                setRoles(rolesData || [])
                setResumes(resumesData || [])
                setHistoryReports(reportsData || [])

                // Auto-preselect default resume if available and completed
                if (resumesData && resumesData.length > 0) {
                    const defaultResume = resumesData.find((r) => r.is_default && r.parsing_status === 'completed')
                    const firstCompleted = resumesData.find((r) => r.parsing_status === 'completed')
                    if (defaultResume) {
                        setSelectedResumeId(defaultResume.id)
                    } else if (firstCompleted) {
                        setSelectedResumeId(firstCompleted.id)
                    }
                }

                // Preselect first role if available
                if (rolesData && rolesData.length > 0) {
                    setSelectedRoleId(rolesData[0].role_id)
                }

                // If historical reports exist, automatically load the latest report as active
                if (reportsData && reportsData.length > 0) {
                    try {
                        const latestReport = await getReportById(reportsData[0].id)
                        if (isMounted) {
                            setActiveReport(latestReport)
                        }
                    } catch {
                        // Fail silently for initial load
                    }
                }
            } catch (err) {
                if (isMounted) {
                    setErrorMessage(err.userMessage || 'Failed to initialize Skill Gap dashboard.')
                }
            } finally {
                if (isMounted) {
                    setIsLoadingInitial(false)
                }
            }
        }

        initDashboard()

        return () => {
            isMounted = false
        }
    }, [])

    // 2. Execute Skill Gap Analysis
    const handleAnalyze = async () => {
        if (!selectedRoleId) {
            setErrorMessage('Please select a target role benchmark.')
            return
        }

        const selectedResume = resumes.find((r) => r.id === selectedResumeId)
        if (selectedResume && selectedResume.parsing_status !== 'completed') {
            setErrorMessage(`Resume '${selectedResume.display_name || selectedResume.original_filename}' has not been parsed yet. Please choose a parsed resume.`)
            return
        }

        setIsAnalyzing(true)
        setErrorMessage(null)

        try {
            const report = await analyzeSkills({
                target_role: selectedRoleId,
                resume_id: selectedResumeId || undefined,
            })

            setActiveReport(report)

            // Refresh historical reports list
            const updatedReports = await getReports()
            setHistoryReports(updatedReports || [])
        } catch (err) {
            setErrorMessage(err.userMessage || 'Skill Gap analysis failed. Please try again.')
        } finally {
            setIsAnalyzing(false)
        }
    }

    // 3. Open historical report
    const handleSelectHistoricalReport = async (reportId) => {
        setErrorMessage(null)
        try {
            const report = await getReportById(reportId)
            setActiveReport(report)
            // Sync selection dropdowns if matching
            if (report.target_role) {
                setSelectedRoleId(report.target_role)
            }
            if (report.resume_record_id) {
                setSelectedResumeId(report.resume_record_id)
            }
        } catch (err) {
            setErrorMessage(err.userMessage || 'Failed to retrieve selected historical report.')
        }
    }

    // 4. Delete historical report
    const handleDeleteHistoricalReport = async (reportId) => {
        try {
            await deleteReport(reportId)
            // Update list
            setHistoryReports((prev) => prev.filter((r) => r.id !== reportId))
            // If deleted report was active, reset or set to next available
            if (activeReport && activeReport.id === reportId) {
                const remaining = historyReports.filter((r) => r.id !== reportId)
                if (remaining.length > 0) {
                    const nextReport = await getReportById(remaining[0].id)
                    setActiveReport(nextReport)
                } else {
                    setActiveReport(null)
                    setIsFormCollapsed(false)
                }
            }
        } catch (err) {
            setErrorMessage(err.userMessage || 'Failed to delete report.')
        }
    }

    // Check if selection is ready to analyze
    const selectedResume = resumes.find((r) => r.id === selectedResumeId)
    const isResumeReady = selectedResume ? selectedResume.parsing_status === 'completed' : false
    const canAnalyze = Boolean(selectedRoleId && isResumeReady && !isAnalyzing)

    return (
        <div className="space-y-6 pb-12 max-w-7xl mx-auto">
            {/* Header Section */}
            <div className="glass-card rounded-2xl p-6 sm:p-8 space-y-4">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="space-y-2">
                        <div className="inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-1 text-xs font-semibold text-[var(--accent)]">
                            <ChartNoAxesCombined size={14} />
                            <span>STANDALONE CAREER INTELLIGENCE</span>
                        </div>

                        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-[var(--text-primary)]">
                            Skill Gap Analysis
                        </h1>

                        <p className="text-sm text-[var(--text-secondary)] max-w-2xl leading-relaxed">
                            Evaluate your parsed resume against standardized industry role benchmarks to uncover matched strengths, semantic affinities, and priority technical gaps without needing a job description.
                        </p>
                    </div>

                    <div className="flex items-center gap-2">
                        <Link
                            to="/jobs"
                            className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3.5 py-2 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)] transition-all"
                        >
                            <Briefcase size={14} className="text-[var(--accent)]" />
                            <span>Match with Job Description</span>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Error State Banner */}
            <SkillGapErrorState
                error={errorMessage}
                onDismiss={() => setErrorMessage(null)}
            />

            {/* Benchmark Selection Configuration Card */}
            <div className="glass-card rounded-2xl p-5 sm:p-7 space-y-5">
                <div className="flex items-center justify-between border-b border-[var(--border)]/60 pb-3">
                    <div className="flex items-center gap-2">
                        <Sparkles size={18} className="text-[var(--accent)]" />
                        <h2 className="text-base sm:text-lg font-bold text-[var(--text-primary)]">
                            Configure Skill Assessment
                        </h2>
                    </div>

                    {activeReport && (
                        <button
                            type="button"
                            onClick={() => setIsFormCollapsed(!isFormCollapsed)}
                            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors cursor-pointer"
                        >
                            <span>{isFormCollapsed ? 'Change Selection' : 'Collapse Selection'}</span>
                            {isFormCollapsed ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
                        </button>
                    )}
                </div>

                {(!activeReport || !isFormCollapsed) && (
                    <div className="space-y-6">
                        {/* 1. Resume Selector */}
                        <ResumeSelector
                            resumes={resumes}
                            selectedResumeId={selectedResumeId}
                            onSelectResume={setSelectedResumeId}
                            isLoading={isLoadingInitial}
                        />

                        {/* 2. Target Role Benchmark Selector */}
                        <RoleSelector
                            roles={roles}
                            selectedRoleId={selectedRoleId}
                            onSelectRole={setSelectedRoleId}
                            isLoading={isLoadingInitial}
                        />

                        {/* Action Bar */}
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-3 border-t border-[var(--border)]/60">
                            <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
                                <ShieldCheck size={14} className="text-[var(--success)]" />
                                <span>Deterministic evaluation against standardized curriculum taxonomy</span>
                            </div>

                            <button
                                type="button"
                                onClick={handleAnalyze}
                                disabled={!canAnalyze}
                                className={`inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-bold text-white shadow-md transition-all cursor-pointer ${
                                    canAnalyze
                                        ? 'bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] hover:opacity-95 shadow-indigo-500/20 active:scale-[0.99]'
                                        : 'bg-[var(--surface-hover)] text-[var(--text-muted)] cursor-not-allowed opacity-60'
                                }`}
                            >
                                {isAnalyzing ? (
                                    <>
                                        <Loader2 size={16} className="animate-spin" />
                                        <span>Evaluating Skill Gaps...</span>
                                    </>
                                ) : (
                                    <>
                                        <Sparkles size={16} />
                                        <span>{activeReport ? 'Re-analyze Skills' : 'Analyze Skills'}</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Active Analysis Results Dashboard */}
            {activeReport ? (
                <div className="space-y-6">
                    {/* A. Overall Score Card */}
                    <OverallSkillScore report={activeReport} />

                    {/* B. Skill Coverage Cards */}
                    <SkillCoverageCards report={activeReport} />

                    {/* C. Matched Skills Panel */}
                    <MatchedSkillsPanel matchedSkills={activeReport.matched_skills || []} />

                    {/* D. Related Skills Panel (Semantic Clusters) */}
                    <RelatedSkillsPanel relatedSkills={activeReport.related_skills || []} />

                    {/* E. Missing Skills Panel (Required & Preferred Gaps) */}
                    <MissingSkillsPanel
                        missingRequired={activeReport.missing_required_skills || []}
                        missingPreferred={activeReport.missing_preferred_skills || []}
                    />

                    {/* F. Category-wise Breakdown with Recharts */}
                    <SkillCategoryBreakdown
                        categoryBreakdown={activeReport.category_breakdown || []}
                    />
                </div>
            ) : (
                /* Empty State when no analysis has been run */
                <SkillGapEmptyState onSelectQuickRole={(roleId) => setSelectedRoleId(roleId)} />
            )}

            {/* Historical Analysis Reports */}
            <SkillAnalysisHistory
                reports={historyReports}
                onSelectReport={handleSelectHistoricalReport}
                onDeleteReport={handleDeleteHistoricalReport}
                activeReportId={activeReport?.id}
                isLoading={false}
            />
        </div>
    )
}
