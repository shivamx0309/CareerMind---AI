import LandingNavbar from '../components/landing/LandingNavbar'
import MobileBottomNav from '../components/landing/MobileBottomNav'
import HeroSection from '../components/landing/HeroSection'
import FeaturesSection from '../components/landing/FeaturesSection'
import HowItWorksSection from '../components/landing/HowItWorksSection'
import WhyCareerMindSection from '../components/landing/WhyCareerMindSection'
import FinalCtaSection from '../components/landing/FinalCtaSection'
import LandingFooter from '../components/landing/LandingFooter'
import MindyChatbot from '../components/landing/MindyChatbot'

export default function Landing() {
    return (
        <div className="landing-page-container bg-[var(--bg)] text-[var(--text-primary)] transition-colors duration-200 min-h-screen relative overflow-x-hidden pb-20 md:pb-0">
            {/* Sticky Top Navigation Bar (Logo + Theme Toggle on Mobile; Full row on Desktop) */}
            <LandingNavbar />

            {/* Main Content Sections */}
            <main>
                <HeroSection />
                <FeaturesSection />
                <HowItWorksSection />
                <WhyCareerMindSection />
                <FinalCtaSection />
            </main>

            {/* Floating Mindy AI Assistant Chatbot */}
            <MindyChatbot />

            {/* Fixed Bottom Horizontal Navigation Bar (Mobile Only: Exactly 4 Items) */}
            <MobileBottomNav />

            {/* Minimal Footer */}
            <LandingFooter />
        </div>
    )
}
