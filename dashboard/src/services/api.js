/**
 * api.js (dashboard)
 * --------------------
 * Same backend, different consumer: the dashboard reads case history and
 * outbreak data instead of sending new chat messages.
 *
 * NOTE: backend-stable mounts everything under /api/v1 — always keep that
 * prefix here.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_V1 = `${API_BASE_URL}/api/v1`;

async function handleResponse(response) {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText}`);
  }
  return response.json();
}

// GET /api/v1/dashboard/cases
export async function getDashboardCases() {
  const response = await fetch(`${API_V1}/dashboard/cases`);
  return handleResponse(response);
}

// GET /api/v1/dashboard/hospitals  (new route — see backend File 3)
export async function getDashboardHospitals() {
  const response = await fetch(`${API_V1}/dashboard/hospitals`);
  return handleResponse(response);
}

// GET /api/v1/dashboard/volunteers  (new route — see backend File 3)
export async function getDashboardVolunteers() {
  const response = await fetch(`${API_V1}/dashboard/volunteers`);
  return handleResponse(response);
}

// GET /api/v1/dashboard/outbreaks
// Backend's SymptomCluster shape doesn't match what OutbreakAlert.jsx expects. Normalize it here.
export async function getOutbreakAlerts() {
  const response = await fetch(`${API_V1}/dashboard/outbreaks`);
  const data = await handleResponse(response);
  const outbreaks = data.outbreaks || {};
  const rawClusters = outbreaks.clusters_detected || [];
  const recommendations = outbreaks.recommended_actions || [];

  const clusters = rawClusters.map((c) => ({
    location_name: c.region || "Unknown region",
    matching_cases: c.case_count ?? 0,
    total_cases: c.case_count ?? 0, // backend doesn't track a separate "total" yet
    pattern: (c.dominant_symptoms && c.dominant_symptoms.join("_")) || "unclassified_symptoms",
    predicted_next_hotspot: undefined, // backend's predicted_next_regions has no distance_km yet
    recommendations: recommendations,
  }));

  return { clusters };
}

// POST /api/v1/emergency/simulate  (body, not query params)
export async function simulateDisaster(numCases = 20) {
  const response = await fetch(`${API_V1}/emergency/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ num_cases: numCases, disaster_type: "flood", region: "Patna" }),
  });
  return handleResponse(response);
}

// POST /api/v1/emergency/simulate-outbreak  (new route — see backend File 4)
export async function simulateOutbreak(numCases = 15) {
  const response = await fetch(`${API_V1}/emergency/simulate-outbreak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ num_cases: numCases, region: "Patna" }),
  });
  return handleResponse(response);
}

// POST /api/v1/dashboard/reset  (new route — see backend File 3)
export async function resetDashboard() {
  const response = await fetch(`${API_V1}/dashboard/reset`, { method: "POST" });
  return handleResponse(response);
}
