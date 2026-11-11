import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function RoadmapPagination({
    currentPage = 1,
    totalPages = 1,
    totalItems = 0,
    itemsPerPage = 3,
    onPageChange,
    itemName = 'items',
    className = '',
}) {
    if (totalPages <= 1) return null

    const startItem = (currentPage - 1) * itemsPerPage + 1
    const endItem = Math.min(currentPage * itemsPerPage, totalItems)

    // Generate smart page window (e.g., [1, 2, 3, 4])
    const pages = []
    for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
    }

    return (
        <nav
            aria-label={`Pagination for ${itemName}`}
            className={`flex flex-col sm:flex-row items-center justify-between gap-3 pt-5 pb-2 border-t border-[var(--border)] ${className}`}
        >
            <div className="text-xs text-[var(--text-secondary)] font-medium text-center sm:text-left">
                Showing{' '}
                <strong className="text-[var(--text-primary)] font-bold">
                    {startItem}–{endItem}
                </strong>{' '}
                of{' '}
                <strong className="text-[var(--text-primary)] font-bold">
                    {totalItems}
                </strong>{' '}
                {itemName}
            </div>

            <div className="flex items-center gap-1.5">
                {/* Previous Button */}
                <button
                    type="button"
                    onClick={() => onPageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    aria-label="Previous page"
                    className="inline-flex items-center gap-1 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-1.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-xs"
                >
                    <ChevronLeft size={14} />
                    <span>Prev</span>
                </button>

                {/* Page Number Buttons */}
                <div className="flex items-center gap-1">
                    {pages.map((pageNum) => {
                        const isActive = pageNum === currentPage
                        return (
                            <button
                                key={pageNum}
                                type="button"
                                onClick={() => onPageChange(pageNum)}
                                aria-current={isActive ? 'page' : undefined}
                                className={`flex h-8 w-8 items-center justify-center rounded-xl text-xs font-bold transition-all cursor-pointer ${
                                    isActive
                                        ? 'bg-[var(--accent)] text-white shadow-md shadow-purple-600/25 scale-105'
                                        : 'border border-[var(--border)] bg-[var(--surface-solid)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)]'
                                }`}
                            >
                                {pageNum}
                            </button>
                        )
                    })}
                </div>

                {/* Next Button */}
                <button
                    type="button"
                    onClick={() => onPageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    aria-label="Next page"
                    className="inline-flex items-center gap-1 rounded-xl border border-[var(--border)] bg-[var(--surface-solid)] px-3 py-1.5 text-xs font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent)] hover:bg-[var(--surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shadow-xs"
                >
                    <span>Next</span>
                    <ChevronRight size={14} />
                </button>
            </div>
        </nav>
    )
}

