import { useState, useRef, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { X, Send, Sparkles, ShieldCheck, ArrowRight, Bot } from 'lucide-react'
import MindyMascot from '../common/MindyMascot'

const PRESET_ANSWERS = {
    privacy: "CareerMind AI is 100% local-first! 🔒 All resumes, skills, and match reports remain purely inside your local SQLite database. We never send your data to external cloud LLM APIs.",
    features: "We currently provide: \n1. Resume Intelligence (extracting and categorizing 10+ skill domains)\n2. Job Description Matching (explainable scoring and skill gap detection)\n3. Coming soon: Learning Roadmaps & AI Interview prep!",
    onboarding: "To get started, click 'Build My Career Profile' to register your background and target preferences in just 3 quick steps!",
    default: "I'm Mindy, your local AI career guide! You can start by building your Career Profile or testing your resume against job descriptions."
}

const GREETING_STORAGE_KEY = 'careermind_mascot_greeted'

export default function MindyChatbot() {
    const [isOpen, setIsOpen] = useState(false)
    const [messages, setMessages] = useState([
        {
            sender: 'mindy',
            text: "Hi! I'm Mindy 👋\nYour AI Career Assistant. How can I help you take control of your career today?",
        },
    ])
    const [inputValue, setInputValue] = useState('')
    const chatEndRef = useRef(null)

    // Greeting popup state: show once on first visit, then auto-hide after 3s
    const [showGreeting, setShowGreeting] = useState(() => {
        try {
            return !localStorage.getItem(GREETING_STORAGE_KEY)
        } catch {
            return false
        }
    })

    const dismissGreeting = useCallback((e) => {
        if (e) e.stopPropagation()
        setShowGreeting(false)
        try {
            localStorage.setItem(GREETING_STORAGE_KEY, 'true')
        } catch {
            // Ignore storage errors safely
        }
    }, [])

    // Automatically hide greeting popup after approximately 3 seconds
    useEffect(() => {
        if (!showGreeting) return

        const timer = setTimeout(() => {
            dismissGreeting()
        }, 3200)

        return () => clearTimeout(timer)
    }, [showGreeting, dismissGreeting])

    useEffect(() => {
        if (isOpen) {
            chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
        }
    }, [messages, isOpen])

    const handleToggleOpen = () => {
        if (!isOpen && showGreeting) {
            dismissGreeting()
        }
        setIsOpen((prev) => !prev)
    }

    const handleSend = (textToSend) => {
        const query = (textToSend || inputValue).trim()
        if (!query) return

        const userMsg = { sender: 'user', text: query }
        const lower = query.toLowerCase()

        let replyText = PRESET_ANSWERS.default
        if (lower.includes('privat') || lower.includes('data') || lower.includes('secure') || lower.includes('cloud')) {
            replyText = PRESET_ANSWERS.privacy
        } else if (lower.includes('feature') || lower.includes('what can you do') || lower.includes('tool')) {
            replyText = PRESET_ANSWERS.features
        } else if (lower.includes('start') || lower.includes('onboard') || lower.includes('profile')) {
            replyText = PRESET_ANSWERS.onboarding
        }

        const mindyMsg = { sender: 'mindy', text: replyText }

        setMessages((prev) => [...prev, userMsg, mindyMsg])
        setInputValue('')
    }

    return (
        <div className="fixed bottom-[calc(4.75rem+env(safe-area-inset-bottom,0px))] right-4 sm:right-5 md:bottom-6 md:right-6 z-40 select-none">
            {/* 1. Chatbot Dialogue Popup Card */}
            {isOpen && (
                <div className="mb-3 w-[92vw] sm:w-[350px] max-h-[500px] flex flex-col rounded-3xl border border-purple-300/40 dark:border-purple-500/30 bg-[var(--surface-solid)]/95 shadow-2xl backdrop-blur-xl overflow-hidden transition-all duration-200 animate-in fade-in zoom-in-95">
                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-3.5 border-b border-[var(--border)] bg-gradient-to-r from-[#6D28D9]/10 via-[#8B5CF6]/10 to-transparent">
                        <div className="flex items-center gap-2.5">
                            <div className="relative flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#6D28D9] to-[#8B5CF6] p-1 shadow-md shadow-purple-500/20 overflow-hidden">
                                <MindyMascot expression="chatbot" size="xs" alt="Mindy Chatbot" className="scale-125" />
                                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-[#22C55E] ring-2 ring-white dark:ring-[#17172E]" />
                            </div>
                            <div>
                                <h3 className="text-sm font-extrabold text-[#17172E] dark:text-[#F8FAFC]">
                                    Hi! I&apos;m Mindy 👋
                                </h3>
                                <p className="text-[11px] font-medium text-[#64748B] dark:text-[#C4B5FD]/80">
                                    Your AI Career Assistant
                                </p>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={() => setIsOpen(false)}
                            aria-label="Close Mindy Chat"
                            className="flex h-8 w-8 items-center justify-center rounded-xl text-[#64748B] hover:text-[#17172E] dark:hover:text-white hover:bg-purple-100/50 dark:hover:bg-purple-900/30 transition-all cursor-pointer"
                        >
                            <X size={18} />
                        </button>
                    </div>

                    {/* Chat Messages List */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs max-h-[290px] scrollbar-thin">
                        {messages.map((m, idx) => (
                            <div
                                key={idx}
                                className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-2xl p-3 leading-relaxed ${
                                        m.sender === 'user'
                                            ? 'purple-gradient-btn text-white rounded-br-none shadow-md'
                                            : 'bg-white dark:bg-[#20183E] text-[#17172E] dark:text-[#F8FAFC] border border-purple-200/50 dark:border-purple-500/20 rounded-bl-none shadow-sm whitespace-pre-line'
                                    }`}
                                >
                                    {m.text}
                                </div>
                            </div>
                        ))}
                        <div ref={chatEndRef} />
                    </div>

                    {/* Quick Guidance Chips */}
                    <div className="px-3 py-2 border-t border-[var(--border)] bg-[var(--surface)] flex items-center gap-1.5 overflow-x-auto no-scrollbar text-[11px]">
                        <Link
                            to="/onboarding"
                            className="inline-flex items-center gap-1 shrink-0 rounded-xl bg-[#8B5CF6]/15 hover:bg-[#8B5CF6]/25 border border-[#8B5CF6]/30 px-2.5 py-1 font-semibold text-[#6D28D9] dark:text-[#C4B5FD] transition-colors"
                        >
                            <span>🚀 Onboarding</span>
                            <ArrowRight size={11} />
                        </Link>
                        <button
                            type="button"
                            onClick={() => handleSend('Is my data private?')}
                            className="inline-flex items-center gap-1 shrink-0 rounded-xl bg-slate-100 dark:bg-purple-900/20 hover:bg-slate-200 dark:hover:bg-purple-900/40 border border-slate-200 dark:border-purple-500/20 px-2.5 py-1 font-medium text-[#64748B] dark:text-[#C4B5FD]/90 transition-colors cursor-pointer"
                        >
                            <ShieldCheck size={12} className="text-[#22C55E]" />
                            <span>Privacy</span>
                        </button>
                        <button
                            type="button"
                            onClick={() => handleSend('What features are offered?')}
                            className="inline-flex items-center gap-1 shrink-0 rounded-xl bg-slate-100 dark:bg-purple-900/20 hover:bg-slate-200 dark:hover:bg-purple-900/40 border border-slate-200 dark:border-purple-500/20 px-2.5 py-1 font-medium text-[#64748B] dark:text-[#C4B5FD]/90 transition-colors cursor-pointer"
                        >
                            <Sparkles size={11} className="text-[#8B5CF6]" />
                            <span>Features</span>
                        </button>
                    </div>

                    {/* Input Bar */}
                    <form
                        onSubmit={(e) => {
                            e.preventDefault()
                            handleSend()
                        }}
                        className="p-2.5 border-t border-[var(--border)] flex items-center gap-2 bg-[var(--surface-solid)]"
                    >
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder="Ask Mindy anything..."
                            className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-xs text-[#17172E] dark:text-[#F8FAFC] placeholder-[#94A3B8] focus:border-[#8B5CF6] focus:outline-none transition-all"
                        />
                        <button
                            type="submit"
                            aria-label="Send message to Mindy"
                            className="purple-gradient-btn flex h-8 w-8 items-center justify-center rounded-xl shrink-0 cursor-pointer"
                        >
                            <Send size={13} />
                        </button>
                    </form>
                </div>
            )}

            {/* 2. Floating Greeting Popup (Shows for ~3s on first visit, or until dismissed) */}
            {!isOpen && showGreeting && (
                <div
                    onClick={handleToggleOpen}
                    role="status"
                    aria-live="polite"
                    className="absolute bottom-[calc(100%+0.75rem)] right-0 z-30 flex items-center gap-2 rounded-2xl border border-purple-200/90 dark:border-purple-500/40 bg-white/98 dark:bg-[#1E1738]/98 px-3.5 py-2 text-xs font-bold text-[#17172E] dark:text-[#F8FAFC] shadow-xl shadow-purple-900/15 backdrop-blur-md animate-in fade-in slide-in-from-bottom-2 duration-300 max-w-[calc(100vw-2rem)] whitespace-nowrap cursor-pointer hover:border-purple-400 dark:hover:border-purple-400 transition-colors"
                >
                    <span className="text-xs sm:text-sm">Let&apos;s do this! 🚀</span>

                    {/* Small close/dismiss button */}
                    <button
                        type="button"
                        onClick={dismissGreeting}
                        aria-label="Dismiss greeting popup"
                        className="flex h-4 w-4 items-center justify-center rounded-full text-[#94A3B8] hover:text-[#17172E] dark:hover:text-white hover:bg-purple-100 dark:hover:bg-purple-900/40 transition-colors p-0.5 ml-0.5 cursor-pointer"
                    >
                        <X size={12} strokeWidth={2.5} />
                    </button>

                    {/* Pointer Arrow pointing down to the mascot */}
                    <div className="absolute -bottom-1.5 right-6 w-3 h-3 rotate-45 border-r border-b border-purple-200/90 dark:border-purple-500/40 bg-white dark:bg-[#1E1738]" />
                </div>
            )}

            {/* 3. Floating Circular Mindy Avatar Button */}
            <button
                type="button"
                onClick={handleToggleOpen}
                aria-label={isOpen ? 'Close Mindy AI Assistant' : 'Open Mindy AI Assistant'}
                className="group relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-tr from-[#6D28D9] via-[#8B5CF6] to-[#C4B5FD] p-0.5 shadow-[0_6px_25px_rgba(109,40,217,0.4)] hover:shadow-[0_8px_32px_rgba(109,40,217,0.55)] hover:scale-105 active:scale-95 transition-all cursor-pointer"
            >
                <div className="relative flex h-full w-full items-center justify-center rounded-full bg-white dark:bg-[#140F28] overflow-hidden">
                    <img
                        src="/assets/mindy/mindy-chatbot.png"
                        alt="Mindy Mascot"
                        className="h-11 w-11 object-contain translate-y-0.5 group-hover:scale-110 transition-transform duration-200"
                    />
                </div>

                {/* Online Indicator Badge */}
                <span className="absolute top-0 right-0 flex h-4 w-4 items-center justify-center">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#22C55E] opacity-75" />
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-[#22C55E] ring-2 ring-white dark:ring-[#140F28]" />
                </span>

                {/* Subtle Hover Bubble on Desktop (only when closed and greeting is not active) */}
                {!isOpen && !showGreeting && (
                    <div className="absolute right-16 hidden md:group-hover:flex items-center gap-1.5 whitespace-nowrap rounded-xl bg-white dark:bg-[#1C1731] border border-purple-200 dark:border-purple-500/30 px-3 py-1.5 text-xs font-bold text-[#17172E] dark:text-[#F8FAFC] shadow-lg animate-in fade-in slide-in-from-right-2">
                        <Bot size={13} className="text-[#8B5CF6]" />
                        <span>Chat with Mindy</span>
                    </div>
                )}
            </button>
        </div>
    )
}

