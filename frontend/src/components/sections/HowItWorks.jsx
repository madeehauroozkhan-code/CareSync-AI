import { motion } from 'framer-motion';
import { MessageSquare, Stethoscope, Building2, Ambulance, Heart, ArrowRight } from 'lucide-react';

const routineSteps = [
  {
    icon: MessageSquare,
    title: 'Intake Agent',
    desc: 'Patient says: "Mujhe 2 din se halka bukhaar hai." Agent extracts symptoms: mild fever, 2 days duration.',
    color: 'bg-blue-500',
    ring: 'ring-blue-50',
  },
  {
    icon: Stethoscope,
    title: 'Triage Agent',
    desc: 'Classifies as Routine (88% confidence). Low-grade fever with no alarming co-symptoms detected.',
    color: 'bg-emerald-500',
    ring: 'ring-emerald-50',
  },
  {
    icon: Heart,
    title: 'Home Care Advice',
    desc: 'Provides safe hydration guidance, rest recommendations, and ORS instructions. No hospital visit needed.',
    color: 'bg-green-500',
    ring: 'ring-green-50',
  },
];

const criticalSteps = [
  {
    icon: MessageSquare,
    title: 'Intake Agent',
    desc: 'Patient reports: "Chest me tez dard hai, saans nahi aa rahi." Critical cardiac symptoms extracted immediately.',
    color: 'bg-blue-500',
    ring: 'ring-blue-50',
  },
  {
    icon: Stethoscope,
    title: 'Triage Agent',
    desc: 'Classifies as CRITICAL (95% confidence). Chest pain + breathlessness = potential cardiac event flagged.',
    color: 'bg-orange-500',
    ring: 'ring-orange-50',
  },
  {
    icon: Building2,
    title: 'Care Coordination',
    desc: 'Scores 12 hospitals. Skips nearest (full ICU). Selects Hospital C — Cardiologist available, 3 ICU beds free, 12km away.',
    color: 'bg-teal-500',
    ring: 'ring-teal-50',
  },
  {
    icon: Ambulance,
    title: 'Emergency Ops + Community',
    desc: 'Dispatches ambulance (ETA 8 min). Alerts nearest registered blood donor (2km). Community health worker notified.',
    color: 'bg-red-500',
    ring: 'ring-red-50',
    pulse: true,
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-28 bg-background relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-primary/3 via-transparent to-transparent pointer-events-none" />
      
      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <span className="inline-block text-xs font-bold tracking-widest uppercase text-primary mb-4 bg-primary/10 px-3 py-1 rounded-full">
            Live Demonstration
          </span>
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            Intelligent Triage & Routing
          </h2>
          <p className="mt-5 text-lg text-muted-foreground leading-relaxed">
            See how AI Sahayak handles a mild fever vs. a critical cardiac emergency.
            Different symptoms trigger different agent pipelines — automatically.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">
          
          {/* Routine Case */}
          <motion.div
            initial={{ opacity: 0, x: -40, y: 20 }}
            whileInView={{ opacity: 1, x: 0, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            className="relative p-8 rounded-3xl bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-700/60 shadow-sm hover:shadow-xl hover:shadow-slate-200/30 dark:hover:shadow-black/50 transition-all duration-500"
          >
            <div className="absolute top-0 right-0 px-5 py-1.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-bl-2xl rounded-tr-3xl uppercase tracking-wider border-b border-l border-emerald-100 dark:border-emerald-800">
              ✓ Routine Case
            </div>

            <div className="flex gap-4 mb-8 mt-4">
              <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center shrink-0">
                <MessageSquare size={16} className="text-slate-500 dark:text-slate-300" />
              </div>
              <div className="bg-slate-50 dark:bg-slate-700/50 p-4 rounded-2xl rounded-tl-sm border border-slate-100 dark:border-slate-600 text-sm font-medium text-slate-700 dark:text-slate-200 italic">
                "Mujhe 2 din se halka bukhaar hai."
              </div>
            </div>

            <div className="space-y-6 pl-5 border-l-2 border-slate-200 dark:border-slate-700 ml-5 py-1">
              {routineSteps.map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -15 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8, delay: 0.2 + i * 0.15, ease: [0.16, 1, 0.3, 1] }}
                  className="relative"
                >
                  <div className={`absolute -left-[27px] top-1 w-3 h-3 rounded-full ${step.color} ring-4 ${step.ring}`} />
                  <p className="text-sm font-bold text-foreground mb-1">{step.title}</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">{step.desc}</p>
                </motion.div>
              ))}
            </div>

            <div className="mt-6 p-3 bg-emerald-50/60 dark:bg-emerald-900/20 rounded-xl border border-emerald-100/60 dark:border-emerald-800/60 flex items-center gap-2">
              <Heart size={14} className="text-emerald-600 dark:text-emerald-400" />
              <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400">Result: Home care advice provided. No hospital visit needed.</span>
            </div>
          </motion.div>

          {/* Critical Case */}
          <motion.div
            initial={{ opacity: 0, x: 40, y: 20 }}
            whileInView={{ opacity: 1, x: 0, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="relative p-8 rounded-3xl bg-white dark:bg-slate-800 border border-red-100/60 dark:border-red-900/60 shadow-sm hover:shadow-xl hover:shadow-red-100/30 dark:hover:shadow-black/50 transition-all duration-500"
          >
            <div className="absolute top-0 right-0 px-5 py-1.5 bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs font-bold rounded-bl-2xl rounded-tr-3xl uppercase tracking-wider border-b border-l border-red-100 dark:border-red-800">
              ⚠ Critical Emergency
            </div>

            <div className="flex gap-4 mb-8 mt-4">
              <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center shrink-0">
                <MessageSquare size={16} className="text-slate-500 dark:text-slate-300" />
              </div>
              <div className="bg-red-50/40 dark:bg-red-900/20 p-4 rounded-2xl rounded-tl-sm border border-red-100/60 dark:border-red-800/60 text-sm font-medium text-slate-700 dark:text-slate-200 italic">
                "Chest me tez dard hai, saans nahi aa rahi."
              </div>
            </div>

            <div className="space-y-6 pl-5 border-l-2 border-red-200/60 dark:border-red-900/60 ml-5 py-1">
              {criticalSteps.map((step, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -15 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8, delay: 0.4 + i * 0.15, ease: [0.16, 1, 0.3, 1] }}
                  className="relative"
                >
                  <div className={`absolute -left-[27px] top-1 w-3 h-3 rounded-full ${step.color} ring-4 ${step.ring} ${step.pulse ? 'animate-pulse' : ''}`} />
                  <p className="text-sm font-bold text-foreground mb-1">{step.title}</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">{step.desc}</p>
                </motion.div>
              ))}
            </div>

            <div className="mt-6 p-3 bg-red-50/60 dark:bg-red-900/20 rounded-xl border border-red-100/60 dark:border-red-800/60 flex items-center gap-2">
              <Ambulance size={14} className="text-red-600 dark:text-red-400" />
              <span className="text-xs font-semibold text-red-700 dark:text-red-400">Result: Ambulance dispatched. Hospital C selected. Blood donor alerted.</span>
            </div>
          </motion.div>
        </div>

        {/* Bottom note */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.8 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="mt-12 text-center"
        >
          <p className="inline-flex items-center gap-2 text-sm text-muted-foreground bg-slate-50 dark:bg-slate-800 px-6 py-3 rounded-full border border-slate-200/60 dark:border-slate-700/60">
            <ArrowRight size={14} className="text-primary" />
            Both scenarios complete end-to-end in under <strong className="text-foreground">8 seconds</strong>
          </p>
        </motion.div>
      </div>
    </section>
  );
}
