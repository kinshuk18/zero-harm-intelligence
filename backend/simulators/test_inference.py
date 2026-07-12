import requests
import json

def run_validation_tests():
    url = "http://127.0.0.1:8000/api/v1/assess-risk"
    headers = {"Content-Type": "application/json"}
    
    # Scenario A: Standard operational values
    normal_payload = {
        "zone_id": "ZONE_CO4",
        "gas_pressure_psi": 48.5,
        "methane_ppm": 8.2,
        "temperature_c": 42.1,
        "hot_work_permit_active": 0,
        "confined_space_entry": 0,
        "cctv_metadata": [{"class": "worker", "bbox": [0.1, 0.1, 0.3, 0.4]}]
    }
    
    # Scenario B: High methane levels occurring concurrently with active welding/hot work
    compound_risk_payload = {
        "zone_id": "ZONE_BF1",
        "gas_pressure_psi": 55.0,
        "methane_ppm": 112.4,
        "temperature_c": 46.8,
        "hot_work_permit_active": 1,
        "confined_space_entry": 0,
        "cctv_metadata": [{"class": "worker", "bbox": [0.2, 0.2, 0.8, 0.9]}] # Proximity breach
    }
    
    print("📡 Sending Safe Operational Payload...")
    response_safe = requests.post(url, data=json.dumps(normal_payload), headers=headers)
    print(f"Status: {response_safe.status_code} | Response: {response_safe.json()}")
    
    print("\n🚨 Sending Compound Hazard Payload (Methane Spike + Active Hot Work)...")
    response_hazard = requests.post(url, data=json.dumps(compound_risk_payload), headers=headers)
    print(f"Status: {response_hazard.status_code} | Response: {response_hazard.json()}")

    print("\n📜 Validating Persistent History Audit Trail Pipeline...")
    history_url = "http://127.0.0.1:8000/api/v1/audit-trail"
    response_history = requests.get(history_url)
    print(f"Status: {response_history.status_code} | Total Logged Breaches Found: {response_history.json().get('count')}")
    if response_history.json().get('count', 0) > 0:
        print(f"Latest Recorded Entry ID: {response_history.json()['history'][0]['entry_id']}")

if __name__ == "__main__":
    try:
        run_validation_tests()
    except requests.exceptions.ConnectionError:
        print("❌ Error: The FastAPI server is offline. Run 'uvicorn backend.api.main:app --reload' first.")