import json
import os
from datetime import datetime

# Resolve storage directories cleanly relative to this source file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIT_LOG_PATH = os.path.join(BASE_DIR, "data", "processed", "audit_log.json")

def log_audit_incident(incident_data: dict) -> bool:
    """
    Appends an authenticated critical risk event straight into the persistent history log.
    """
    try:
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        
        # Load existing entries or initialize clean array
        if os.path.exists(AUDIT_LOG_PATH):
            with open(AUDIT_LOG_PATH, "r") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        else:
            history = []
            
        # Structure timeline log record
        log_entry = {
            "entry_id": f"AUDIT-{int(datetime.now().timestamp())}",
            "logged_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "zone_id": incident_data.get("zone_id"),
            "risk_probability": incident_data.get("risk_probability"),
            "telemetry_snapshot": {
                "methane_ppm": incident_data.get("methane_ppm"),
                "gas_pressure_psi": incident_data.get("gas_pressure_psi"),
                "temperature_c": incident_data.get("temperature_c")
            },
            "mitigation_protocol": incident_data.get("geospatial_context", {}).get("mitigation_protocol"),
            "regulatory_report_summary": incident_data.get("autonomous_incident_report")
        }
        
        history.insert(0, log_entry) # Keep newest events at the top
        
        with open(AUDIT_LOG_PATH, "w") as f:
            json.dump(history, f, indent=4)
        return True
    except Exception as e:
        print(f"❌ Failed to commit entry to audit ledger: {str(e)}")
        return False

def get_audit_trail() -> list:
    """
    Retrieves the complete array of historical breaches for analytics mapping.
    """
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    try:
        with open(AUDIT_LOG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []