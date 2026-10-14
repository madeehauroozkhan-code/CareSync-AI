import React from "react";
import { motion } from "framer-motion";
import { MapPin, Clock, Building2, CheckCircle2 } from "lucide-react";

export default function StatusTracker({ coordinationResult }) {
  if (!coordinationResult?.selected_hospital) return null;

  const hospital = coordinationResult.selected_hospital;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl p-5 shadow-glass-hover hover:shadow-lg transition-all"
    >
      <div className="flex items-center gap-3 mb-4 border-b border-slate-50 dark:border-slate-700/50 pb-3">
        <div className="p-2 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg text-emerald-600 dark:text-emerald-400">
          <Building2 size={20} />
        </div>
        <div>
          <span className="font-semibold text-slate-900 dark:text-slate-100 block">{hospital.hospital_name}</span>
          <span className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Optimal Match Found</span>
        </div>
        <div className="ml-auto flex flex-col items-end">
           <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">Match Score</span>
           <span className="text-sm font-bold text-slate-700 dark:text-slate-200">{hospital.score}</span>
        </div>
      </div>

      <div className="flex items-center gap-6 text-sm text-slate-600 dark:text-slate-300 mb-4 bg-slate-50/50 dark:bg-slate-700/30 p-3 rounded-xl border border-slate-50 dark:border-slate-700/50">
        <span className="flex items-center gap-2 font-medium">
          <Clock size={16} className="text-orange-500" /> ~{hospital.eta_minutes} min ETA
        </span>
        <span className="flex items-center gap-2 font-medium">
          <MapPin size={16} className="text-red-500" /> {hospital.distance_km} km away
        </span>
      </div>

      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">Coordination Reasoning</h4>
        {hospital.reasons.map((reason, i) => (
          <motion.p
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className="text-sm text-slate-700 dark:text-slate-300 flex items-start gap-2"
          >
            <CheckCircle2 size={16} className="text-emerald-500 dark:text-emerald-400 shrink-0 mt-0.5" />
            <span>{reason}</span>
          </motion.p>
        ))}
      </div>

      {coordinationResult.fallback_note && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-4 text-xs text-red-700 dark:text-red-400 bg-red-50/50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-lg p-3 flex gap-2"
        >
          <span className="font-bold">Note:</span> {coordinationResult.fallback_note}
        </motion.div>
      )}
    </motion.div>
  );
}
