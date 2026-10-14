/**
 * RedistributionView Component
 * ==============================
 * Shows live hospital redistribution during emergency events.
 * Displays which hospitals are redirecting cases and to where.
 */

import './RedistributionView.css';

function RedistributionView({ redistributions, alertLevel }) {
  const isActive = redistributions && redistributions.length > 0;

  return (
    <div className={`redistribution-view ${isActive ? 'active' : ''}`}>
      <div className="redistribution-header">
        <h3>🔄 Redistribution Status</h3>
        <span className={`alert-badge alert-${alertLevel || 'normal'}`}>
          {(alertLevel || 'normal').toUpperCase()}
        </span>
      </div>

      {!isActive ? (
        <div className="no-redistribution">
          <p>✅ All hospitals operating normally</p>
          <p className="sub-text">No redistribution needed</p>
        </div>
      ) : (
        <div className="redistribution-list">
          {redistributions.map((r, index) => (
            <div key={index} className="redistribution-item">
              <div className="redistribution-flow">
                <div className="hospital-from">
                  <span className="hospital-label">FROM</span>
                  <span className="hospital-name">{r.from_hospital_name}</span>
                </div>
                <div className="flow-arrow">
                  <span className="arrow">→</span>
                  <span className="case-count">{r.cases_to_redirect} cases</span>
                </div>
                <div className="hospital-to">
                  <span className="hospital-label">TO</span>
                  <span className="hospital-name">{r.to_hospital_name}</span>
                </div>
              </div>
              <p className="redistribution-reason">{r.reason}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RedistributionView;
