import React from "react";
 
const STATUS_STYLES = {
  "Near Full": "bg-coral/10 text-coral",
  "Moderate": "bg-amber-100 text-amber-700",
  "Available": "bg-teal/10 text-teal",
};
 
const BAR_COLOR = {
  "Near Full": "bg-coral",
  "Moderate": "bg-amber-500",
  "Available": "bg-teal",
};
 
/**
 * HospitalTable
 * ---------------
 * IMPORTANT: this reads from GET /dashboard/hospitals, NOT from the raw
 * mock_hospitals.json file. That endpoint guarantees these exact field
 * names: id, name, occupied_beds, total_beds, icu_beds_available,
 * occupancy_pct, status -- so there's no risk of the blank-name / NaN-ICU
 * bug that comes from importing the raw JSON and expecting different
 * field names (e.g. "hospital_name" or "icu_free").
 */
export default function HospitalTable({ hospitals = [] }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h3 className="font-semibold text-navy text-sm">Hospital Capacity</h3>
        <p className="text-xs text-gray-400">Live bed availability across the network</p>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-gray-400 border-b border-gray-100">
            <th className="px-4 py-2 font-medium">Hospital</th>
            <th className="px-4 py-2 font-medium">Occupied / Total</th>
            <th className="px-4 py-2 font-medium">ICU Free</th>
            <th className="px-4 py-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {hospitals.map((h) => (
            <tr key={h.id} className="border-b border-gray-50 last:border-0">
              <td className="px-4 py-3 font-medium text-gray-800">{h.name}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="text-gray-600 text-xs w-16">{h.occupied_beds}/{h.total_beds}</span>
                  <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden max-w-[100px]">
                    <div
                      className={`h-full rounded-full ${BAR_COLOR[h.status]}`}
                      style={{ width: `${h.occupancy_pct}%` }}
                    />
                  </div>
                </div>
              </td>
              <td className="px-4 py-3 text-gray-600">{h.icu_beds_available}</td>
              <td className="px-4 py-3">
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${STATUS_STYLES[h.status]}`}>
                  {h.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
