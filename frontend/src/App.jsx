import Navbar from './components/sections/Navbar';
import HeroSection from './components/sections/HeroSection';
import AgentArchitecture from './components/sections/AgentArchitecture';
import HowItWorks from './components/sections/HowItWorks';
import TeamSection from './components/sections/TeamSection';
import SeeItInAction from './components/sections/SeeItInAction';
import AnimatedPipeline from './components/sections/AnimatedPipeline';
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
    window.scrollTo(0, 0);
  }, []);

  // Ensure dark mode is disabled globally if it was previously set
  useEffect(() => {
    document.documentElement.classList.remove('dark');
  }, []);

  return (
    <div className="min-h-screen bg-background font-sans text-foreground overflow-x-hidden">
      <Navbar />
      
      <main>
        <HeroSection />
        <AnimatedPipeline />
        <AgentArchitecture />
        <HowItWorks />
        <SeeItInAction />
        <TeamSection />
      </main>
      
      <footer className="py-10 bg-slate-900 text-slate-400 border-t border-slate-800">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm">© 2026 AI Sahayak. Built for Rural Healthcare in India.</p>
          <div className="flex items-center gap-6 text-sm">
            <a href="https://github.com/m1n1v1rus/ai-sahayak" target="_blank" rel="noreferrer" className="hover:text-white transition-colors">GitHub</a>
            <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
            <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
