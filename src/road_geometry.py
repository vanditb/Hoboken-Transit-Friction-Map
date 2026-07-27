"""Road-snapped display geometry for manually anchored construction corridors."""

from pathlib import Path
import math


HOBOKEN_PLACE = "Hoboken, New Jersey, USA"
GRAPH_CACHE_PATH = Path(__file__).resolve().parents[1] / "data" / "hoboken_street_graph.graphml"


def _import_osmnx():
    try:
        import networkx as nx
        import osmnx as ox
    except ImportError as error:
        return None, None, f"OSMnx is not installed: {error}"
    return ox, nx, None


def load_hoboken_graph(use_disk_cache=True):
    """Load a small public-street graph, downloading it only when no cache exists."""
    ox, _, error = _import_osmnx()
    if error:
        return None, error

    try:
        if use_disk_cache and GRAPH_CACHE_PATH.exists():
            return ox.load_graphml(GRAPH_CACHE_PATH), None

        graph = ox.graph_from_place(HOBOKEN_PLACE, network_type="drive")
        if use_disk_cache:
            GRAPH_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            ox.save_graphml(graph, GRAPH_CACHE_PATH)
        return graph, None
    except Exception as error:  # Network and OSM data errors should not stop the app.
        return None, f"Could not load the Hoboken street graph: {error}"


def nearest_graph_node(graph, lat, lon):
    """Find the closest graph node without OSMnx's optional scikit-learn dependency."""
    latitude = float(lat)
    longitude = float(lon)
    closest_node = None
    closest_distance = float("inf")
    for node, data in graph.nodes(data=True):
        # Hoboken is small, so an equirectangular local-distance approximation is enough for snapping.
        latitude_delta = float(data["y"]) - latitude
        longitude_delta = (float(data["x"]) - longitude) * math.cos(math.radians(latitude))
        distance = latitude_delta * latitude_delta + longitude_delta * longitude_delta
        if distance < closest_distance:
            closest_node = node
            closest_distance = distance
    if closest_node is None:
        raise ValueError("Street graph did not contain any nodes.")
    return closest_node


def route_between_anchors(graph, start_lat, start_lon, end_lat, end_lon):
    """Snap approximate anchors to graph nodes and return a road-following Folium route."""
    ox, nx, error = _import_osmnx()
    if error:
        return None, error
    if graph is None:
        return None, "Street graph is unavailable."

    try:
        start_node = nearest_graph_node(graph, start_lat, start_lon)
        end_node = nearest_graph_node(graph, end_lat, end_lon)
        route = nx.shortest_path(graph, start_node, end_node, weight="length")
        coordinates = [[graph.nodes[node]["y"], graph.nodes[node]["x"]] for node in route]
        route_length_m = sum(
            min(edge.get("length", 0) for edge in graph.get_edge_data(first, second).values())
            for first, second in zip(route, route[1:])
        )
        snapped_start = coordinates[0]
        snapped_end = coordinates[-1]
        return {
            "coordinates": coordinates,
            "route_length_m": round(route_length_m, 1),
            "snapped_start_lat": snapped_start[0],
            "snapped_start_lon": snapped_start[1],
            "snapped_end_lat": snapped_end[0],
            "snapped_end_lon": snapped_end[1],
            "geometry_method": "road_snapped_osmnx",
        }, None
    except Exception as error:
        return None, f"Could not snap and route this corridor: {error}"
