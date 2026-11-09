
/* eslint-disable react-refresh/only-export-components */
import {
    createContext,
    useContext,
    useEffect,
    useState,
} from 'react'

const ThemeContext = createContext(null)

function getInitialTheme() {
    try {
        const savedTheme = localStorage.getItem('careermind-theme')

        if (savedTheme === 'dark' || savedTheme === 'light') {
            return savedTheme
        }
    } catch {
        // Fall back to dark theme.
    }

    return 'dark'
}

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState(getInitialTheme)

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme)
        if (theme === 'dark') {
            document.documentElement.classList.add('dark')
        } else {
            document.documentElement.classList.remove('dark')
        }

        try {
            localStorage.setItem('careermind-theme', theme)
        } catch {
            // Current session theme remains functional.
        }
    }, [theme])

    const toggleTheme = () => {
        setTheme((current) =>
            current === 'dark' ? 'light' : 'dark'
        )
    }

    return (
        <ThemeContext.Provider
            value={{ theme, setTheme, toggleTheme }}
        >
            {children}
        </ThemeContext.Provider>
    )
}

export function useTheme() {
    const context = useContext(ThemeContext)

    if (!context) {
        throw new Error(
            'useTheme must be used inside ThemeProvider'
        )
    }

    return context
}
