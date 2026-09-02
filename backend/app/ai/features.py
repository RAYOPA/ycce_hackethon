from typing import List, Dict, Any, Optional
import math
from datetime import datetime

# Default configuration for minimum history requirements
MIN_OBSERVATIONS_FOR_MEAN = 3
MIN_OBSERVATIONS_FOR_STD = 3
MIN_OBSERVATIONS_FOR_TREND = 5

def calculate_personal_mean(values: List[float], min_obs: int = MIN_OBSERVATIONS_FOR_MEAN) -> Optional[float]:
    if len(values) < min_obs:
        return None
    return sum(values) / len(values)

def calculate_personal_std(values: List[float], min_obs: int = MIN_OBSERVATIONS_FOR_STD) -> Optional[float]:
    if len(values) < min_obs:
        return None
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1) if len(values) > 1 else 0.0
    return math.sqrt(variance)

def calculate_z_score(value: float, mean: Optional[float], std: Optional[float]) -> Optional[float]:
    if mean is None or std is None:
        return None
    if std == 0.0:
        return 0.0  # Zero variance handling
    return (value - mean) / std

def calculate_trend(values: List[float], min_obs: int = MIN_OBSERVATIONS_FOR_TREND) -> Optional[float]:
    # Simple linear regression slope
    n = len(values)
    if n < min_obs:
        return None
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    
    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0.0
    return numerator / denominator

def get_temporal_features(records: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
    """
    Extracts deterministic temporal features for a specific field across historical records.
    Assumes records are sorted from oldest to newest.
    """
    values = [r[field] for r in records if r.get(field) is not None]
    
    features = {
        f"{field}_observation_count": len(values),
        f"{field}_missing_count": len(records) - len(values),
        f"{field}_completeness_ratio": len(values) / len(records) if records else 0.0,
    }
    
    if not values:
        features.update({
            f"{field}_latest": None,
            f"{field}_mean": None,
            f"{field}_std": None,
            f"{field}_z_score": None,
            f"{field}_trend": None
        })
        return features

    latest_val = values[-1]
    features[f"{field}_latest"] = latest_val
    
    mean = calculate_personal_mean(values)
    std = calculate_personal_std(values)
    
    features[f"{field}_mean"] = mean
    features[f"{field}_std"] = std
    
    if mean is not None:
        features[f"{field}_deviation"] = latest_val - mean
    else:
        features[f"{field}_deviation"] = None
        
    features[f"{field}_z_score"] = calculate_z_score(latest_val, mean, std)
    features[f"{field}_trend"] = calculate_trend(values)
    
    # Calculate rolling means (e.g. last 3, last 7 observations)
    for window in [3, 7, 14, 30]:
        if len(values) >= window:
            rolling_vals = values[-window:]
            features[f"{field}_rolling_{window}_mean"] = sum(rolling_vals) / window
        else:
            features[f"{field}_rolling_{window}_mean"] = None
            
    return features
