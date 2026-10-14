import { motion } from 'framer-motion';
import { MessageSquare, Stethoscope, Building2, Ambulance, Microscope, Users, Phone, ArrowRight } from 'lucide-react';

const agents = [
  {
    id: '01',
    name: 'Intake Agent',
    role: 'Natural Language Understanding',
    description: 'Accepts patient symptoms in Hindi, Bhojpuri, or English via text/voice. Extracts structured medical entities like symptoms, duration, age, and location using Gemini LLM.',
    icon: MessageSquare,
    color: 'from-blue-500 to-indigo-600',
    bgLight: 'bg-blue-50',
    textColor: 'text-blue-700',
  },
  {
    id: '02',
    name: 'Triage Agent',
    role: 'Urgency Classification Engine',
    description: 'Analyzes extracted symptoms and classifies urgency as Critical, Urgent, or Routine. Uses evidence-based medical reasoning with confidence scores and transparent decision rationale.',
    icon: Stethoscope,
    color: 'from-orange-500 to-amber-600',
    bgLight: 'bg-orange-50',
    textColor: 'text-orange-700',
  },
  {
    id: '03',
    name: 'Care Coordination',
    role: 'Hospital Scoring & Routing',
    description: 'Scores nearby hospitals on bed availability, ICU capacity, specialist presence, and travel distance. Dynamically routes patients to the best-equipped facility — not just the nearest.',
    icon: Building2,
    color: 'from-emerald-500 to-teal-600',
    bgLight: 'bg-emerald-50',
    textColor: 'text-emerald-700',
  },
  {
    id: '04',
    name: 'Emergency Ops',
    role: 'Overload Prediction & Load Balancing',
    description: 'Predicts hospital overload before it happens. When a facility nears capacity, redistributes incoming patients to alternate hospitals and dispatches ambulance services.',
    icon: Ambulance,
    color: 'from-red-500 to-rose-600',
    bgLight: 'bg-red-50',
    textColor: 'text-red-700',
  },
  {
    id: '05',
    name: 'Public Health Intel',
    role: 'Disease Outbreak Detection',
    description: 'Clusters recent cases by symptoms and geography. Detects patterns like Dengue or Cholera outbreaks and predicts next hotspot location using spatial analysis.',
    icon: Microscope,
    color: 'from-purple-500 to-violet-600',
    bgLight: 'bg-purple-50',
    textColor: 'text-purple-700',
  },
  {
    id: '06',
    name: 'Community Liaison',
    role: 'Local Resource Mobilization',
    description: 'Dispatches registered local drivers, volunteers, and blood donors near the patient. Connects community health workers for last-mile emergency support in rural areas.',
    icon: Users,
    color: 'from-teal-500 to-cyan-600',
    bgLight: 'bg-teal-50',
    textColor: 'text-teal-700',
  },
  {
    id: '07',
    name: 'Follow-up Agent',
    role: 'Post-Treatment Monitoring',
    description: 'Sends automated 24-hour check-in messages to patients. Tracks recovery, flags worsening symptoms, and re-triggers the care pipeline if intervention is needed.',
    icon: Phone,
    color: 'from-indigo-500 to-blue-600',
    bgLight: 'bg-indigo-50',
    textColor: 'text-indigo-700',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08 }
  }
};

const cardVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100, damping: 20 } }
};

export default function AgentArchitecture() {
  return (
    <section id="architecture" className="py-28 bg-slate-50/50 dark:bg-slate-900/50 relative overflow-hidden">
      {/* Decorative background */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[400px] bg-gradient-to-b from-primary/3 to-transparent rounded-full blur-3xl pointer-events-none" />

      <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <span className="inline-block text-xs font-bold tracking-widest uppercase text-primary mb-4 bg-primary/10 px-3 py-1 rounded-full">
            System Architecture
          </span>
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            7 Specialized AI Agents,
            <br />
            <span className="text-muted-foreground">One Coordinated System</span>
          </h2>
          <p className="mt-5 text-lg text-muted-foreground leading-relaxed">
            A single LLM cannot manage a healthcare crisis. AI Sahayak decomposes the problem into 
            7 deterministic agents, each with a clear responsibility, communicating via structured JSON contracts.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5"
        >
          {agents.map((agent) => (
            <motion.div
              key={agent.id}
              variants={cardVariants}
              whileHover={{ y: -6, scale: 1.02 }}
              className="group relative flex flex-col p-6 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-2xl border border-slate-200/60 dark:border-slate-700/60 shadow-sm transition-all duration-300 hover:shadow-xl hover:shadow-slate-200/50 dark:hover:shadow-black/50 hover:border-slate-300/60 dark:hover:border-slate-600/60"
            >
              {/* Gradient accent on hover */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${agent.color} opacity-0 group-hover:opacity-[0.03] transition-opacity duration-500`} />

              <div className="relative z-10">
                <div className="flex items-center justify-between mb-4">
                  <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${agent.bgLight} transition-transform group-hover:scale-110`}>
                    <agent.icon size={20} className={agent.textColor} />
                  </div>
                  <span className="text-xs font-bold text-slate-300 group-hover:text-primary/30 transition-colors">
                    {agent.id}
                  </span>
                </div>

                <h3 className="text-base font-bold text-foreground mb-1 tracking-tight">
                  {agent.name}
                </h3>
                <p className="text-[11px] font-semibold text-primary/70 uppercase tracking-wider mb-3">
                  {agent.role}
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {agent.description}
                </p>
              </div>
            </motion.div>
          ))}

          <motion.div
            variants={cardVariants}
            className="flex flex-col items-center justify-center p-6 bg-gradient-to-br from-primary/5 dark:from-primary/10 to-blue-50/50 dark:to-slate-800/50 rounded-2xl border border-primary/15 dark:border-primary/20 border-dashed"
          >
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-3">
              <ArrowRight size={20} className="text-primary" />
            </div>
            <p className="text-sm font-semibold text-primary text-center leading-snug">
              All agents communicate via structured JSON contracts — no hallucinations, fully deterministic.
            </p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
