import React from "react";
import { MapContainer, TileLayer, CircleMarker, Marker, Popup } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
 
/**
 * MapView -- ADVANCED VERSION
 * =============================
 * This map now has THREE independent data layers, each answering a
 * different question for the person watching the dashboard:
 *
 * 1. HOSPITALS (always visible, colored circles)
 *    Answers: "where can patients be treated, and how full are they?"
 *    Color = occupancy: teal (plenty of room) -> amber (filling up)
 *    -> coral/red (near full). Click any hospital for exact numbers.
 *
 * 2. CASES (clustered pins, colored by urgency)
 *    Answers: "where are incoming patients located right now?"
 *    During the disaster simulation this can be 20-140+ points clustered
 *    tightly together -- rendering each one as a separate marker would
 *    make the map unreadable and slow. MarkerClusterGroup automatically
 *    groups nearby pins into a single number-badged circle that expands
 *    as you zoom in, which is the standard solution for "many points in
 *    a small area" on any map product.
 *
 * 3. VOLUNTEERS (small purple markers)
 *    Answers: "who did the Community Liaison agent notify, and where
 *    are they relative to the emergency?"
 *
 * Each layer can be toggled independently by simply not passing that
 * prop -- e.g. omit `cases` entirely on a simpler view.
 */
 
function getHospitalColor(occupiedBeds, totalBeds) {
  const ratio = occupiedBeds / totalBeds;
  if (ratio >= 0.9) return "#B8442F"; // coral/red - near full
  if (ratio >= 0.6) return "#D97706"; // amber - filling up
  return "#1F6F78"; // teal - plenty of capacity
}
 
const URGENCY_COLOR = {
  Critical: "#B8442F",
  Urgent: "#D97706",
  Routine: "#1F6F78",
};
 
// A small custom purple icon for volunteers, built from an inline SVG so
// no external icon image files are needed.
const volunteerIcon = new L.DivIcon({
  html: `<div style="background:#7C3AED;width:10px;height:10px;border-radius:50%;border:2px solid white;box-shadow:0 0 0 1px #7C3AED;"></div>`,
  className: "",
  iconSize: [10, 10],
});
 
export default function MapView({ hospitals = [], cases = [], volunteers = [], center = [25.6, 85.13] }) {
  return (
    <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm">
      <div className="h-[300px] md:h-[400px] lg:h-[450px]">
        <MapContainer center={center} zoom={11} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
 
          {/* Layer 1: Hospitals -- always-visible circles, color = occupancy */}
          {hospitals.map((h) => (
            <CircleMarker
              key={h.id}
              center={[h.lat, h.lng]}
              radius={11}
              pathOptions={{
                color: getHospitalColor(h.occupied_beds, h.total_beds),
                fillColor: getHospitalColor(h.occupied_beds, h.total_beds),
                fillOpacity: 0.75,
                weight: 2,
              }}
            >
              <Popup>
                <strong>{h.name}</strong>
                <br />
                Beds: {h.occupied_beds}/{h.total_beds} occupied
                <br />
                ICU available: {h.icu_beds_available}
                <br />
                Avg wait: {h.avg_wait_time_minutes} min
                <br />
                Status: {h.status}
              </Popup>
            </CircleMarker>
          ))}
 
          {/* Layer 2: Cases -- clustered pins, color = urgency.
              MarkerClusterGroup groups nearby points automatically, so
              100+ disaster-simulation cases stay readable. */}
          {cases.length > 0 && (
            <MarkerClusterGroup chunkedLoading maxClusterRadius={50}>
              {cases.map((c) => (
                <CircleMarker
                  key={c.case_id}
                  center={[c.lat, c.lng]}
                  radius={6}
                  pathOptions={{
                    color: URGENCY_COLOR[c.urgency] || "#999",
                    fillColor: URGENCY_COLOR[c.urgency] || "#999",
                    fillOpacity: 0.8,
                    weight: 1,
                  }}
                >
                  <Popup>
                    <strong>{c.urgency}</strong>
                    <br />
                    {c.location_name || c.region || "Unknown"}
                    <br />
                    {(c.symptom_tags || c.symptoms || []).join(", ").replace(/_/g, " ")}
                    {c.hospital_name && (
                      <>
                        <br />→ {c.hospital_name}
                      </>
                    )}
                  </Popup>
                </CircleMarker>
              ))}
            </MarkerClusterGroup>
          )}
 
          {/* Layer 3: Volunteers -- small purple dots, shown once Community
              Liaison has been activated (disaster mode). */}
          {volunteers.map((v) => (
            <Marker key={v.id} position={[v.lat, v.lng]} icon={volunteerIcon}>
              <Popup>
                <strong>{v.name}</strong>
                <br />
                {v.type}
                <br />
                Skills: {v.skills?.join(", ")}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
 
      {/* Legend -- explains all three layers at a glance */}
      <div className="flex flex-wrap items-center gap-4 px-4 py-2.5 bg-gray-50 border-t border-gray-100 text-xs text-gray-600">
        <span className="font-semibold text-gray-400 uppercase tracking-wide text-[10px]">Legend</span>
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#1F6F78]" /> Hospital: Available</span>
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#D97706]" /> Hospital: Moderate</span>
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#B8442F]" /> Hospital: Near Full</span>
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#7C3AED]" /> Volunteer</span>
        <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full border border-gray-400" /> Case cluster (number = count)</span>
      </div>
    </div>
  );
}
