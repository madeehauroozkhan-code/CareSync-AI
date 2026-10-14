import { motion } from 'framer-motion';
import { User, MessageSquare, Stethoscope, Network, Building2 } from 'lucide-react';

const nodes = [
  { id: 'patient', label: 'Patient', icon: User, activeColor: 'rgba(148, 163, 184, 0.8)', defaultColor: 'rgba(226, 232, 240, 1)', iconColor: '#64748b' },
  { id: 'intake', label: 'Intake Agent', icon: MessageSquare, activeColor: 'rgba(59, 130, 246, 0.8)', defaultColor: 'rgba(219, 234, 254, 1)', iconColor: '#2563eb' },
  { id: 'triage', label: 'Triage Agent', icon: Stethoscope, activeColor: 'rgba(16, 185, 129, 0.8)', defaultColor: 'rgba(209, 250, 229, 1)', iconColor: '#059669' },
  { id: 'coord', label: 'Care Coordination', icon: Network, activeColor: 'rgba(20, 184, 166, 0.8)', defaultColor: 'rgba(204, 251, 241, 1)', iconColor: '#0d9488' },
  { id: 'hospital', label: 'Hospital', icon: Building2, activeColor: 'rgba(244, 63, 94, 0.8)', defaultColor: 'rgba(255, 228, 230, 1)', iconColor: '#e11d48' },
];

const duration = 8; // Slower, 8 seconds loop duration

const nodeAnimations = [
  // 0: Patient (hits at t=0s, which is 0%)
  {
    scale: [1.15, 1, 1, 1, 1.15],
    boxShadow: [`0px 0px 30px ${nodes[0].activeColor}`, '0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)', `0px 0px 30px ${nodes[0].activeColor}`],
    borderColor: [nodes[0].activeColor, nodes[0].defaultColor, nodes[0].defaultColor, nodes[0].defaultColor, nodes[0].activeColor],
    times: [0, 0.04, 0.2, 0.96, 1]
  },
  // 1: Intake (hits at t=2s, which is 25%)
  {
    scale: [1, 1, 1.15, 1, 1],
    boxShadow: ['0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)', `0px 0px 30px ${nodes[1].activeColor}`, '0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)'],
    borderColor: [nodes[1].defaultColor, nodes[1].defaultColor, nodes[1].activeColor, nodes[1].defaultColor, nodes[1].defaultColor],
    times: [0, 0.21, 0.25, 0.29, 1]
  },
  // 2: Triage (hits at t=4s, which is 50%)
  {
    scale: [1, 1, 1.15, 1, 1],
    boxShadow: ['0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)', `0px 0px 30px ${nodes[2].activeColor}`, '0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)'],
    borderColor: [nodes[2].defaultColor, nodes[2].defaultColor, nodes[2].activeColor, nodes[2].defaultColor, nodes[2].defaultColor],
    times: [0, 0.46, 0.5, 0.54, 1]
  },
  // 3: Coord (hits at t=6s, which is 75%)
  {
    scale: [1, 1, 1.15, 1, 1],
    boxShadow: ['0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)', `0px 0px 30px ${nodes[3].activeColor}`, '0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)'],
    borderColor: [nodes[3].defaultColor, nodes[3].defaultColor, nodes[3].activeColor, nodes[3].defaultColor, nodes[3].defaultColor],
    times: [0, 0.71, 0.75, 0.79, 1]
  },
  // 4: Hospital (hits at t=8s, which is 100%)
  {
    scale: [1, 1, 1, 1.15, 1],
    boxShadow: ['0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)', '0px 0px 0px rgba(0,0,0,0)', `0px 0px 30px ${nodes[4].activeColor}`, '0px 0px 0px rgba(0,0,0,0)'],
    borderColor: [nodes[4].defaultColor, nodes[4].defaultColor, nodes[4].defaultColor, nodes[4].activeColor, nodes[4].defaultColor],
    times: [0, 0.8, 0.95, 0.99, 1]
  }
];

export default function AnimatedPipeline() {
  return (
    <section className="py-24 bg-slate-50/50 dark:bg-slate-950/50 relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-primary/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="container mx-auto max-w-6xl px-4 relative z-10">
        <div className="text-center mb-20">
          <span className="inline-block text-xs font-bold tracking-widest uppercase text-primary mb-4 bg-primary/10 px-3 py-1 rounded-full">
            Data Flow
          </span>
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Continuous AI Pipeline
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Watch how data flows seamlessly between autonomous AI agents. No manual intervention required.
          </p>
        </div>

        {/* Desktop Container Wrapper */}
        <div className="hidden md:flex relative w-full mt-10 rounded-[32px] p-[1px] bg-gradient-to-r from-cyan-400/50 via-blue-500/50 to-cyan-400/50 shadow-[0_0_40px_rgba(59,130,246,0.15)] group">
          
          {/* Inner Content */}
          <div className="relative z-10 flex items-center justify-between w-full p-8 rounded-[31px] bg-white dark:bg-slate-950">
            
            {/* Background Connecting Line (Desktop) */}
            <div className="absolute top-1/2 left-[40px] right-[40px] h-1 bg-slate-200/50 dark:bg-slate-700/50 -translate-y-1/2 rounded-full" >
              {/* Animated Particle (Desktop) */}
              <motion.div
                animate={{ left: ["0%", "100%"], opacity: [0, 1, 1, 1, 0] }}
                transition={{ repeat: Infinity, duration, ease: "linear", times: [0, 0.05, 0.5, 0.95, 1] }}
                className="absolute top-1/2 -translate-y-1/2 z-20 flex items-center w-16 -ml-8 drop-shadow-[0_0_8px_rgba(var(--primary),0.8)]"
              >
                {/* Blurry rectangular tail */}
                <div className="flex-1 h-1.5 bg-gradient-to-r from-transparent to-primary blur-[1px] rounded-l-full" />
                {/* Arrow head */}
                <div className="w-0 h-0 border-y-[6px] border-y-transparent border-l-[10px] border-l-primary" />
              </motion.div>
            </div>

            {nodes.map((node, index) => (
              <div key={node.id} className="relative z-10 flex flex-col items-center">
                <motion.div 
                  animate={nodeAnimations[index]}
                  transition={{ repeat: Infinity, duration, ease: "linear" }}
                  className="w-20 h-20 flex items-center justify-center rounded-2xl border-[3px] bg-white/80 dark:bg-slate-900/80 backdrop-blur-md relative z-30"
                >
                  <node.icon size={32} color={node.iconColor} />
                </motion.div>
                <div className="absolute top-full mt-4 text-sm font-bold text-slate-700 dark:text-slate-200 whitespace-nowrap text-center">
                  {node.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mobile Container Wrapper */}
        <div className="md:hidden relative w-full mt-10 rounded-[32px] p-[1px] bg-gradient-to-b from-cyan-400/50 via-blue-500/50 to-cyan-400/50 shadow-[0_0_40px_rgba(59,130,246,0.15)] group">
          
          {/* Inner Content */}
          <div className="relative z-10 flex flex-col items-center justify-between w-full p-8 rounded-[31px] bg-white dark:bg-slate-950 space-y-12 pb-16">
            
            {/* Background Connecting Line (Mobile) */}
            <div className="absolute left-1/2 top-[40px] bottom-[40px] w-1 bg-slate-200/50 dark:bg-slate-700/50 -translate-x-1/2 rounded-full" >
               {/* Animated Particle (Mobile) */}
               <motion.div
                 animate={{ top: ["0%", "100%"], opacity: [0, 1, 1, 1, 0] }}
                 transition={{ repeat: Infinity, duration, ease: "linear", times: [0, 0.05, 0.5, 0.95, 1] }}
                 className="absolute left-1/2 -translate-x-1/2 z-20 flex flex-col items-center h-16 -mt-8 drop-shadow-[0_0_8px_rgba(var(--primary),0.8)]"
               >
                 {/* Blurry rectangular tail (vertical) */}
                 <div className="flex-1 w-1.5 bg-gradient-to-b from-transparent to-primary blur-[1px] rounded-t-full" />
                 {/* Arrow head pointing down */}
                 <div className="w-0 h-0 border-x-[6px] border-x-transparent border-t-[10px] border-t-primary" />
               </motion.div>
            </div>

            {nodes.map((node, index) => (
              <div key={node.id} className="relative z-10 flex flex-col items-center">
                <motion.div 
                  animate={nodeAnimations[index]}
                  transition={{ repeat: Infinity, duration, ease: "linear" }}
                  className="w-16 h-16 flex items-center justify-center rounded-2xl border-[3px] bg-white/80 dark:bg-slate-900/80 backdrop-blur-md relative z-30"
                >
                  <node.icon size={24} color={node.iconColor} />
                </motion.div>
                <div className="mt-3 text-sm font-bold text-slate-700 dark:text-slate-200 text-center">
                  {node.label}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </section>
  );
}
