import React, { useEffect, useState, useRef } from "react";
import { RotateCcw } from "lucide-react";
import MapView from "./components/MapView.jsx";
import CaseList from "./components/CaseList.jsx";
import OutbreakAlert from "./components/OutbreakAlert.jsx";
import HospitalTable from "./components/HospitalTable.jsx";
import KeyMetrics from "./components/KeyMetrics.jsx";
import LiveAgentTrace from "./components/LiveAgentTrace.jsx";
import { getDashboardCases, getOutbreakAlerts, getDashboardHospitals, getDashboardVolunteers, simulateDisaster, simulateOutbreak, resetDashboard } from "./services/api.js";
 
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace("http", "ws") + "/api/v1/dashboard/ws/live-feed";
 
export default function App() {
  const [cases, setCases] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [agentSteps, setAgentSteps] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isSimulatingOutbreak, setIsSimulatingOutbreak] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
 
  const refreshData = async () => {
    try {
      const [caseData, outbreakData, hospitalData, volunteerData] = await Promise.all([
        getDashboardCases(),
        getOutbreakAlerts(),
        getDashboardHospitals(),
        getDashboardVolunteers(),
      ]);
      setCases(caseData.cases || []);
      setClusters(outbreakData.clusters || []);
      setHospitals(hospitalData.hospitals || []);
      setVolunteers(volunteerData.volunteers || []);
    } catch (err) {
      console.error("Failed to refresh dashboard data:", err);
    }
  };
 
  // Initial load + slow polling fallback for hospitals/outbreaks (these
  // don't need to be instant -- the WebSocket handles the truly live parts).
  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 10000);
    return () => clearInterval(interval);
  }, []);
 
  // WebSocket connection -- this is what makes Live Feed and Live Agent
  // Trace update the instant a case is processed, no polling needed.
  useEffect(() => {
    let ws;
    let reconnectTimeout;
    let isUnmounted = false;

    const connect = () => {
      ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => setIsConnected(true);

      ws.onclose = () => {
        setIsConnected(false);
        if (!isUnmounted) {
          // Backend restart / network blip ke baad 3 second me retry karo
          reconnectTimeout = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => {
        setIsConnected(false);
        ws.close(); // triggers onclose -> retry
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.event === "case_processed") {
          setCases((prev) => [data.case, ...prev].slice(0, 200));
          setAgentSteps(data.agent_trace || []);
          getDashboardHospitals().then((res) => setHospitals(res.hospitals || []));
        } else if (data.event === "dashboard_reset") {
          setCases([]);
          setAgentSteps([]);
        }
      };
    };

    connect();

    return () => {
      isUnmounted = true;
      clearTimeout(reconnectTimeout);
      // Guard: only close if the socket actually opened, prevents
      // "WebSocket closed before connection established" in React StrictMode
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);
 
  const handleSimulateDisaster = async () => {
    setIsSimulating(true);
    setAgentSteps([]);
    try {
      await simulateDisaster(20);
      await refreshData();
    } catch (err) {
      console.error("Disaster simulation failed:", err);
    } finally {
      setIsSimulating(false);
    }
  };
 
  const handleSimulateOutbreak = async () => {
    setIsSimulatingOutbreak(true);
    setAgentSteps([]);
    try {
      await simulateOutbreak(15);
      await refreshData();
    } catch (err) {
      console.error("Outbreak simulation failed:", err);
    } finally {
      setIsSimulatingOutbreak(false);
    }
  };
 
  return (
    <div className="min-h-screen px-6 py-8 max-w-7xl mx-auto space-y-6">
      <div className="bg-white rounded-2xl border border-gray-200 p-6 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-navy">AI Sahayak Command Center</h1>
            <span
              className={`text-xs font-medium px-2 py-1 rounded-full flex items-center gap-1 ${
                isConnected ? "bg-teal/10 text-teal" : "bg-gray-100 text-gray-400"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? "bg-teal" : "bg-gray-400"}`} />
              {isConnected ? "SYSTEM ONLINE" : "CONNECTING..."}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">Real-time resource and outbreak monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={async () => { await resetDashboard(); }}
            className="flex items-center gap-1.5 bg-gray-100 text-gray-600 text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-200"
          >
            <RotateCcw size={14} /> Reset Demo
          </button>
          <button
            onClick={handleSimulateOutbreak}
            disabled={isSimulatingOutbreak}
            className="bg-amber-600 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
          >
            {isSimulatingOutbreak ? "Simulating..." : "Simulate Outbreak"}
          </button>
          <button
            onClick={handleSimulateDisaster}
            disabled={isSimulating}
            className="bg-coral text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
          >
            {isSimulating ? "Simulating..." : "Simulate Flood Event"}
          </button>
        </div>
      </div>
 
      <KeyMetrics cases={cases} hospitals={hospitals} clusters={clusters} />
 
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <MapView hospitals={hospitals} cases={cases} volunteers={volunteers} />
          <HospitalTable hospitals={hospitals} />
          <OutbreakAlert clusters={clusters} />
        </div>
        <div className="space-y-6 md:col-span-2 lg:col-span-1">
          <CaseList cases={cases} />
          <LiveAgentTrace steps={agentSteps} />
        </div>
      </div>
    </div>
  );
}
