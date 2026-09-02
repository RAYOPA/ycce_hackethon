from typing import List, Dict, Any
from app.ai.features import get_temporal_features
from datetime import datetime

# Feature Engineering Version (Traceability)
FEATURE_VERSION = "v1"

def generate_personal_baseline_features(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Orchestrates the transformation of raw history into a versioned feature dictionary.
    Handles temporal feature extraction across multiple signals.
    """
    baseline_payload = {
        "metadata": {
            "feature_version": FEATURE_VERSION,
            "generated_at": datetime.utcnow().isoformat(),
            "total_historical_observations": len(history)
        },
        "features": {}
    }
    
    # Sort history chronologically
    sorted_history = sorted(history, key=lambda x: x["checkin_date"])
    
    # Signals to process
    signals = ["sleep_hours", "sleep_quality", "mood_score", "energy_score", "workload_score", "stress_score"]
    
    for signal in signals:
        signal_features = get_temporal_features(sorted_history, signal)
        baseline_payload["features"].update(signal_features)
        
    # Additional dataset quality rules
    # E.g., is there sufficient history for a reliable baseline model?
    # Determine overall sufficient history based on some minimal threshold
    total_obs = len(sorted_history)
    baseline_payload["metadata"]["sufficient_history"] = total_obs >= 7
    
    if total_obs > 0:
        latest_date = sorted_history[-1]["checkin_date"]
        # Convert isoformat to datetime to get age
        # Depending on how it's serialized, this might be a string.
        if isinstance(latest_date, str):
            try:
                # Basic parse for iso format
                ld = datetime.fromisoformat(latest_date.replace("Z", "+00:00"))
                baseline_payload["metadata"]["latest_observation_age_days"] = (datetime.utcnow().astimezone() - ld).days
            except Exception:
                baseline_payload["metadata"]["latest_observation_age_days"] = None
    else:
        baseline_payload["metadata"]["latest_observation_age_days"] = None

    return baseline_payload
