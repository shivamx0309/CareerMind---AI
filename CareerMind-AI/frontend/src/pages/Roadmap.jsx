import { useState, useEffect, useCallback } from 'react'
import {
    Calendar,
    Layers,
    AlertCircle,
    RefreshCw,
    LayoutList,
} from 'lucide-react'

import {
    getRoadmaps,
    getRoadmapById,
    generateRoadmap,
    deleteRoadmap,
    updateTopicStatus,
    updateSkillStatus,
    updateMilestoneStatus,
    getRoadmapProgress,
} from '../services/learningService'
import { getResumeLibrary } from '../services/skillGapService'

import RoadmapHeader from '../components/roadmap/RoadmapHeader'
import RoadmapOverviewCards from '../components/roadmap/RoadmapOverviewCards'
import RoadmapProgressVisual from '../components/roadmap/RoadmapProgressVisual'
import WeeklyTimeline from '../components/roadmap/WeeklyTimeline'
import SkillModulesList from '../components/roadmap/SkillModulesList'
import RoadmapGeneratorModal from '../components/roadmap/RoadmapGeneratorModal'
import RoadmapPreferencesModal from '../components/roadmap/RoadmapPreferencesModal'
import RoadmapHistoryModal from '../components/roadmap/RoadmapHistoryModal'
import RoadmapEmptyState from '../components/roadmap/RoadmapEmptyState'

export default function Roadmap() {
    // Roadmaps State
    const [allRoadmaps, setAllRoadmaps] = useState([])
    const [activeRoadmap, setActiveRoadmap] = useState(null)
    const [progressData, setProgressData] = useState(null)
    const [resumes, setResumes] = useState([])

    // Loading & Error States
    const [isLoadingInitial, setIsLoadingInitial] = useState(true)
    const [errorMessage, setErrorMessage] = useState(null)
    const [isGenerating, setIsGenerating] = useState(false)
    const [updatingTopicId, setUpdatingTopicId] = useState(null)
    const [updatingSkillId, setUpdatingSkillId] = useState(null)
    const [updatingMilestoneId, setUpdatingMilestoneId] = useState(null)

    // Modals
    const [isGeneratorOpen, setIsGeneratorOpen] = useState(false)
    const [isPreferencesOpen, setIsPreferencesOpen] = useState(false)
    const [isHistoryOpen, setIsHistoryOpen] = useState(false)

    // View Mode: 'all' | 'timeline' | 'skills'
    const [activeViewMode, setActiveViewMode] = useState('all')

    // Fetch Full Details & Telemetry for a selected roadmap ID
    const loadRoadmapDetails = useCallback(async (roadmapId) => {
        try {
            const [detail, prog] = await Promise.all([
                getRoadmapById(roadmapId),
                getRoadmapProgress(roadmapId).catch((err) => {
                    console.error('Failed to load progress telemetry:', err)
                    return null
                }),
            ])
            setActiveRoadmap(detail)
            setProgressData(prog)
        } catch (err) {
            console.error('Failed to load roadmap details:', err)
            setErrorMessage('Unable to load full details for the selected roadmap.')
        }
    }, [])

    // Initial Dashboard Bootstrap
    useEffect(() => {
        let isMounted = true

        async function initRoadmapPage() {
            setIsLoadingInitial(true)
            setErrorMessage(null)
            try {
                const [roadmapsData, resumesData] = await Promise.all([
                    getRoadmaps().catch((err) => {
                        console.error('Failed to load roadmaps:', err)
                        return []
                    }),
                    getResumeLibrary().catch((err) => {
                        console.error('Failed to load resumes:', err)
                        return []
                    }),
                ])

                if (!isMounted) return

                setAllRoadmaps(roadmapsData || [])
                setResumes(resumesData || [])

                // Auto-load first roadmap if available
                if (roadmapsData && roadmapsData.length > 0) {
                    await loadRoadmapDetails(roadmapsData[0].id)
                }
            } catch (err) {
                if (!isMounted) return
                console.error('Failed to initialize roadmap dashboard:', err)
                setErrorMessage('Failed to initialize roadmap dashboard. Please check backend status.')
            } finally {
                if (isMounted) setIsLoadingInitial(false)
            }
        }

        initRoadmapPage()

        return () => {
            isMounted = false
        }
    }, [loadRoadmapDetails])

    // Generate Roadmap Handler
    const handleGenerateRoadmap = async (payload) => {
        setIsGenerating(true)
        try {
            const generated = await generateRoadmap(payload)
            // Refresh summaries list
            const updatedSummaries = await getRoadmaps()
            setAllRoadmaps(updatedSummaries)

            // Set newly generated roadmap as active
            setActiveRoadmap(generated)
            const prog = await getRoadmapProgress(generated.id).catch(() => null)
            setProgressData(prog)
            return generated
        } finally {
            setIsGenerating(false)
        }
    }

    // Delete Roadmap Handler
    const handleDeleteRoadmap = async (roadmapId) => {
        await deleteRoadmap(roadmapId)
        const updatedSummaries = await getRoadmaps()
        setAllRoadmaps(updatedSummaries)

        // If active roadmap was deleted, switch to next or null
        if (activeRoadmap?.id === roadmapId) {
            if (updatedSummaries.length > 0) {
                await loadRoadmapDetails(updatedSummaries[0].id)
            } else {
                setActiveRoadmap(null)
                setProgressData(null)
            }
        }
    }

    // Update Topic Status Handler
    const handleUpdateTopicStatus = async (topicId, status) => {
        if (!activeRoadmap) return
        setUpdatingTopicId(topicId)
        try {
            await updateTopicStatus(activeRoadmap.id, topicId, status)
            // Refresh roadmap and telemetry
            const [refreshed, prog] = await Promise.all([
                getRoadmapById(activeRoadmap.id),
                getRoadmapProgress(activeRoadmap.id).catch(() => null),
            ])
            setActiveRoadmap(refreshed)
            setProgressData(prog)
        } finally {
            setUpdatingTopicId(null)
        }
    }

    // Update Skill Status Handler (cascades to all child topics)
    const handleUpdateSkillStatus = async (skillId, status) => {
        if (!activeRoadmap) return
        setUpdatingSkillId(skillId)
        try {
            await updateSkillStatus(activeRoadmap.id, skillId, status)
            const [refreshed, prog] = await Promise.all([
                getRoadmapById(activeRoadmap.id),
                getRoadmapProgress(activeRoadmap.id).catch(() => null),
            ])
            setActiveRoadmap(refreshed)
            setProgressData(prog)
        } finally {
            setUpdatingSkillId(null)
        }
    }

    // Update Milestone Status Handler
    const handleUpdateMilestoneStatus = async (milestoneId, status) => {
        if (!activeRoadmap) return
        setUpdatingMilestoneId(milestoneId)
        try {
            await updateMilestoneStatus(activeRoadmap.id, milestoneId, status)
            const refreshed = await getRoadmapById(activeRoadmap.id)
            setActiveRoadmap(refreshed)
        } finally {
            setUpdatingMilestoneId(null)
        }
    }

    // Resolve resume display name
    const activeResume = resumes.find((r) => r.id === activeRoadmap?.resume_record_id)
    const resumeDisplayName = activeResume?.display_name || activeResume?.original_filename || 'Active Candidate Resume'

    return (
        <div className="space-y-6 pb-12">
            {/* Top Header */}
            <RoadmapHeader
                activeRoadmap={activeRoadmap}
                allRoadmaps={allRoadmaps}
                onSelectRoadmap={loadRoadmapDetails}
                onOpenGenerator={() => setIsGeneratorOpen(true)}
                onOpenPreferences={() => setIsPreferencesOpen(true)}
                onOpenHistory={() => setIsHistoryOpen(true)}
            />

            {/* Error Banner */}
            {errorMessage && (
                <div className="flex items-center justify-between rounded-2xl border border-rose-500/20 bg-rose-500/10 p-4 text-xs text-rose-600 dark:text-rose-400">
                    <div className="flex items-center gap-2.5">
                        <AlertCircle size={18} className="shrink-0" />
                        <span>{errorMessage}</span>
                    </div>
                    <button
                        type="button"
                        onClick={() => {
                            if (activeRoadmap) loadRoadmapDetails(activeRoadmap.id)
                            else window.location.reload()
                        }}
                        className="inline-flex items-center gap-1 rounded-xl bg-rose-500/20 px-3 py-1 font-bold hover:bg-rose-500/30 transition-all cursor-pointer"
                    >
                        <RefreshCw size={12} />
                        Retry
                    </button>
                </div>
            )}

            {/* Initial Loading Skeleton */}
            {isLoadingInitial ? (
                <div className="space-y-6">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-32 rounded-2xl border border-[var(--border)] bg-[var(--surface-card)] animate-pulse" />
                        ))}
                    </div>
                    <div className="h-64 rounded-2xl border border-[var(--border)] bg-[var(--surface-card)] animate-pulse" />
                </div>
            ) : !activeRoadmap ? (
                /* Empty State */
                <RoadmapEmptyState onOpenGenerator={() => setIsGeneratorOpen(true)} />
            ) : (
                /* Active Roadmap Content */
                <div className="space-y-7">
                    {/* 1. Metrics & Overview Cards */}
                    <RoadmapOverviewCards
                        roadmap={activeRoadmap}
                        progress={progressData}
                        resumeName={resumeDisplayName}
                    />

                    {/* 2. Visual Distribution Chart */}
                    <RoadmapProgressVisual
                        skills={activeRoadmap.skills || []}
                        progressPct={progressData?.progress_percentage ?? activeRoadmap.progress_percentage ?? 0}
                    />

                    {/* 3. View Mode Switcher */}
                    <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={() => setActiveViewMode('all')}
                                className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                                    activeViewMode === 'all'
                                        ? 'bg-[var(--primary-purple)] text-white shadow-sm'
                                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)]'
                                }`}
                            >
                                <LayoutList size={14} />
                                Full Roadmap View
                            </button>
                            <button
                                type="button"
                                onClick={() => setActiveViewMode('timeline')}
                                className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                                    activeViewMode === 'timeline'
                                        ? 'bg-[var(--primary-purple)] text-white shadow-sm'
                                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)]'
                                }`}
                            >
                                <Calendar size={14} />
                                Weekly Schedule ({activeRoadmap.total_weeks}w)
                            </button>
                            <button
                                type="button"
                                onClick={() => setActiveViewMode('skills')}
                                className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                                    activeViewMode === 'skills'
                                        ? 'bg-[var(--primary-purple)] text-white shadow-sm'
                                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)]'
                                }`}
                            >
                                <Layers size={14} />
                                Skill Modules ({activeRoadmap.skills?.length || 0})
                            </button>
                        </div>
                    </div>

                    {/* 4. Weekly Timeline Section */}
                    {(activeViewMode === 'all' || activeViewMode === 'timeline') && (
                        <WeeklyTimeline
                            milestones={activeRoadmap.milestones || []}
                            weeklySchedule={activeRoadmap.weekly_schedule || []}
                            roadmapId={activeRoadmap.id}
                            currentWeek={progressData?.current_week || 1}
                            onUpdateMilestoneStatus={handleUpdateMilestoneStatus}
                            updatingMilestoneId={updatingMilestoneId}
                        />
                    )}

                    {/* 5. Skill Modules & Topics Section */}
                    {(activeViewMode === 'all' || activeViewMode === 'skills') && (
                        <SkillModulesList
                            skills={activeRoadmap.skills || []}
                            roadmapId={activeRoadmap.id}
                            onUpdateTopicStatus={handleUpdateTopicStatus}
                            onUpdateSkillStatus={handleUpdateSkillStatus}
                            updatingTopicId={updatingTopicId}
                            updatingSkillId={updatingSkillId}
                        />
                    )}
                </div>
            )}

            {/* Generator Modal */}
            <RoadmapGeneratorModal
                isOpen={isGeneratorOpen}
                onClose={() => setIsGeneratorOpen(false)}
                onGenerate={handleGenerateRoadmap}
                defaultWeeklyHours={activeRoadmap?.weekly_study_hours || 10}
                isGenerating={isGenerating}
            />

            {/* Preferences Modal */}
            <RoadmapPreferencesModal
                isOpen={isPreferencesOpen}
                onClose={() => setIsPreferencesOpen(false)}
                onSaved={() => {
                    // If active roadmap exists, optionally re-fetch or notify
                }}
            />

            {/* History Modal */}
            <RoadmapHistoryModal
                isOpen={isHistoryOpen}
                onClose={() => setIsHistoryOpen(false)}
                roadmaps={allRoadmaps}
                activeRoadmapId={activeRoadmap?.id}
                onSelectRoadmap={loadRoadmapDetails}
                onDeleteRoadmap={handleDeleteRoadmap}
                onOpenGenerator={() => setIsGeneratorOpen(true)}
            />
        </div>
    )
}
