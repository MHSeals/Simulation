import asyncio
import math
from typing import Tuple
from mavsdk import System
from mavsdk.telemetry import (Telemetry, LandedState)
import mission_helper


async def print_position_and_heading(telemetry: Telemetry):
    """Prints the current location and heading of the boat

    Args:
        telemetry (Telemetry): The telemetry subscription from the boat
    """
    async for position in telemetry.position():
        print(f"Latitude: {position.latitude_deg:.3f}")
        print(f"Longitude: {position.longitude_deg:.3f}")
        position = (position.latitude_deg, position.longitude_deg)
        await asyncio.sleep(2)

    async for heading in telemetry.heading():
        print(f"Heading: {heading.heading_deg}")
        heading = heading.heading_deg
        await asyncio.sleep(2)


def get_dist(coords_a: Tuple[float, float], coords_b: Tuple[float, float]):
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


async def return_home(boat: System, home_coords: Tuple[float, float], error_bound: float = 1):
    await boat.action.return_to_launch()
    
    reached_dest = False
    while not reached_dest:
        current_pos, _ = await get_location(boat.telemetry)

        # distance in feet
        distance = get_dist(current_pos, home_coords)
        print(f'{distance=}')

        reached_dest = distance < error_bound
        if not reached_dest:
            await asyncio.sleep(1)  # wait for 1 second before checking again


async def go_to(boat: System, coords: Tuple[float, float], heading: float, error_bound: float = 1):
    await boat.action.goto_location(coords[0], coords[1], 0, heading)

    reached_dest = False
    while not reached_dest:
        current_pos, _ = await get_location(boat.telemetry)

        # distance in feet
        distance = get_dist(current_pos, coords)
        print(f'distance: {distance:.2f} feet from ({coords[0]:.3f}, {coords[1]:.3f})')

        reached_dest = distance < error_bound
        if not reached_dest:
            await asyncio.sleep(1)  # wait for 1 second before checking again
    
    print("---- Boat Reached Location ----")


async def get_location(telemetry: Telemetry) -> Tuple[Tuple[float, float], float]:
    """Get the current location and heading of the boat

    Args:
        telemetry (Telemetry): The boat telmetry

    Returns:
        Tuple[Tuple[float, float], float]: ((latitude, longitude), heading)
    """
    async for position in telemetry.position():
        pos = (position.latitude_deg, position.longitude_deg)
        break
    async for heading in telemetry.heading():
        head = heading.heading_deg
        break

    return (pos, head)


async def arm_boat(boat: System):
    """Arms the boat once the boat is able to be armed

    Args:
        boat (System): The boat to arm
    """
    async for health in boat.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("---- Global Position State Good ----")
            break

    print('---- Arming Boat ----')
    await boat.action.arm()


async def disarm_boat(boat: System):
    """Disarms the boat when it is ready to disarm

    Args:
        boat (System): The boat
    """
    async for landed_state in boat.telemetry.landed_state():
        if landed_state == LandedState.LANDING: break
        await asyncio.sleep(1) # check every second
    
    async for position in boat.telemetry.position():
        await boat.action.set_return_to_launch_altitude(position.relative_altitude_m)
        break
    
    async for landed_state in boat.telemetry.landed_state():
        if landed_state == LandedState.ON_GROUND:
            break
        await asyncio.sleep(1)  # check every second
        
    print('---- Disarming Boat ----')
    await boat.action.disarm()


async def connect_to_boat(connection_string='udp://:14540') -> System:
    """Establishes a connection to the boat and returns the boat

    Args:
        connection_string (str, optional): See http://mavsdk-python-docs.s3-website.eu-central-1.amazonaws.com/system.html#mavsdk.system.System.connect. Defaults to 'udp://:14540'.

    Returns:
        System: The boat object
    """
    boat = System()

    # Wait for mavsdk to connect to boat
    await boat.connect(connection_string)
    async for state in boat.core.connection_state():
        if state.is_connected:
            print('---- Connection Established ----')
            break

    return boat


async def main():
    print('---- Establishing Connection ----')
    boat = await connect_to_boat()

    telemetry = boat.telemetry

    # Get current position and heading
    starting_position, heading = await get_location(telemetry)

    # Create tasks to constantly print out position and heading
    print_location_task = asyncio.ensure_future(
        print_position_and_heading(telemetry))

    await arm_boat(boat)

    new_coords = mission_helper.get_new_coordinate(
        starting_position, 200, heading)
    
    await go_to(boat, new_coords, heading, error_bound=5)
    await boat.action.return_to_launch()

    print_location_task.cancel()
    await disarm_boat(boat)


if __name__ == "__main__":
    asyncio.run(main())
