import { lazy, Suspense } from 'react'
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Link,
  useLocation,
} from 'react-router-dom'
import { Sparkles, ArrowLeft } from 'lucide-react'

import DashboardLayout from './layouts/DashboardLayout'
import ErrorBoundary from './components/common/ErrorBoundary'
import { useCareerProfile } from './context/CareerProfileContext'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const ResumeAnalyzer = lazy(() => import('./pages/ResumeAnalyzer'))
const JobMatcher = lazy(() => import('./pages/JobMatcher'))
const Onboarding = lazy(() => import('./pages/Onboarding'))
const Landing = lazy(() => import('./pages/Landing'))

function PageLoader() {
  return (
    <div className="flex min-h-[300px] w-full items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--accent)] border-t-transparent" />
    </div>
  )
}

function PlaceholderPage({ title }) {
  return (
    <div className="placeholder-page glass-card">
      <div className="placeholder-icon">
        <Sparkles size={36} />
      </div>
      <h1>{title}</h1>
      <p>
        This feature is under development.
        It will be connected to the CareerMind AI backend in the next phase.
      </p>
      <Link to="/dashboard" className="primary-button secondary-style">
        <ArrowLeft size={16} /> Back to Dashboard
      </Link>
    </div>
  )
}

/**
 * Route guard ensuring that new users without a completed career profile
 * are redirected to /onboarding before accessing the workspace.
 */
function RequireOnboarding({ children }) {
  const { onboardingCompleted, isLoading } = useCareerProfile()
  const location = useLocation()

  if (isLoading) {
    return <PageLoader />
  }

  if (!onboardingCompleted) {
    return <Navigate to="/onboarding" replace state={{ from: location }} />
  }

  return children
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public SaaS Landing Page */}
        <Route
          path="/"
          element={
            <ErrorBoundary title="Home">
              <Suspense fallback={<PageLoader />}>
                <Landing />
              </Suspense>
            </ErrorBoundary>
          }
        />

        {/* Onboarding Registration Route */}
        <Route
          path="/onboarding"
          element={
            <ErrorBoundary title="Onboarding">
              <Suspense fallback={<PageLoader />}>
                <Onboarding />
              </Suspense>
            </ErrorBoundary>
          }
        />

        {/* Protected Workspace Routes requiring completed Career Profile */}
        <Route
          element={
            <RequireOnboarding>
              <DashboardLayout />
            </RequireOnboarding>
          }
        >
          <Route
            path="/dashboard"
            element={
              <ErrorBoundary title="Dashboard">
                <Suspense fallback={<PageLoader />}>
                  <Dashboard />
                </Suspense>
              </ErrorBoundary>
            }
          />

          <Route
            path="/resume"
            element={
              <ErrorBoundary title="Resume Analyzer">
                <Suspense fallback={<PageLoader />}>
                  <ResumeAnalyzer />
                </Suspense>
              </ErrorBoundary>
            }
          />

          <Route
            path="/jobs"
            element={
              <ErrorBoundary title="Job Matcher">
                <Suspense fallback={<PageLoader />}>
                  <JobMatcher />
                </Suspense>
              </ErrorBoundary>
            }
          />

          <Route
            path="/skills"
            element={<PlaceholderPage title="Skill Gap Analysis" />}
          />

          <Route
            path="/roadmap"
            element={<PlaceholderPage title="Learning Roadmap" />}
          />

          <Route
            path="/interview"
            element={<PlaceholderPage title="AI Interview" />}
          />
        </Route>

        {/* Catch-all redirect to Dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
