import numpy as np

def analyze_cctv_frame(zone_id: str, bounding_boxes: list) -> dict:
    """
    Parses object detection metadata from a local camera stream zone.
    Evaluates worker spatial distribution against dangerous proximity markers.
    """
    # Simulate inference check using standard coordinates from video streams
    # Format: {"class": "worker" | "hazard_zone", "bbox": [x_min, y_min, x_max, y_max]}
    
    worker_count = 0
    proximity_violation = 0
    
    for obj in bounding_boxes:
        if obj.get("class") == "worker":
            worker_count += 1
            bbox = obj.get("bbox", [0, 0, 0, 0])
            
            # Check if coordinates cross into the normalized high-risk zone grid boundary
            # Default mock boundary defined between 0.6 and 1.0 for dangerous machinery proximity
            if bbox[2] > 0.6 and bbox[3] > 0.6:
                proximity_violation = 1
                
    return {
        "active_worker_count": worker_count,
        "hazard_zone_proximity_violation": proximity_violation,
        "optical_stream_status": "STABLE"
    }