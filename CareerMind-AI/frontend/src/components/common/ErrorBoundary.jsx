import React from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Link } from 'react-router-dom'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    if (this.props.onReset) {
      this.props.onReset()
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="glass-card my-6 rounded-2xl border border-rose-500/30 bg-rose-500/5 p-6 sm:p-8 text-center space-y-4">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400">
            <AlertTriangle size={24} />
          </div>

          <div className="space-y-1">
            <h3 className="text-base font-bold text-[var(--text-primary)]">
              {this.props.title || 'Something went wrong in this section'}
            </h3>
            <p className="text-xs text-[var(--text-secondary)] max-w-md mx-auto">
              An unexpected error occurred while rendering this component. You can reload or return to the dashboard.
            </p>
            {this.state.error?.message && (
              <p className="font-mono text-[11px] text-rose-300/80 bg-rose-950/30 rounded-lg p-2 max-w-lg mx-auto truncate mt-2">
                {this.state.error.message}
              </p>
            )}
          </div>

          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--surface-hover)] border border-[var(--border)] px-4 py-2 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--accent)] transition-all cursor-pointer"
            >
              <RefreshCw size={14} />
              <span>Try Again</span>
            </button>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 rounded-xl bg-[var(--accent)] px-4 py-2 text-xs font-semibold text-white hover:opacity-90 transition-all"
            >
              <Home size={14} />
              <span>Back to Dashboard</span>
            </Link>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

