import React from "react";
import { AlertTriangle, TrendingUp, Radar } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function OutbreakAlert({ clusters = [] }) {
  if (clusters.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-navy-50 p-6 shadow-sm flex flex-col items-center justify-center text-center h-[200px]">
        <div className="w-12 h-12 bg-teal-light rounded-full flex items-center justify-center mb-3">
          <Radar size={20} className="text-teal" />
        </div>
        <h3 className="font-display font-bold text-navy-800">No Outbreaks Detected</h3>
        <p className="text-sm text-navy-400 mt-1">Public Health Intelligence Agent is monitoring live data.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-navy-50 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4 border-b border-navy-50 pb-4">
         <Radar size={18} className="text-coral animate-pulse" />
         <h3 className="font-display font-bold text-navy-900">Active Health Alerts</h3>
         <span className="ml-auto bg-coral text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-sm shadow-coral/30">
           {clusters.length}
         </span>
      </div>

      <div className="space-y-4">
        <AnimatePresence>
          {clusters.map((cluster, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: i * 0.1 }}
              className="relative overflow-hidden border border-coral/30 bg-gradient-to-r from-coral-light/40 to-white rounded-xl p-4 shadow-sm group hover:border-coral/60 transition-colors"
            >
              {/* Decorative side accent */}
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-coral"></div>

              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 bg-coral-light rounded-lg text-coral shrink-0 mt-1">
                  <AlertTriangle size={18} />
                </div>
                <div>
                  <h4 className="font-display font-semibold text-coral-700 leading-tight">
                    Possible outbreak in {cluster.location_name}
                  </h4>
                  <p className="text-xs text-coral/80 font-medium mt-1">
                    {cluster.matching_cases} of {cluster.total_cases} recent cases match <span className="font-bold underline decoration-coral/30 underline-offset-2">{cluster.pattern.replace(/_/g, " ")}</span>
                  </p>
                </div>
              </div>

              {cluster.predicted_next_hotspot && (
                <div className="ml-11 mb-3 bg-white/60 rounded-lg p-3 border border-coral/10 flex items-center gap-3">
                  <TrendingUp size={16} className="text-amber-500" />
                  <p className="text-[11px] text-navy-700 font-medium">
                    Predicted next hotspot: <strong className="text-amber-600">{cluster.predicted_next_hotspot.location_name}</strong>{" "}
                    <span className="text-navy-400">({cluster.predicted_next_hotspot.distance_km} km away)</span>
                  </p>
                </div>
              )}

              <div className="ml-11">
                <h5 className="text-[10px] font-bold text-coral/60 uppercase tracking-wider mb-1.5">Action Plan</h5>
                <ul className="text-xs text-navy-600 space-y-1.5">
                  {cluster.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="mt-1 flex-shrink-0 h-1.5 w-1.5 rounded-full bg-coral/40"></span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
