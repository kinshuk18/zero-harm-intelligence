import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ShieldAlert, CheckCircle, Activity, Server, AlertTriangle } from 'lucide-react';

export default function App() {
  const [systemStatus, setSystemStatus] = useState('STANDBY');
  const [assessment, setAssessment] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch history on load
  useEffect(() => {
    fetchAuditTrail();
  }, []);

  const fetchAuditTrail = async () => {
    try {
      const res = await axios.get('/api/v1/audit-trail');
      setAuditLog(res.data.history || []);
    } catch (err) {
      console.error("Failed to load audit trail", err);
    }
  };

  const triggerSimulation = async (scenario) => {
    setLoading(true);
    let payload = {};
    
    if (scenario === 'safe') {
      payload = {
        zone_id: "ZONE_CO4",
        gas_pressure_psi: 48.5,
        methane_ppm: 8.2,
        temperature_c: 42.1,
        hot_work_permit_active: 0,
        confined_space_entry: 0,
        cctv_metadata: [{"class": "worker", "bbox": [0.1, 0.1, 0.3, 0.4]}]
      };
    } else {
      payload = {
        zone_id: "ZONE_BF1",
        gas_pressure_psi: 55.0,
        methane_ppm: 112.4,
        temperature_c: 46.8,
        hot_work_permit_active: 1,
        confined_space_entry: 0,
        cctv_metadata: [{"class": "worker", "bbox": [0.7, 0.7, 0.9, 0.9]}] // Proximity breach
      };
    }

    try {
      const res = await axios.post('/api/v1/assess-risk', payload);
      setAssessment(res.data);
      setSystemStatus(res.data.status);
      if (res.data.critical_risk_flag === 1) {
        fetchAuditTrail(); // Refresh log if critical
      }
    } catch (err) {
      console.error(err);
      setSystemStatus('OFFLINE');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-industrial-900 p-8 font-mono">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-wider flex items-center gap-3">
            <Server className="text-industrial-accent" />
            ZERO-HARM INTELLIGENCE
          </h1>
          <p className="text-gray-400 mt-1">Autonomous Multimodal Safety Orchestrator</p>
        </div>
        <div className={`px-4 py-2 rounded-full font-bold flex items-center gap-2 ${systemStatus === 'CRITICAL_HAZARD_DETECTED' ? 'bg-red-500 animate-pulse' : 'bg-green-600'}`}>
          {systemStatus === 'CRITICAL_HAZARD_DETECTED' ? <AlertTriangle size={20} /> : <CheckCircle size={20} />}
          {systemStatus}
        </div>
      </header>

      {/* Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Col: Controls & Live Feed */}
        <div className="space-y-6">
          <div className="bg-industrial-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl text-industrial-accent font-semibold mb-4 flex items-center gap-2">
              <Activity size={20} /> Manual Telemetry Override
            </h2>
            <div className="flex gap-4">
              <button 
                onClick={() => triggerSimulation('safe')}
                disabled={loading}
                className="flex-1 bg-gray-700 hover:bg-gray-600 p-3 rounded font-bold transition-all disabled:opacity-50"
              >
                Inject Safe Payload
              </button>
              <button 
                onClick={() => triggerSimulation('critical')}
                disabled={loading}
                className="flex-1 bg-red-900 hover:bg-red-800 border border-red-500 p-3 rounded font-bold transition-all disabled:opacity-50"
              >
                Inject Compound Hazard
              </button>
            </div>
          </div>

          {/* Assessment Output */}
          {assessment && (
            <div className="bg-industrial-800 p-6 rounded-lg border border-gray-700">
              <h2 className="text-xl text-gray-300 font-semibold mb-4">Edge AI Evaluation</h2>
              <div className="space-y-3">
                <div className="flex justify-between border-b border-gray-700 pb-2">
                  <span className="text-gray-400">Risk Probability (PyTorch)</span>
                  <span className={`font-bold ${assessment.risk_probability > 0.5 ? 'text-red-400' : 'text-green-400'}`}>
                    {(assessment.risk_probability * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between border-b border-gray-700 pb-2">
                  <span className="text-gray-400">Target Zone</span>
                  <span className="font-bold text-white">{assessment.geospatial_context.zone_name}</span>
                </div>
                <div className="flex justify-between border-b border-gray-700 pb-2">
                  <span className="text-gray-400">CCTV Vision Anomaly</span>
                  <span className={`font-bold ${assessment.vision_analytics_context.hazard_zone_proximity_violation ? 'text-red-400' : 'text-green-400'}`}>
                    {assessment.vision_analytics_context.hazard_zone_proximity_violation ? "DETECTED" : "CLEAR"}
                  </span>
                </div>
                <div className="flex justify-between pb-2">
                  <span className="text-gray-400">Automated Mitigation</span>
                  <span className="font-bold text-yellow-400 text-right">{assessment.geospatial_context.mitigation_protocol}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Middle/Right Col: GenAI Report & History */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* GenAI Report Panel */}
          {assessment?.critical_risk_flag === 1 && (
            <div className="bg-red-950/40 p-6 rounded-lg border-l-4 border-red-500 backdrop-blur-sm">
              <h2 className="text-xl text-red-400 font-semibold mb-4 flex items-center gap-2">
                <ShieldAlert size={20} /> Autonomous GenAI Regulatory Report (Gemini 3.5)
              </h2>
              <div className="bg-black/50 p-4 rounded text-sm text-gray-300 whitespace-pre-wrap font-mono leading-relaxed h-64 overflow-y-auto">
                {assessment.autonomous_incident_report || "Generating..."}
              </div>
            </div>
          )}

          {/* Audit Ledger */}
          <div className="bg-industrial-800 p-6 rounded-lg border border-gray-700">
            <h2 className="text-xl text-industrial-accent font-semibold mb-4 flex items-center gap-2">
              <Server size={20} /> Immutable Audit Ledger
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-gray-400">
                <thead className="text-xs text-gray-300 uppercase bg-gray-700">
                  <tr>
                    <th className="px-4 py-3">Timestamp</th>
                    <th className="px-4 py-3">Entry ID</th>
                    <th className="px-4 py-3">Zone</th>
                    <th className="px-4 py-3">Risk Level</th>
                  </tr>
                </thead>
                <tbody>
                  {auditLog.map((log, idx) => (
                    <tr key={idx} className="border-b border-gray-700">
                      <td className="px-4 py-3">{log.logged_timestamp}</td>
                      <td className="px-4 py-3 font-mono text-yellow-500">{log.entry_id}</td>
                      <td className="px-4 py-3">{log.zone_id}</td>
                      <td className="px-4 py-3 text-red-400 font-bold">{(log.risk_probability * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                  {auditLog.length === 0 && (
                    <tr>
                      <td colSpan="4" className="px-4 py-4 text-center">No critical breaches logged in current session.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}