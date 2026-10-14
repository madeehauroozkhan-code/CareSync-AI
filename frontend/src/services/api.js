/**
 * api.js
 * --------
 * All calls to the AI Sahayak backend go through this file. Keeping every
 * fetch call in one place means the base URL only has to be changed here
 * if the backend moves (e.g. from localhost to a deployed Render URL).
 *
 * NOTE: backend-stable mounts every route under /api/v1 (see
 * backend/api/v1/router.py -> APIRouter(prefix="/api/v1")). Always keep
 * that prefix here.
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

// Matches backend/api/v1/chat.py -> POST /api/v1/chat
export async function sendChatMessage({ message, lat, lng, age = null, disasterMode = false, sessionId = null }) {
  const response = await fetch(`${API_V1}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      lat,
      lng,
      age,
      disaster_mode: disasterMode,
      session_id: sessionId,
    }),
  });
  return handleResponse(response);
}

// Matches backend/api/v1/emergency.py -> POST /api/v1/emergency/simulate
// IMPORTANT: backend expects a JSON body (Pydantic model), NOT a query param.
export async function simulateDisaster(numCases = 20, disasterType = "flood", region = "Patna") {
  const response = await fetch(`${API_V1}/emergency/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      num_cases: numCases,
      disaster_type: disasterType,
      region: region,
    }),
  });
  return handleResponse(response);
}

// Matches backend/api/v1/dashboard.py -> GET /api/v1/dashboard/cases
export async function getDashboardCases() {
  const response = await fetch(`${API_V1}/dashboard/cases`);
  return handleResponse(response);
}

// Matches backend/api/v1/dashboard.py -> GET /api/v1/dashboard/outbreaks
export async function getOutbreakAlerts() {
  const response = await fetch(`${API_V1}/dashboard/outbreaks`);
  return handleResponse(response);
}

// Matches backend/api/v1/health.py -> GET /api/v1/health
export async function getHealthStatus() {
  const response = await fetch(`${API_V1}/health`);
  return handleResponse(response);
}

/**
 * respondToFollowup, submitIntake, submitTriage, submitCareCoordination
 * REMOVED: these have no corresponding route in backend-stable.
 * The whole intake -> triage -> care pipeline now runs internally,
 * inside the single /api/v1/chat call via PlannerOrchestrator.
 * If you need a standalone follow-up endpoint, it must be added to the
 * backend first (see "File 2" below) before this frontend function is
 * re-added.
 */
