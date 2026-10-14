import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
 
/**
 * LiveAgentTrace
 * -----------------
 * Mirrors what the backend terminal prints (conversation_logger.py) but
 * inside the dashboard itself.
 *
 * IMPORTANT FIX: this used to call scrollRef.current?.scrollIntoView(),
 * which scrolls the nearest scrollable ancestor -- and when the page
 * itself is taller than the viewport, that ancestor is the whole window,
 * not this panel. That's what was causing the entire dashboard page to
 * jump/scroll every time a new step arrived. Fixed by scrolling only this
 * panel's own internal container (containerRef.scrollTop), which never
 * touches the page's scroll position.
 */
export default function LiveAgentTrace({ steps = [] }) {
  const containerRef = useRef(null);
 
  useEffect(() => {
    const el = containerRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [steps]);
 
  return (
    <div className="bg-[#0d1117] rounded-xl border border-gray-800 overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-gray-800">
        <span className="text-gray-500 text-xs font-mono">{">_"}</span>
        <span className="text-gray-300 text-xs font-semibold tracking-wide">LIVE AGENT TRACE</span>
        <div className="ml-auto flex gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500/70" />
          <div className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
          <div className="w-2.5 h-2.5 rounded-full bg-green-500/70" />
        </div>
      </div>
 
      {/* Fixed height + overflow-y-auto means this box scrolls internally
          only -- it can never grow the page or drag the window scroll
          position along with it. */}
      <div ref={containerRef} className="p-4 h-[260px] overflow-y-auto font-mono text-xs space-y-2">
        {steps.length === 0 && (
          <p className="text-gray-600 italic">Waiting for agent activity...</p>
        )}
        <AnimatePresence>
          {steps.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15 }}
            >
              <span className="text-gray-500">{step.icon}</span>{" "}
              <span className="text-teal-400 font-semibold">{step.agent}</span>{" "}
              <span className="text-gray-500">→</span>{" "}
              <span className="text-gray-300">{step.message}</span>
              {step.detail && (
                <div className="text-gray-600 pl-6">{step.detail}</div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
