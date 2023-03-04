#!/usr/bin/env python3
import math
from typing import Tuple
from mavsdk.mission import (MissionItem)


def make_waypoint(latitude: float, longitude: float, acceptance_radius=0) -> MissionItem:
    return MissionItem(latitude,
                       longitude,
                       0,
                       10,
                       True,
                       float('nan'),
                       float('nan'),
                       MissionItem.CameraAction.NONE,
                       float('nan'),
                       float('nan'),
                       acceptance_radius,
                       float('nan'),
                       float('nan'))


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
