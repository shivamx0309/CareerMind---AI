import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './index.css'
import './App.css'
import App from './App.jsx'
import { ThemeProvider } from './context/ThemeContext.jsx'
import { CandidateProvider } from './context/CandidateContext.jsx'
import { CareerProfileProvider } from './context/CareerProfileContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider>
      <CareerProfileProvider>
        <CandidateProvider>
          <App />
        </CandidateProvider>
      </CareerProfileProvider>
    </ThemeProvider>
  </StrictMode>,
)
