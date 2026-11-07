
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './index.css'
import './App.css'
import App from './App.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'
import { CandidateProvider } from './context/CandidateContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <CandidateProvider>
        <App />
      </CandidateProvider>
    </ThemeProvider>
  </StrictMode>,
)
