import os

# Define facility boundaries using a mock normalized coordinate mapping system
FACILITY_ZONES = {
    "ZONE_BF1": {
        "zone_name": "Blast Furnace Core A",
        "base_coordinates": [26.1104, 85.3201],
        "evacuation_radius_meters": 75,
        "primary_hazard_risk": "Gas Accumulation & Thermal Surge"
    },
    "ZONE_CO4": {
        "zone_name": "Coke Oven Battery 4",
        "base_coordinates": [26.1120, 85.3245],
        "evacuation_radius_meters": 50,
        "primary_hazard_risk": "Volatile Hydrocarbon Leakage"
    },
    "ZONE_SMS2": {
        "zone_name": "Steel Melting Shop 2",
        "base_coordinates": [26.1085, 85.3188],
        "evacuation_radius_meters": 100,
        "primary_hazard_risk": "High-Pressure System Failure"
    }
}

def get_spatial_context(zone_id: str, critical_flag: int) -> dict:
    """
    Resolves the environmental zone information and appends dynamic protocols 
    if an active critical compound hazard flag is identified.
    """
    zone = FACILITY_ZONES.get(zone_id, {
        "zone_name": "General Factory Area",
        "base_coordinates": [26.1100, 85.3200],
        "evacuation_radius_meters": 30,
        "primary_hazard_risk": "Standard Operational Variance"
    })
    
    # Calculate actionable protocols based on model risk state
    if critical_flag == 1:
        recommended_action = "IMMEDIATE_ZONE_EVACUATION & AUTOMATIC_VALVE_SHUTDOWN"
        isolation_status = "TRIGGERED"
    else:
        recommended_action = "CONTINUOUS_MONITORING_NORMAL"
        isolation_status = "STABLE"
    
    return {
        "zone_name": zone["zone_name"],
        "coordinates": zone["base_coordinates"],
        "evacuation_radius_m": zone["evacuation_radius_meters"],
        "mitigation_protocol": recommended_action,
        "containment_valve_isolation": isolation_status
    }