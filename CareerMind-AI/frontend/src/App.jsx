import { lazy, Suspense } from 'react'
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
} from 'react-router-dom'
import { Sparkles, ArrowLeft } from 'lucide-react'

import DashboardLayout from './layouts/DashboardLayout'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const ResumeAnalyzer = lazy(() => import('./pages/ResumeAnalyzer'))
const JobMatcher = lazy(() => import('./pages/JobMatcher'))

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
      <Link to="/" className="primary-button secondary-style">
        <ArrowLeft size={16} /> Back to Dashboard
      </Link>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route
            path="/"
            element={
              <Suspense fallback={<PageLoader />}>
                <Dashboard />
              </Suspense>
            }
          />

          <Route
            path="/resume"
            element={
              <Suspense fallback={<PageLoader />}>
                <ResumeAnalyzer />
              </Suspense>
            }
          />

          <Route
            path="/jobs"
            element={
              <Suspense fallback={<PageLoader />}>
                <JobMatcher />
              </Suspense>
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
      </Routes>
    </BrowserRouter>
  )
}

export default App
