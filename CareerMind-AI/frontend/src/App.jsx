
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
} from 'react-router-dom'
import { Sparkles, ArrowLeft } from 'lucide-react'

import DashboardLayout from './layouts/DashboardLayout'
import Dashboard from './pages/Dashboard'

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
          <Route path="/" element={<Dashboard />} />

          <Route
            path="/resume"
            element={<PlaceholderPage title="Resume Analyzer" />}
          />

          <Route
            path="/jobs"
            element={<PlaceholderPage title="Job Matcher" />}
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
