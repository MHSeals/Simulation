import asyncio
from asyncio import Task
from typing import List
from mavsdk import System
from mavsdk.telemetry import Telemetry
from mavsdk.mission import MissionPlan
import mission_helper


async def print_mission_progress(boat: System):
    """Prints the mission progress of the boat

    Args:
        boat (System): The boat
    """
    async for mission_progress in boat.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")
        await asyncio.sleep(5)


async def print_position_and_heading(telemetry: Telemetry):
    """Prints the current location and heading of the boat

    Args:
        telemetry (Telemetry): The telemetry subscription from the boat
    """
    async for position in telemetry.position():
        print(f"Latitude: {position.latitude_deg}")
        print(f"Longitude: {position.longitude_deg}")
        position = (position.latitude_deg, position.longitude_deg)
        await asyncio.sleep(5)

    async for heading in telemetry.heading():
        print(f"Heading: {heading.heading_deg}")
        heading = heading.heading_deg
        await asyncio.sleep(5)


async def boat_reached_rtl(boat: System, tasks: List[Task]):
    """Cancels all tasks in the task list when boat reaches it starting location

    Args:
        boat (System): The boat
        tasks (List[Task]): The list of tasks to end
    """
    async for mission_progress in boat.mission.mission_progress():
        if mission_progress.current <= mission_progress.total:
            continue

        print('---- Mission Complete ----')
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        await asyncio.get_event_loop().shutdown_asyncgens()
        return


async def main():
    print('---- Establishing Connection ----')
    boat = System()

    # Wait for mavsdk to connect to boat
    await boat.connect('udp://:14540')
    async for state in boat.core.connection_state():
        if state.is_connected:
            print('---- Connection Established ----')
            break

    telemetry = boat.telemetry
    # Get current position and heading
    starting_position = (-1, -1)
    heading = -1

    async for starting_position in telemetry.position():
        starting_position = (starting_position.latitude_deg, starting_position.longitude_deg)
        break

    async for heading in telemetry.heading():
        heading = heading.heading_deg
        break

    # Create tasks to constantly print out position and heading
    print_location_task = asyncio.ensure_future(
        print_position_and_heading(telemetry))
    print_mission_task = asyncio.ensure_future(print_mission_progress(boat))

    running_tasks = [print_location_task, print_mission_task]
    termination_task = asyncio.ensure_future(
        boat_reached_rtl(boat, running_tasks))

    # Create a waypoint 200 feet in front of boat
    mission_items = []

    new_coords = mission_helper.get_new_coordinate(starting_position, 200, heading)
    mission_items.append(mission_helper.make_waypoint(
        new_coords[0], new_coords[1]))

    await boat.mission.set_return_to_launch_after_mission(True)
    await boat.action.set_maximum_speed(10)

    print('---- Uploading Mission ----')
    await boat.mission.upload_mission(MissionPlan(mission_items))

    # Arming and running the mission
    async for health in boat.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("---- Global Position State Good ----")
            break

    print('---- Arming Boat ----')
    await boat.action.arm()

    print('---- Starting Mission ----')
    await boat.mission.start_mission()
    await termination_task

    print('---- Disarming Boat ----')
    await boat.action.disarm()
    # await boat.action.kill()


if __name__ == "__main__":
    asyncio.run(main())
