"""Optional live check for OSMnx road snapping."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from road_geometry import load_hoboken_graph, route_between_anchors


def main():
    graph, error = load_hoboken_graph()
    if error:
        print(f"SKIP: road geometry test could not run: {error}")
        return

    route, error = route_between_anchors(graph, 40.7427, -74.0242, 40.7507, -74.0233)
    if error:
        raise RuntimeError(error)
    assert len(route["coordinates"]) > 2
    assert route["route_length_m"] > 0
    failed_route, failed_error = route_between_anchors(graph, None, None, None, None)
    assert failed_route is None and failed_error
    print("Road geometry checks passed: graph loaded, anchors snapped, route has multiple points, fallback reports an error.")


if __name__ == "__main__":
    main()
