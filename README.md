# Zero-Harm Industrial Intelligence (ET AI Hackathon 2026)

An AI-powered industrial safety intelligence platform designed to transition heavy industries from reactive monitoring to proactive, evidence-based intervention. 

This platform fuses real-time SCADA telemetry, computer vision metadata, and geospatial routing with a Gemini-powered Generative AI orchestrator to predict compound hazards and autonomously generate regulatory compliance reports.

## System Architecture

Our solution addresses the **Compound Risk Detection** and **Emergency Response Orchestrator** requirements of the problem statement via a multi-layered intelligence engine.

1.  **SCADA Risk Engine:** A PyTorch neural network trained on time-series telemetry (methane, pressure, temperature) and administrative states (hot work permits, confined space entry).
2.  **Geospatial Safety Router:** Maps sensor payloads to physical facility zones, attaching dynamic evacuation radii and containment protocols.
3.  **Vision Analytics Processor:** Ingests bounding-box metadata from CCTV feeds to identify physical proximity violations in hazardous zones.
4.  **Autonomous Incident Orchestrator:** Utilizes `gemini-3.5-flash` to intercept critical hazard flags and generate structured, Factory Act/OISD compliant incident reports in real-time.
5.  **Immutable Audit Ledger:** Persists all autonomous mitigation actions and compliance data to a structured timeline for historical analysis.

## API Documentation (For Frontend Integration)

The backend is served via FastAPI. To run the server locally:
\`\`\`bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.api.main:app --reload --port 8000
\`\`\`

### 1. Live Telemetry & Risk Assessment
**POST** `/api/v1/assess-risk`

**Request Payload Example:**
\`\`\`json
{
  "zone_id": "ZONE_BF1",
  "gas_pressure_psi": 55.0,
  "methane_ppm": 112.4,
  "temperature_c": 46.8,
  "hot_work_permit_active": 1,
  "confined_space_entry": 0,
  "cctv_metadata": [{"class": "worker", "bbox": [0.2, 0.2, 0.8, 0.9]}]
}
\`\`\`

**Response Payload Example:**
\`\`\`json
{
  "risk_probability": 0.9997,
  "critical_risk_flag": 1,
  "status": "CRITICAL_HAZARD_DETECTED",
  "geospatial_context": { ... },
  "vision_analytics_context": { ... },
  "autonomous_incident_report": "**PRELIMINARY INCIDENT REPORT**\n..."
}
\`\`\`

### 2. Historical Audit Trail
**GET** `/api/v1/audit-trail`
Returns an array of all historical critical breaches and the corresponding autonomous mitigation steps taken.