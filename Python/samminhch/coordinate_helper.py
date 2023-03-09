from typing import Tuple
import math

def get_new_coordinate(start_coord: Tuple[float, float], distance_feet: float, heading_degrees: float) -> Tuple[float, float]:
    """This returns a new coordinate that's `distance_feet` away from the `starting_coord` at `heading_degrees`

    Args:
        start_coord (Tuple[float, float]): A tuple containing the starting latitude and longitude respectively
        distance_feet (float): The distance to make the new coordinate
        heading_degrees (float): The heading at which to make the new coordinate at

    Returns:
        Tuple[float, float]: The new coordinate
    """
    # Convert starting coordinates to radians
    starting_lat, starting_long = map(math.radians, start_coord)

    # Convert distance from feet to meters
    distance_meters = distance_feet * 0.3048

    # Convert heading from degrees to radians
    heading = math.radians(heading_degrees)

    # Earth's radius in meters
    earth_radius = 6378137

    # Calculate new coordinates
    result_lat = math.asin(math.sin(starting_lat) * math.cos(distance_meters / earth_radius) +
                     math.cos(starting_lat) * math.sin(distance_meters / earth_radius) * math.cos(heading))
    result_long = starting_long + math.atan2(math.sin(heading) * math.sin(distance_meters / earth_radius) * math.cos(starting_lat),
                             math.cos(distance_meters / earth_radius) - math.sin(starting_lat) * math.sin(result_lat))

    # Convert new coordinates back to degrees
    new_coord = math.degrees(result_lat), math.degrees(result_long)

    return new_coord


def coord_dist(coords_a: Tuple[float, float], coords_b: Tuple[float, float]):
    """Gets the distance between two geometric coordinates in feet

    Args:
        coords_a (Tuple[float, float]): The starting geometric coordinate
        coords_b (Tuple[float, float]): The ending geometric coordinate

    Returns:
        float: The distance between two coordinates in feet
    """
    # distance in feet
    earth_radius_m = 6371000
    meters_to_feet = 3.281

    d_lat = math.radians(coords_b[0] - coords_a[0])
    d_lon = math.radians(coords_b[1] - coords_a[1])
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(coords_b[0])) * \
        math.cos(math.radians(coords_a[0])) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_m = earth_radius_m * c

    return distance_m * meters_to_feet
