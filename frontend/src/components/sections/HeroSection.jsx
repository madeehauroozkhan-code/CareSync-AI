import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { Activity, ArrowDown, Zap, Users, Clock } from 'lucide-react';
import { useEffect, useState } from 'react';
import ChatWindow from '../ChatWindow';

function AnimatedCounter({ from, to, duration = 2.5, prefix = "", suffix = "" }) {
  const count = useMotionValue(from);
  const rounded = useTransform(count, (latest) => prefix + Math.round(latest) + suffix);

  useEffect(() => {
    const controls = animate(count, to, { 
      duration, 
      ease: [0.16, 1, 0.3, 1], 
      delay: 0.5,
      repeat: Infinity,
      repeatType: "loop",
      repeatDelay: 0.5
    });
    return controls.stop;
  }, [count, to, duration]);

  return <motion.span>{rounded}</motion.span>;
}

const stats = [
  { icon: Zap, label: 'Active AI Agents', value: <AnimatedCounter from={0} to={7} /> },
  { icon: Users, label: 'Hospitals Connected', value: <AnimatedCounter from={0} to={12} /> },
  { icon: Clock, label: 'Avg. Response Time', value: <AnimatedCounter from={15} to={8} prefix="<" suffix="s" /> },
];

const marqueeItems = [
  "🩺 Multi-Agent AI Coordination",
  "⚡ Sub-8-Second Response",
  "🌐 Voice-First, Any Language",
  "🏥 12 Hospitals Connected",
  "🔒 Deterministic — Zero Hallucinations",
  "📊 Real-Time Dashboard",
  "🚑 Predictive Overload Detection"
];

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-background min-h-screen">
      {/* Animated gradient orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-primary/10 dark:bg-primary/20 blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full bg-blue-500/10 dark:bg-blue-600/20 blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-gradient-to-br from-primary/5 dark:from-primary/10 to-transparent blur-3xl" />
      </div>

      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10 pt-20 pb-16">
        
        {/* Top badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="flex justify-center mb-10"
        >
          <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/5 backdrop-blur-md px-4 py-2 text-sm font-medium text-primary gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            Live System — 7 AI Agents Coordinating in Real-Time
          </div>
        </motion.div>

        {/* Title + Description */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center max-w-4xl mx-auto mb-12"
        >
          <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight text-foreground leading-[1.05] mb-6">
            AI-Powered Healthcare
            <br />
            <span className="bg-gradient-to-r from-primary via-blue-600 to-primary bg-clip-text text-transparent">
              Coordination Platform
            </span>
          </h1>

          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            In rural India, every second matters. AI Sahayak is a multi-agent AI system that
            triages patients, scores hospital capacity, and dispatches emergency resources —
            all in under 8 seconds.
          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <button
              onClick={() => window.open(import.meta.env.VITE_DASHBOARD_URL || '#', '_blank')}
              className="inline-flex items-center gap-2 rounded-full text-base font-bold transition-all bg-primary text-primary-foreground hover:bg-primary/90 hover:scale-[1.03] hover:shadow-xl hover:shadow-primary/25 active:scale-100 h-13 px-8 py-3 shadow-lg shadow-primary/20"
            >
              <Activity className="h-5 w-5" />
              Launch Live Dashboard
            </button>
            <button
              onClick={() => document.getElementById('chat-section')?.scrollIntoView({ behavior: 'smooth', block: 'center' })}
              className="inline-flex items-center gap-2 rounded-full text-base font-bold transition-all bg-white/80 dark:bg-slate-800/80 backdrop-blur-md text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-700 hover:scale-[1.03] hover:shadow-lg active:scale-100 h-13 px-8 py-3 shadow-sm"
            >
              <ArrowDown className="h-4 w-4 animate-bounce" />
              Try AI Agent
            </button>
          </div>
        </motion.div>

        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="flex justify-center gap-8 md:gap-12 mb-14"
        >
          {stats.map((stat, i) => (
            <div key={i} className="flex items-center gap-3 text-center">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <stat.icon size={18} className="text-primary" />
              </div>
              <div className="text-left">
                <p className="text-xl font-bold text-foreground leading-none">{stat.value}</p>
                <p className="text-xs text-muted-foreground font-medium mt-0.5">{stat.label}</p>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Marquee Strip */}
        <div className="w-full max-w-5xl mx-auto overflow-hidden mb-8 relative">
          {/* Fading edges for marquee */}
          <div className="absolute inset-y-0 left-0 w-16 bg-gradient-to-r from-background to-transparent z-10"></div>
          <div className="absolute inset-y-0 right-0 w-16 bg-gradient-to-l from-background to-transparent z-10"></div>
          
          <div className="flex h-12 items-center bg-gray-100/50 dark:bg-gray-800/30 rounded-full border border-gray-200/50 dark:border-gray-700/50">
            <motion.div
              className="flex w-max gap-4 px-4 items-center"
              animate={{ x: ["0%", "-50%"] }}
              transition={{ repeat: Infinity, ease: "linear", duration: 25 }}
              whileHover={{ animationPlayState: "paused" }} // Attempt pause if supported
            >
              {[...marqueeItems, ...marqueeItems].map((item, idx) => (
                <div
                  key={idx}
                  className="whitespace-nowrap px-4 py-1.5 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-sm font-medium shadow-sm flex items-center"
                >
                  {item}
                </div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* Chat Window */}
        <motion.div
          id="chat-section"
          initial={{ opacity: 0, scale: 0.95, y: 40 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 1.2, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="relative max-w-3xl mx-auto h-[520px] rounded-2xl overflow-hidden shadow-2xl shadow-slate-900/10 dark:shadow-black/40 border border-white/60 dark:border-slate-700/50"
        >
          {/* Glass background effect */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/60 dark:from-slate-800/60 via-slate-50/40 dark:via-slate-900/40 to-primary/5 dark:to-primary/10 backdrop-blur-md"></div>
          
          <div className="relative w-full h-full z-10">
            <ChatWindow />
          </div>
        </motion.div>
      </div>
    </section>
  );
}
