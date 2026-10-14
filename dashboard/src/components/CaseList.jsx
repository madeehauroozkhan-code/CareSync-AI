import React, { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity } from "lucide-react";
 
const URGENCY_COLORS = {
  Critical: "bg-coral/10 text-coral",
  Urgent: "bg-amber-100 text-amber-700",
  Routine: "bg-teal/10 text-teal",
};
 
const MAX_VISIBLE_CASES = 50;
 
/**
 * CaseList ("Live Feed")
 * ------------------------
 * FIX: this panel now has a fixed height with its own internal scrollbar
 * (overflow-y-auto on a height-capped div), and the list is capped at
 * MAX_VISIBLE_CASES entries. Previously this list had no height limit, so
 * during the disaster simulation (20-140 cases) it grew the entire page
 * taller and taller -- which is why the page kept "jumping" and growing
 * every time a new case arrived. Now new cases appear inside this box
 * only; the page height never changes because of incoming cases.
 */
export default function CaseList({ cases = [] }) {
  const containerRef = useRef(null);

  // Parse timestamp — handles epoch seconds, epoch ms, ISO strings, or null
  const parseTs = (ts) => {
    if (!ts) return 0;
    if (typeof ts === "number") return ts < 1e12 ? ts : ts / 1000; // epoch s vs ms
    return new Date(ts).getTime() / 1000 || 0; // ISO string
  };

  const sorted = [...cases]
    .sort((a, b) => parseTs(b.timestamp) - parseTs(a.timestamp))
    .slice(0, MAX_VISIBLE_CASES);
 
  // New cases are prepended (newest first), so we keep the box scrolled to
  // the top when a new one arrives -- scrolling this box only, never the page.
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = 0;
    }
  }, [cases.length]);
 
  // Format time for display — handles all timestamp types
  const formatTime = (ts) => {
    if (!ts) return "Just now";
    const epochMs = typeof ts === "number"
      ? (ts < 1e12 ? ts * 1000 : ts)
      : new Date(ts).getTime();
    if (isNaN(epochMs)) return "Just now";
    return new Date(epochMs).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity size={14} className="text-teal" />
          <h3 className="font-semibold text-navy text-sm">Live Feed</h3>
        </div>
        <span className="text-xs bg-gray-100 text-gray-500 font-medium px-2 py-0.5 rounded-full">
          {cases.length} Cases
        </span>
      </div>
 
      {/* h-[420px] + overflow-y-auto = fixed box, internal scroll only */}
      <div ref={containerRef} className="h-[420px] overflow-y-auto divide-y divide-gray-50">
        {sorted.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center px-6">
            <p className="text-sm text-gray-400">Monitoring for incoming cases...</p>
          </div>
        )}
        <AnimatePresence initial={false}>
          {sorted.map((c) => (
            <motion.div
              key={c.case_id}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.25 }}
              className="px-4 py-3"
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${URGENCY_COLORS[c.urgency] || "bg-gray-100 text-gray-600"}`}>
                  {c.urgency?.toUpperCase()}
                </span>
                <span className="text-xs text-gray-400">
                  {formatTime(c.timestamp)}
                </span>
              </div>
              <p className="text-sm font-semibold text-gray-800">{c.location_name || c.region || "Unknown location"}</p>
              <p className="text-xs text-gray-500">
                {(c.symptom_tags || c.symptoms || []).join(", ").replace(/_/g, " ") || "no symptoms recorded"}
              </p>
              {c.hospital_name && (
                <p className="text-xs text-teal mt-0.5">→ {c.hospital_name}</p>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
