from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import torch
import torch.nn as nn
import numpy as np
import os
import sys

# Ensure backend directory is in path to resolve sibling module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.geospatial_router import get_spatial_context
from models.incident_agent import generate_regulatory_report
from models.vision_processor import analyze_cctv_frame
from models.audit_logger import log_audit_incident, get_audit_trail

app = FastAPI(title="Zero-Harm Industrial Safety Intelligence Engine", version="1.0.0")

# 1. Resolve absolute paths to model binaries dynamically
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(os.path.dirname(current_dir), "models")

model_path = os.path.join(models_dir, "risk_model.pth")
mean_path = os.path.join(models_dir, "scaler_mean.npy")
scale_path = os.path.join(models_dir, "scaler_scale.npy")

# Ensure dependencies exist before boot
if not (os.path.exists(model_path) and os.path.exists(mean_path) and os.path.exists(scale_path)):
    raise FileNotFoundError("API engine execution failed: Required model binary or scaling arrays missing.")

# 2. Re-instantiate Neural Network Architecture matching the training configuration
class CompoundRiskNet(nn.Module):
    def __init__(self, input_dim):
        super(CompoundRiskNet, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)

# Load operational binaries into CPU state memory
input_dim = 5
model = CompoundRiskNet(input_dim)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

scaler_mean = np.load(mean_path)
scaler_scale = np.load(scale_path)

# 3. Request/Response Payload Specifications
class TelemetryPayload(BaseModel):
    zone_id: str = Field(..., example="ZONE_BF1")
    gas_pressure_psi: float = Field(..., example=52.3)
    methane_ppm: float = Field(..., example=12.4)
    temperature_c: float = Field(..., example=46.1)
    hot_work_permit_active: int = Field(..., ge=0, le=1, example=1)
    confined_space_entry: int = Field(..., ge=0, le=1, example=0)
    cctv_metadata: list = Field(default=[], example=[{"class": "worker", "bbox": [0.1, 0.2, 0.7, 0.85]}])

class RiskAssessmentResponse(BaseModel):
    risk_probability: float
    critical_risk_flag: int
    status: str
    geospatial_context: dict
    vision_analytics_context: dict
    autonomous_incident_report: str | None = None

# 4. Inference Route Execution
@app.get("/")
async def root_status():
    return {
        "engine": "Zero-Harm Industrial Safety Intelligence",
        "status": "ACTIVE",
        "supported_routes": ["/health", "/api/v1/assess-risk"]
    }

@app.post("/api/v1/assess-risk", response_model=RiskAssessmentResponse)
async def assess_risk(payload: TelemetryPayload):
    try:
        # Vectorize telemetry components
        raw_features = np.array([[
            payload.gas_pressure_psi,
            payload.methane_ppm,
            payload.temperature_c,
            payload.hot_work_permit_active,
            payload.confined_space_entry
        ]], dtype=np.float32)
        
        # Apply standard scaling transformation mapping
        scaled_features = (raw_features - scaler_mean) / scaler_scale
        tensor_features = torch.tensor(scaled_features, dtype=torch.float32)
        
        # Evaluate tensors through the frozen neural graph
        with torch.no_grad():
            prediction_prob = model(tensor_features).item()
            
        # Determine critical intervention trigger threshold
        critical_flag = 1 if prediction_prob >= 0.5 else 0
        status_message = "CRITICAL_HAZARD_DETECTED" if critical_flag == 1 else "OPERATIONAL_NORMAL"
        
        # Enforce structural geospatial mapping lookup
        spatial_data = get_spatial_context(payload.zone_id, critical_flag)
        
        # Compute vision analytics telemetry data vectors
        vision_data = analyze_cctv_frame(payload.zone_id, payload.cctv_metadata)
        
        # Trigger GenAI Emergency Orchestrator if critical hazard is confirmed
        incident_report = None
        if critical_flag == 1:
            # Aggregate payload data with vision signals for context-rich LLM reporting
            aggregated_payload = payload.model_dump()
            aggregated_payload.update(vision_data)
            incident_report = generate_regulatory_report(aggregated_payload, spatial_data)
        
        response_data = RiskAssessmentResponse(
            risk_probability=round(prediction_prob, 4),
            critical_risk_flag=critical_flag,
            status=status_message,
            geospatial_context=spatial_data,
            vision_analytics_context=vision_data,
            autonomous_incident_report=incident_report
        )
        
        # If a critical incident is confirmed, append it to the audit log asynchronously
        if critical_flag == 1:
            log_payload = response_data.model_dump()
            log_payload["zone_id"] = payload.zone_id
            log_payload["methane_ppm"] = payload.methane_ppm
            log_payload["gas_pressure_psi"] = payload.gas_pressure_psi
            log_payload["temperature_c"] = payload.temperature_c
            log_audit_incident(log_payload)
            
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference pipeline execution failure: {str(e)}")

@app.get("/api/v1/audit-trail")
async def fetch_audit_trail():
    return {"history": get_audit_trail(), "count": len(get_audit_trail())}

@app.get("/health")
async def health_check():
    return {"status": "ONLINE"}