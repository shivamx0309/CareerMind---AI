import { lazy, Suspense } from 'react'
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from 'react-router-dom'

import DashboardLayout from './layouts/DashboardLayout'
import ErrorBoundary from './components/common/ErrorBoundary'
import { useCareerProfile } from './context/CareerProfileContext'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const ResumeAnalyzer = lazy(() => import('./pages/ResumeAnalyzer'))
const JobMatcher = lazy(() => import('./pages/JobMatcher'))
const SkillGap = lazy(() => import('./pages/SkillGap'))
const Roadmap = lazy(() => import('./pages/Roadmap'))
const Interview = lazy(() => import('./pages/Interview'))
const Onboarding = lazy(() => import('./pages/Onboarding'))
const Landing = lazy(() => import('./pages/Landing'))

function PageLoader() {
  return (
    <div className="flex min-h-[300px] w-full items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--accent)] border-t-transparent" />
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
            element={
              <ErrorBoundary title="Skill Gap Analysis">
                <Suspense fallback={<PageLoader />}>
                  <SkillGap />
                </Suspense>
              </ErrorBoundary>
            }
          />

          <Route
            path="/roadmap"
            element={
              <ErrorBoundary title="Learning Roadmap">
                <Suspense fallback={<PageLoader />}>
                  <Roadmap />
                </Suspense>
              </ErrorBoundary>
            }
          />

          <Route
            path="/interview"
            element={
              <ErrorBoundary title="Mock Interview">
                <Suspense fallback={<PageLoader />}>
                  <Interview />
                </Suspense>
              </ErrorBoundary>
            }
          />
        </Route>

        {/* Catch-all redirect to Dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
