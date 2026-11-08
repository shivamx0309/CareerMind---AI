/**
 * Mindy Mascot — The official 3D robot companion of CareerMind AI.
 * Renders consistent, high-fidelity transparent PNG assets across platform views.
 */
const MASCOT_EXPRESSIONS = {
    welcome: '/assets/mindy/mindy-welcome.png',
    guide: '/assets/mindy/mindy-guide.png',
    thinking: '/assets/mindy/mindy-thinking.png',
    working: '/assets/mindy/mindy-working.png',
    success: '/assets/mindy/mindy-success.png',
    chatbot: '/assets/mindy/mindy-chatbot.png',
}

export default function MindyMascot({
    expression = 'welcome',
    alt = 'Mindy - AI Career Mascot',
    className = '',
    size = 'md', // sm, md, lg, xl, or custom
    speechBubble = null,
    priority = false,
}) {
    const src = MASCOT_EXPRESSIONS[expression] || MASCOT_EXPRESSIONS.welcome

    const sizeClasses = {
        xs: 'w-10 h-10',
        sm: 'w-16 h-16',
        md: 'w-32 h-32 md:w-40 md:h-40',
        lg: 'w-48 h-48 md:w-64 md:h-64',
        xl: 'w-72 h-72 md:w-96 md:h-96 lg:w-[440px] lg:h-[440px]',
        custom: '',
    }[size] || ''

    return (
        <div className={`relative inline-flex flex-col items-center select-none ${className}`}>
            {speechBubble && (
                <div className="absolute -top-12 z-20 whitespace-nowrap rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-1.5 text-xs font-bold text-[var(--text-primary)] shadow-md backdrop-blur-md animate-bounce">
                    {speechBubble}
                    <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-2.5 h-2.5 rotate-45 border-r border-b border-[var(--border)] bg-[var(--surface)]" />
                </div>
            )}
            <img
                src={src}
                alt={alt}
                loading={priority ? 'eager' : 'lazy'}
                decoding="async"
                className={`${sizeClasses} object-contain transition-transform duration-300 filter drop-shadow-[0_15px_30px_rgba(109,40,217,0.22)]`}
            />
        </div>
    )
}
