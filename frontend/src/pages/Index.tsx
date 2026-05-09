import Navbar from "@/components/landing/Navbar";
import HeroSection from "@/components/landing/HeroSection";
import ProblemSection from "@/components/landing/ProblemSection";
import SolutionSection from "@/components/landing/SolutionSection";
import ChatDemoSection from "@/components/landing/ChatDemoSection";
import ScopeSection from "@/components/landing/ScopeSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import BenefitsSection from "@/components/landing/BenefitsSection";
import UseCasesSection from "@/components/landing/UseCasesSection";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";

const Index = () => (
  <>
    <Navbar />
    <main>
      <HeroSection />
      <ProblemSection />
      <SolutionSection />
      <ChatDemoSection />
      <ScopeSection />
      <HowItWorksSection />
      <BenefitsSection />
      <UseCasesSection />
      <CTASection />
    </main>
    <Footer />
  </>
);

export default Index;
