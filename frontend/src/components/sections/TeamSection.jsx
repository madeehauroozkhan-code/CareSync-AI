import { motion } from 'framer-motion';
import { ExternalLink, Code2, Cpu, Globe, Sparkles } from 'lucide-react';

const GithubIcon = ({ size = 16, className = '' }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} className={`fill-current ${className}`} xmlns="http://www.w3.org/2000/svg">
    <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
  </svg>
);

const techStack = [
  { icon: Cpu, name: 'Google Gemini', desc: 'LLM backbone for NLU + triage reasoning' },
  { icon: Code2, name: 'FastAPI', desc: 'High-performance async Python backend' },
  { icon: Globe, name: 'React + Vite', desc: 'Modern frontend with Framer Motion' },
  { icon: Sparkles, name: 'Multi-Agent', desc: '7 deterministic agents via JSON contracts' },
];

export default function TeamSection() {
  return (
    <section id="team" className="py-28 bg-slate-50 dark:bg-slate-900 border-t border-border/50 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-primary/5 to-transparent rounded-full blur-3xl pointer-events-none" />

      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <span className="inline-block text-xs font-bold tracking-widest uppercase text-primary mb-4 bg-primary/10 px-3 py-1 rounded-full">
            Open Source
          </span>
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl mb-6">
            Built for Impact,
            <br />
            <span className="text-muted-foreground">Ready to Scale</span>
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed">
            AI Sahayak demonstrates how multi-agent AI architectures can solve 
            real-world healthcare infrastructure problems in resource-constrained regions of India.
          </p>
        </motion.div>

        {/* Tech Stack Grid */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto mb-14"
        >
          {techStack.map((tech, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col items-center text-center p-5 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl border border-slate-200/60 dark:border-slate-700/60 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300"
            >
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-3">
                <tech.icon size={18} className="text-primary" />
              </div>
              <h4 className="text-sm font-bold text-foreground mb-1">{tech.name}</h4>
              <p className="text-[11px] text-muted-foreground leading-snug">{tech.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <motion.a
            href="https://github.com/m1n1v1rus/ai-sahayak"
            target="_blank"
            rel="noreferrer"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center gap-3 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 px-8 py-4 rounded-full text-base font-bold shadow-xl shadow-slate-900/20 dark:shadow-black/50 hover:shadow-2xl hover:shadow-slate-900/30 dark:hover:shadow-black/70 transition-all"
          >
            <GithubIcon size={20} />
            View on GitHub
          </motion.a>
          <motion.button
            onClick={() => window.open(import.meta.env.VITE_DASHBOARD_URL || '#', '_blank')}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center gap-3 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 border-2 border-slate-200 dark:border-slate-700 px-8 py-4 rounded-full text-base font-bold shadow-sm hover:shadow-lg hover:border-slate-300 dark:hover:border-slate-600 transition-all"
          >
            <ExternalLink size={18} />
            Open Live Dashboard
          </motion.button>
        </div>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.8 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center text-sm text-slate-400 dark:text-slate-500 mt-10"
        >
          Built with FastAPI · React · Framer Motion · Google Gemini · Leaflet
        </motion.p>
      </div>
    </section>
  );
}
