/**
 * DashboardPage — Main Admin Dashboard
 * =======================================
 * Combines MapView, CaseList, OutbreakAlert, and RedistributionView
 * into a comprehensive admin panel for monitoring the healthcare system.
 */

import { useState, useEffect } from 'react';
import MapView from '../components/MapView';
import CaseList from '../components/CaseList';
import OutbreakAlert from '../components/OutbreakAlert';
import RedistributionView from '../components/RedistributionView';
import { getDashboardOverview, simulateDisaster } from '../services/api';
import './DashboardPage.css';

function DashboardPage() {
  const [overview, setOverview] = useState(null);
  const [hospitals, setHospitals] = useState([]);
  const [cases, setCases] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [redistributions, setRedistributions] = useState([]);
  const [alertLevel, setAlertLevel] = useState('normal');
  const [isSimulating, setIsSimulating] = useState(false);

  // Fetch dashboard data on mount and poll every 3 seconds
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await getDashboardOverview();
      setOverview(data);
      
      const casesData = await import('../services/api').then(m => m.getCases());
      setCases(casesData);
      
      const mapData = await import('../services/api').then(m => m.getMapData());
      setHospitals(mapData.hospitals || []);
      
      const redistributionData = await import('../services/api').then(m => m.getRedistributionData());
      setRedistributions(redistributionData.active_redistributions || []);
      
      try {
        const alertsData = await import('../services/api').then(m => m.getOutbreakAlerts());
        setAlerts(alertsData.clusters_detected || []);
      } catch (e) {
        // Ignore if endpoint not yet fully implemented
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const handleSimulateDisaster = async () => {
    setIsSimulating(true);
    try {
      const result = await simulateDisaster('flood', 'Patna East', 50);
      // TODO: Update dashboard state with simulation results
      setAlertLevel(result.alert_level || 'critical');
      setRedistributions(result.redistributions || []);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="dashboard-page">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🩺 AI Sahayak — Admin Dashboard</h1>
          <p>Healthcare Coordination Command Center</p>
        </div>
        <div className="header-actions">
          <button
            className="simulate-btn"
            onClick={handleSimulateDisaster}
            disabled={isSimulating}
          >
            {isSimulating ? '⏳ Simulating...' : '🌊 Simulate Flood Event'}
          </button>
        </div>
      </header>

      {/* Stats Overview */}
      <section className="stats-row">
        <div className="stat-card">
          <span className="stat-icon">📊</span>
          <div>
            <span className="stat-number">{overview?.total_cases_today || 0}</span>
            <span className="stat-label">Cases Today</span>
          </div>
        </div>
        <div className="stat-card critical">
          <span className="stat-icon">🔴</span>
          <div>
            <span className="stat-number">{overview?.cases_by_urgency?.critical || 0}</span>
            <span className="stat-label">Critical</span>
          </div>
        </div>
        <div className="stat-card urgent">
          <span className="stat-icon">🟡</span>
          <div>
            <span className="stat-number">{overview?.cases_by_urgency?.urgent || 0}</span>
            <span className="stat-label">Urgent</span>
          </div>
        </div>
        <div className="stat-card routine">
          <span className="stat-icon">🟢</span>
          <div>
            <span className="stat-number">{overview?.cases_by_urgency?.routine || 0}</span>
            <span className="stat-label">Routine</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">⚠️</span>
          <div>
            <span className="stat-number">{overview?.active_alerts || 0}</span>
            <span className="stat-label">Active Alerts</span>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <section className="dashboard-grid">
        <div className="grid-left">
          <MapView
            hospitals={hospitals}
            activeCases={cases}
            volunteers={[]}
            redistributions={redistributions}
          />
          <CaseList cases={cases} />
        </div>
        <div className="grid-right">
          <RedistributionView
            redistributions={redistributions}
            alertLevel={alertLevel}
          />
          <OutbreakAlert alerts={alerts} />
        </div>
      </section>
    </div>
  );
}

export default DashboardPage;
