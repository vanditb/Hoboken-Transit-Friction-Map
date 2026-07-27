"""Small checks for the prototype score helpers."""

from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scoring import EXPERIMENTAL_WEIGHTS, calculate_construction_friction, combine_scores, project_affects_mode


def main():
    station = pd.Series({"lat": 40.7433, "lon": -74.0324})
    construction = pd.DataFrame(
        [
            {
                "project_name": "Nearby verified closure", "geometry_type": "point", "lat": 40.7433, "lon": -74.0324,
                "verification_status": "verified", "active_status": "active", "friction_level": "severe", "mode_affected": "biking",
            },
            {
                "project_name": "Expired row", "geometry_type": "point", "lat": 40.7433, "lon": -74.0324,
                "verification_status": "verified", "active_status": "expired", "friction_level": "severe", "mode_affected": "biking",
            },
            {
                "project_name": "Unverified row", "geometry_type": "point", "lat": 40.7433, "lon": -74.0324,
                "verification_status": "unverified", "active_status": "active", "friction_level": "severe", "mode_affected": "biking",
            },
        ]
    )
    result = calculate_construction_friction(station, construction, "Biking")
    assert result["score"] == 100.0
    assert result["nearest_project"] == "Nearby verified closure"
    assert project_affects_mode(construction.iloc[0], "Biking")
    assert not project_affects_mode(construction.iloc[0], "Driving")

    far_station = pd.Series({"lat": 40.7478, "lon": -74.0324})
    far_result = calculate_construction_friction(far_station, construction.iloc[:1], "Biking")
    assert far_result["score"] == 0.0

    score = combine_scores({"bike": 80, "weather": None, "construction": 20}, EXPERIMENTAL_WEIGHTS)
    assert score == 65.0, "Missing weather should renormalize bike/construction weights."
    assert 0 <= score <= 100
    print("Scoring checks passed: bounds, mode filtering, distance decay, status filtering, and renormalization.")


if __name__ == "__main__":
    main()
