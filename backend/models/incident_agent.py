import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(base_dir, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Initialize modern GenAI Client
if API_KEY and API_KEY != "your_api_key_here":
    client = genai.Client(api_key=API_KEY)
    MODEL_ACTIVE = True
else:
    client = None
    MODEL_ACTIVE = False
    print("⚠️ GenAI Agent Offline: GEMINI_API_KEY not found in .env file. Running in fallback mode.")

def generate_regulatory_report(payload_dict: dict, spatial_context: dict) -> str:
    """
    Acts as the Emergency Response Orchestrator. 
    Generates a preliminary Factory Act compliant incident report upon critical hazard confirmation.
    """
    if not MODEL_ACTIVE:
        return "AUTOMATED_REPORT_PENDING: Valid LLM API Key required for generation."

    prompt = f"""
    You are an autonomous Industrial Safety Intelligence Orchestrator.
    A compound critical hazard has just been detected by the edge ML models.
    
    [INCIDENT DATA]
    - Location: {spatial_context.get('zone_name')}
    - Coordinates: {spatial_context.get('coordinates')}
    - Active Mitigation: {spatial_context.get('mitigation_protocol')}
    - Containment Status: {spatial_context.get('containment_valve_isolation')}
    
    [SENSOR TELEMETRY]
    - Methane Level: {payload_dict.get('methane_ppm')} ppm
    - Gas Pressure: {payload_dict.get('gas_pressure_psi')} PSI
    - Active Hot Work Permit: {'YES' if payload_dict.get('hot_work_permit_active') == 1 else 'NO'}
    - Confined Space Entry: {'YES' if payload_dict.get('confined_space_entry') == 1 else 'NO'}
    
    TASK: Generate a concise, 3-paragraph preliminary regulatory incident report (Factory Act / OISD standards format).
    Include:
    1. The specific compound risk detected.
    2. The immediate autonomous actions taken by the system.
    3. Required immediate follow-up actions for the human safety officer.
    Keep it strictly professional, technical, and urgent.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"REPORT_GENERATION_FAILED: {str(e)}"