import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Menu, X, ExternalLink } from 'lucide-react';

const GithubIcon = ({ size = 16, className = '' }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} className={`fill-current ${className}`} xmlns="http://www.w3.org/2000/svg">
    <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
  </svg>
);

const navLinks = [
  { label: 'Architecture', href: '#architecture' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Team', href: '#team' },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleNav = (href) => {
    setMobileOpen(false);
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <>
      <header className={`fixed top-0 left-0 right-0 z-50 flex justify-center w-full transition-all duration-[600ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${scrolled ? 'pt-4 px-4' : 'pt-0 px-0'}`}>
        <motion.nav
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className={`w-full transition-all duration-[600ms] ease-[cubic-bezier(0.16,1,0.3,1)] overflow-hidden relative ${
            scrolled
              ? 'max-w-5xl rounded-2xl bg-white/40 dark:bg-slate-900/40 backdrop-blur-xl shadow-[0_4px_30px_rgba(6,182,212,0.15)] border border-white/20'
              : 'max-w-full rounded-none bg-transparent border-b border-transparent'
          }`}
        >
          {/* Neon edge line that appears when scrolled */}
          <div className={`absolute bottom-0 left-0 h-[3px] w-full bg-gradient-to-r from-transparent via-cyan-400 to-transparent transition-opacity duration-[600ms] ease-[cubic-bezier(0.16,1,0.3,1)] shadow-[0_0_15px_rgba(6,182,212,0.8)] ${scrolled ? 'opacity-100' : 'opacity-0'}`} />
          <div className="container mx-auto flex h-16 w-full items-center justify-between px-4 sm:px-6 lg:px-8 relative z-10">
          
          {/* Logo */}
          <a href="#" className="flex items-center gap-2.5 group">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl overflow-hidden shadow-[0_0_15px_rgba(6,182,212,0.4)] group-hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] transition-shadow bg-white">
              <img src="/logo.png" alt="AI Sahayak Logo" className="w-full h-full object-contain p-1" />
            </div>
            <span className="text-lg font-bold tracking-tight text-foreground">
              AI Sahayak
            </span>
          </a>

          {/* Right Side: Navigation & Actions */}
          <div className="flex items-center gap-6">
            {/* Desktop Links */}
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => handleNav(link.href)}
                  className="relative px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors rounded-lg hover:bg-slate-100/60 dark:hover:bg-slate-800/60"
                >
                  {link.label}
                </button>
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
            <a
              href="https://github.com/m1n1v1rus/ai-sahayak"
              target="_blank"
              rel="noreferrer"
              className="hidden sm:inline-flex items-center gap-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-foreground hover:bg-slate-100/60 dark:hover:bg-slate-800/60 transition-all px-3 py-2"
            >
              <GithubIcon size={16} />
              GitHub
            </a>
            <button
              onClick={() => window.open(import.meta.env.VITE_DASHBOARD_URL || '#', '_blank')}
              className="hidden sm:inline-flex items-center gap-2 rounded-xl text-sm font-bold transition-all bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-lg hover:shadow-primary/20 hover:-translate-y-0.5 active:translate-y-0 h-9 px-5"
            >
              <ExternalLink size={14} />
              Live Dashboard
            </button>

            {/* Mobile toggle */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden inline-flex items-center justify-center w-9 h-9 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-600 dark:text-slate-300"
            >
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
          </div>
        </div>
      </motion.nav>
      </header>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-x-0 top-16 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-2xl border-b border-slate-200 dark:border-slate-800 shadow-xl md:hidden"
          >
            <div className="p-4 space-y-1">
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => handleNav(link.href)}
                  className="w-full text-left px-4 py-3 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors"
                >
                  {link.label}
                </button>
              ))}
              <hr className="my-2 border-slate-100 dark:border-slate-800" />
              <a
                href="https://github.com/m1n1v1rus/ai-sahayak"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 px-4 py-3 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
              >
                <GithubIcon size={16} /> GitHub Repository
              </a>
              <button
                onClick={() => { setMobileOpen(false); window.open(import.meta.env.VITE_DASHBOARD_URL || '#', '_blank'); }}
                className="w-full mt-2 flex items-center justify-center gap-2 bg-primary text-primary-foreground rounded-xl py-3 text-sm font-bold"
              >
                <ExternalLink size={14} /> Open Live Dashboard
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
