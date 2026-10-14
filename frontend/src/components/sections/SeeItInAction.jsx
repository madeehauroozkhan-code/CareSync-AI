import { motion } from 'framer-motion';
import { ExternalLink } from 'lucide-react';

export default function SeeItInAction() {
  return (
    <section className="py-24 bg-slate-50 dark:bg-slate-900/50 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/5 via-transparent to-transparent pointer-events-none" />

      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <span className="inline-block text-xs font-bold tracking-widest uppercase text-primary mb-4 bg-primary/10 px-3 py-1 rounded-full">
            Command Center
          </span>
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            See It In Action
          </h2>
          <p className="mt-5 text-lg text-muted-foreground leading-relaxed">
            The real-time admin dashboard coordinates everything automatically. Track active cases, monitor hospital capacity, and detect early disease outbreaks in a single view.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
          className="relative max-w-5xl mx-auto px-2 sm:px-0"
        >
          {/* Subtle floating/parallax effect on the wrapper */}
          <motion.div 
            animate={{ y: [0, -8, 0] }}
            transition={{ repeat: Infinity, duration: 6, ease: "easeInOut" }}
            className="rounded-xl overflow-hidden shadow-2xl shadow-primary/10 dark:shadow-primary/5 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950"
          >
            {/* Browser Window Frame */}
            <div className="bg-slate-100 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 py-3 flex items-center gap-4">
              <div className="flex gap-1.5 shrink-0">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
              </div>
              
              {/* Fake address bar */}
              <div className="flex-1 bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-md py-1 px-3 text-center text-xs font-medium text-slate-500 font-mono tracking-wider max-w-sm mx-auto shadow-sm inset-y-0 truncate">
                admin.ai-sahayak.org
              </div>
            </div>
            
            {/* The actual screenshot */}
            <div className="relative group cursor-pointer overflow-hidden bg-slate-50 dark:bg-slate-900" onClick={() => window.open(import.meta.env.VITE_DASHBOARD_URL || '#', '_blank')}>
              <div className="flex flex-col transition-transform duration-700 group-hover:scale-[1.02]">
                <img 
                  src="/dashboard-screenshot-1.png" 
                  alt="AI Sahayak Admin Dashboard Top" 
                  className="w-full h-auto object-cover border-none"
                />
                <img 
                  src="/dashboard-screenshot-2.png" 
                  alt="AI Sahayak Admin Dashboard Bottom" 
                  className="w-full h-auto object-cover border-none"
                />
              </div>
              <div className="absolute inset-0 bg-slate-900/0 group-hover:bg-slate-900/10 dark:group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
                 <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm px-6 py-3 rounded-full shadow-lg border border-slate-200 dark:border-slate-700 text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center gap-2 transform translate-y-4 group-hover:translate-y-0 text-slate-800 dark:text-white">
                   <ExternalLink size={16} />
                   Open Live Dashboard
                 </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
