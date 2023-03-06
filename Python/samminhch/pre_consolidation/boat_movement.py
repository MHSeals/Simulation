import asyncio
from mavsdk import System


async def turn_left(boat: System):
    # Set the target angle to 90 degrees to turn left
    target_angle = -90

    # Get the current heading of the boat
    async for heading in boat.telemetry.heading():
        current_heading: float = heading.heading_deg
        break

    # Calculate the new heading based on the target angle
    new_heading = current_heading + target_angle

    # Limit the new heading to be between 0 and 360 degrees
    if new_heading < 0:
        new_heading += 360
    elif new_heading >= 360:
        new_heading -= 360

    # Set the new heading using set_yaw() method
    await boat.action.return_to_launch()
