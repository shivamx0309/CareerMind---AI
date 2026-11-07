import { useRef, useState } from 'react'
import {
    Upload,
    FileText,
    AlertCircle,
    LoaderCircle,
    X,
    FileCheck,
} from 'lucide-react'

const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5 MB

export default function ResumeUpload({
    onFileSelected,
    onUpload,
    selectedFile,
    isUploading,
    uploadProgress,
    error,
    onClearFile,
}) {
    const fileInputRef = useRef(null)
    const [isDragging, setIsDragging] = useState(false)
    const [clientError, setClientError] = useState('')

    function validateFile(file) {
        if (!file) return 'Please select a PDF file.'
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            return 'Only PDF files are supported. Please select a .pdf file.'
        }
        if (file.type && file.type !== 'application/pdf') {
            return 'Invalid file type. Please upload a standard PDF.'
        }
        if (file.size === 0) {
            return 'The selected file is empty (0 bytes).'
        }
        if (file.size > MAX_FILE_SIZE) {
            return 'File size exceeds the 5 MB limit. Please select a smaller PDF.'
        }
        return ''
    }

    function handleFile(file) {
        setClientError('')
        const validationError = validateFile(file)
        if (validationError) {
            setClientError(validationError)
            return
        }
        onFileSelected(file)
    }

    function handleDrop(event) {
        event.preventDefault()
        setIsDragging(false)
        if (isUploading) return

        const file = event.dataTransfer.files?.[0]
        if (file) {
            handleFile(file)
        }
    }

    function handleDragOver(event) {
        event.preventDefault()
        if (!isUploading) {
            setIsDragging(true)
        }
    }

    function handleDragLeave() {
        setIsDragging(false)
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} B`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
        return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
    }

    const activeError = clientError || error

    return (
        <div className="glass-card p-6 sm:p-8">
            <div className="mb-6">
                <h2 className="text-xl font-bold text-[var(--text-primary)]">
                    Upload your resume
                </h2>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                    Upload your PDF resume to extract skills, work experience, education, and career insights.
                </p>
            </div>

            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                className="hidden"
                disabled={isUploading}
                onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) handleFile(file)
                }}
            />

            {!selectedFile ? (
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition-all sm:p-12 ${
                        isDragging
                            ? 'border-[var(--accent)] bg-[var(--accent-soft)]'
                            : 'border-[var(--border)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)]'
                    }`}
                >
                    <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--accent-soft)] text-[var(--accent)]">
                        <Upload size={30} />
                    </div>

                    <h3 className="text-base font-semibold text-[var(--text-primary)]">
                        Drag and drop your resume here
                    </h3>

                    <p className="mt-2 text-sm text-[var(--text-secondary)]">
                        or click to browse documents from your device
                    </p>

                    <span className="mt-5 inline-flex rounded-xl bg-[var(--accent)] px-5 py-2.5 text-sm font-semibold text-white shadow-md transition-all hover:opacity-90">
                        Choose PDF Resume
                    </span>

                    <p className="mt-4 text-xs text-[var(--text-muted)]">
                        Standard PDF only • Maximum file size: 5 MB
                    </p>
                </div>
            ) : (
                <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-solid)] p-4 sm:p-5">
                    <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
                            <FileText size={24} />
                        </div>

                        <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-semibold text-[var(--text-primary)]">
                                {selectedFile.name}
                            </p>
                            <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
                                {formatFileSize(selectedFile.size)} • PDF Document
                            </p>
                        </div>

                        {!isUploading && (
                            <button
                                type="button"
                                onClick={() => {
                                    setClientError('')
                                    onClearFile()
                                    if (fileInputRef.current) fileInputRef.current.value = ''
                                }}
                                className="rounded-lg p-2 text-[var(--text-secondary)] transition-colors hover:bg-[var(--surface-hover)] hover:text-[var(--text-primary)]"
                                aria-label="Remove selected file"
                            >
                                <X size={20} />
                            </button>
                        )}
                    </div>

                    {isUploading && (
                        <div className="mt-4 space-y-2">
                            <div className="flex justify-between text-xs font-medium text-[var(--text-secondary)]">
                                <span>Uploading document to CareerMind AI...</span>
                                <span>{uploadProgress}%</span>
                            </div>
                            <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--surface-hover)]">
                                <div
                                    className="h-full rounded-full bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] transition-all duration-300"
                                    style={{ width: `${uploadProgress}%` }}
                                />
                            </div>
                        </div>
                    )}
                </div>
            )}

            {activeError && (
                <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-500/25 bg-red-500/10 p-4 text-sm text-red-400">
                    <AlertCircle size={20} className="mt-0.5 shrink-0 text-red-500" />
                    <p className="leading-5">{activeError}</p>
                </div>
            )}

            {selectedFile && !isUploading && (
                <button
                    type="button"
                    onClick={onUpload}
                    className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-secondary)] px-6 py-3.5 text-sm font-semibold text-white shadow-lg transition-all hover:opacity-95 hover:shadow-indigo-500/25 active:scale-[0.99]"
                >
                    <FileCheck size={18} />
                    Upload & Analyze Resume
                </button>
            )}

            {isUploading && (
                <button
                    type="button"
                    disabled
                    className="mt-6 flex w-full cursor-not-allowed items-center justify-center gap-2 rounded-xl bg-[var(--accent)] px-6 py-3.5 text-sm font-semibold text-white opacity-70"
                >
                    <LoaderCircle size={18} className="animate-spin" />
                    Uploading...
                </button>
            )}
        </div>
    )
}

