import { CheckCircle } from 'lucide-react'

export default function RoleSelector({
    roles = [],
    selectedRoleId,
    onSelectRole,
    isLoading = false,
}) {
    if (isLoading) {
        return (
            <div className="space-y-3">
                <div className="h-4 w-32 bg-[var(--surface-hover)] rounded animate-pulse" />
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                        <div
                            key={i}
                            className="h-28 rounded-xl bg-[var(--surface-hover)] animate-pulse"
                        />
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <label className="block text-xs font-bold uppercase tracking-wider text-[var(--text-secondary)]">
                    Target Role Benchmark
                </label>
                <span className="text-xs text-[var(--text-muted)]">
                    {roles.length} standard roles available
                </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {roles.map((role) => {
                    const isSelected = selectedRoleId === role.role_id

                    return (
                        <button
                            key={role.role_id}
                            type="button"
                            onClick={() => onSelectRole(role.role_id)}
                            className={`group relative flex flex-col justify-between text-left rounded-xl p-3.5 transition-all cursor-pointer border ${
                                isSelected
                                    ? 'border-[var(--accent)] bg-[var(--accent-soft)] shadow-sm shadow-[var(--accent)]/15 ring-1 ring-[var(--accent)]'
                                    : 'border-[var(--border)] bg-[var(--surface-solid)] hover:border-[var(--accent)]/50 hover:bg-[var(--surface-hover)]'
                            }`}
                        >
                            <div className="space-y-1.5">
                                <div className="flex items-start justify-between gap-2">
                                    <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--accent)]">
                                        {role.domain}
                                    </span>
                                    {isSelected && (
                                        <CheckCircle
                                            size={16}
                                            className="text-[var(--accent)] shrink-0 mt-0.5"
                                        />
                                    )}
                                </div>

                                <h4 className="text-sm font-bold text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors line-clamp-1">
                                    {role.title}
                                </h4>

                                <p className="text-xs text-[var(--text-muted)] line-clamp-2 leading-relaxed">
                                    {role.description}
                                </p>
                            </div>

                            <div className="flex items-center gap-2 pt-3 border-t border-[var(--border)]/60 text-[11px] text-[var(--text-secondary)]">
                                <span className="font-medium">
                                    <strong className="text-[var(--text-primary)]">{role.required_skills_count}</strong> req
                                </span>
                                <span>•</span>
                                <span className="font-medium">
                                    <strong className="text-[var(--text-primary)]">{role.preferred_skills_count}</strong> pref
                                </span>
                                <span className="ml-auto text-[10px] text-[var(--text-muted)]">
                                    v{role.version}
                                </span>
                            </div>
                        </button>
                    )
                })}
            </div>
        </div>
    )
}
