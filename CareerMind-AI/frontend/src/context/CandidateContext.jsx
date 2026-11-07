/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react'

const CandidateContext = createContext(null)

const SESSION_STORAGE_KEY = 'careermind_resume_file_id'
const HEX_UUID_REGEX = /^[0-9a-f]{32}$/i

/**
 * Validate that a file ID strictly conforms to a 32-character hexadecimal UUID.
 *
 * @param {string} id - Raw file ID.
 * @returns {boolean} True if format is valid.
 */
function isValidFileId(id) {
    if (!id || typeof id !== 'string') return false
    return HEX_UUID_REGEX.test(id.trim())
}

/**
 * Provider that manages the candidate resume file_id lifecycle.
 *
 * Persists ONLY the validated 32-character hexadecimal resume file_id in sessionStorage.
 * Never stores candidate personal information, contact info, raw text, or full profiles.
 */
export function CandidateProvider({ children }) {
    const [fileId, setFileIdState] = useState(() => {
        try {
            const stored = sessionStorage.getItem(SESSION_STORAGE_KEY)
            if (stored && isValidFileId(stored)) {
                return stored.trim().toLowerCase()
            }
            if (stored) {
                // Remove malformed or corrupted entry safely
                sessionStorage.removeItem(SESSION_STORAGE_KEY)
            }
        } catch {
            // Guard against disabled or restricted sessionStorage
        }
        return null
    })

    // Sync state to sessionStorage whenever fileId changes
    useEffect(() => {
        try {
            if (fileId && isValidFileId(fileId)) {
                sessionStorage.setItem(SESSION_STORAGE_KEY, fileId)
            } else {
                sessionStorage.removeItem(SESSION_STORAGE_KEY)
            }
        } catch {
            // Ignore storage access errors
        }
    }, [fileId])

    /**
     * Store a validated resume file_id.
     *
     * @param {string} newId - 32-character hexadecimal UUID.
     */
    const setResumeFileId = useCallback((newId) => {
        if (!newId) {
            setFileIdState(null)
            return
        }

        const cleaned = String(newId).trim().toLowerCase()
        if (isValidFileId(cleaned)) {
            setFileIdState(cleaned)
        } else {
            console.warn(`[CandidateContext] Invalid file_id format rejected: "${newId}"`)
            setFileIdState(null)
        }
    }, [])

    /**
     * Safely clear the active resume file_id from both state and sessionStorage.
     */
    const clearResume = useCallback(() => {
        try {
            sessionStorage.removeItem(SESSION_STORAGE_KEY)
        } catch {
            // Ignore storage errors
        }
        setFileIdState(null)
    }, [])

    const value = useMemo(
        () => ({
            fileId,
            hasResume: Boolean(fileId),
            setResumeFileId,
            clearResume,
        }),
        [fileId, setResumeFileId, clearResume]
    )

    return (
        <CandidateContext.Provider value={value}>
            {children}
        </CandidateContext.Provider>
    )
}

/**
 * Custom hook to access the CandidateContext.
 *
 * @returns {{
 *   fileId: string | null,
 *   hasResume: boolean,
 *   setResumeFileId: (id: string) => void,
 *   clearResume: () => void
 * }}
 */
export function useCandidate() {
    const context = useContext(CandidateContext)
    if (!context) {
        throw new Error('useCandidate must be used within a CandidateProvider')
    }
    return context
}
