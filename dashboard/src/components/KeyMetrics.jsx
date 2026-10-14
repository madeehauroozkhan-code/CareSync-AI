import React from "react";
import { AlertCircle, AlertTriangle, Clock, Activity, Users } from "lucide-react";
 
/**
 * KeyMetrics
 * ------------
 * The top KPI row. All numbers are derived client-side from data already
 * fetched for other panels (cases + hospitals) -- no extra API calls needed.
 */
export default function KeyMetrics({ cases = [], hospitals = [], clusters = [] }) {
  const activeCritical = cases.filter((c) => c.urgency === "Critical").length;
  const hospitalsFull = hospitals.filter((h) => h.status === "Near Full").length;
 
  const recentCases = cases.filter((c) => Date.now() / 1000 - c.timestamp < 86400);
  const avgEtaSeconds = recentCases.length
    ? Math.round(recentCases.reduce((sum, c) => sum + (c.eta_minutes || 3), 0) / recentCases.length * 60)
    : 0;
  const avgEtaLabel = avgEtaSeconds ? `${Math.floor(avgEtaSeconds / 60)}m ${avgEtaSeconds % 60}s` : "—";
 
  const metrics = [
    { label: "Active Critical", value: activeCritical, sub: "Unresolved cases", icon: AlertCircle, color: "text-coral" },
    { label: "Hospitals Full", value: hospitalsFull, sub: ">85% capacity", icon: AlertTriangle, color: "text-amber-600" },
    { label: "Avg Response", value: avgEtaLabel, sub: "Last 24 hours", icon: Clock, color: "text-navy" },
    { label: "Outbreak Alerts", value: clusters.length, sub: "Active clusters", icon: Activity, color: "text-teal" },
    { label: "Cases Today", value: cases.length, sub: "Total volume", icon: Users, color: "text-teal" },
  ];
 
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {metrics.map((m) => (
        <div key={m.label} className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{m.label}</span>
            <m.icon size={16} className={m.color} />
          </div>
          <p className="text-2xl font-bold text-gray-800">{m.value}</p>
          <p className="text-xs text-gray-400 mt-0.5">{m.sub}</p>
        </div>
      ))}
    </div>
  );
}
