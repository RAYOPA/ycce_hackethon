import pytest
from app.ai.features import (
    calculate_personal_mean,
    calculate_personal_std,
    calculate_z_score,
    calculate_trend,
    get_temporal_features
)

def test_calculate_personal_mean():
    assert calculate_personal_mean([2.0, 4.0, 6.0]) == 4.0
    assert calculate_personal_mean([2.0, 4.0], min_obs=3) is None

def test_calculate_personal_std():
    # Variance of 2,4,6 is 4. Std is 2.
    assert calculate_personal_std([2.0, 4.0, 6.0]) == 2.0
    assert calculate_personal_std([2.0, 4.0], min_obs=3) is None
    # Zero variance
    assert calculate_personal_std([5.0, 5.0, 5.0]) == 0.0

def test_calculate_z_score():
    assert calculate_z_score(6.0, 4.0, 2.0) == 1.0
    assert calculate_z_score(2.0, 4.0, 2.0) == -1.0
    # Zero variance fallback
    assert calculate_z_score(5.0, 5.0, 0.0) == 0.0

def test_calculate_trend():
    # Linear trend [2, 4, 6, 8, 10] -> slope is 2
    assert calculate_trend([2.0, 4.0, 6.0, 8.0, 10.0]) == 2.0
    assert calculate_trend([10.0, 8.0, 6.0, 4.0, 2.0]) == -2.0

def test_get_temporal_features():
    records = [
        {"checkin_date": "2026-09-01", "sleep_hours": 6.0},
        {"checkin_date": "2026-09-02", "sleep_hours": 7.0},
        {"checkin_date": "2026-09-03", "sleep_hours": 8.0}
    ]
    features = get_temporal_features(records, "sleep_hours")
    
    assert features["sleep_hours_observation_count"] == 3
    assert features["sleep_hours_latest"] == 8.0
    assert features["sleep_hours_mean"] == 7.0
    assert features["sleep_hours_std"] == 1.0
    assert features["sleep_hours_deviation"] == 1.0  # 8 - 7
    assert features["sleep_hours_z_score"] == 1.0
    assert features["sleep_hours_rolling_3_mean"] == 7.0
    assert features["sleep_hours_rolling_7_mean"] is None
