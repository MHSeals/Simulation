import asyncio
import time
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)

waypoints = [
        # (47.333796, 8.547610),
        # (47.333698, 8.547897),
        (47.333831, 8.548232)
        ]

def make_waypoint(latitude, longitude, acceptance_radius=0):
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


async def print_position(boat: System):
    async for position in boat.telemetry.position():
        print(f'Boat is at: ({position.latitude_deg}, {position.longitude_deg})')
        time.sleep(1)


async def boat_reached_rtl(boat: System, tasks):
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

    print_position_task = asyncio.ensure_future(print_position(boat))
    running_tasks = [print_position_task]
    # running_tasks = None
    termination_task = asyncio.ensure_future(boat_reached_rtl(boat, running_tasks))

    # Creating and uploading mission
    mission_items = []
    for waypoint in waypoints:
        mission_items.append(make_waypoint(*(waypoint)))

    mission_plan = MissionPlan(mission_items)

    await boat.mission.set_return_to_launch_after_mission(True)
    await boat.action.set_maximum_speed(10)

    print('---- Uploading Mission ----')
    await boat.mission.upload_mission(mission_plan)

    # Arming and running the mission
    async for health in boat.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("---- Global Position State Good ----")
            break

    print('---- Arming Boat ----')
    await boat.action.arm()

    print('---- Starting Mission ----')
    await boat.mission.start_mission()
    # print('---- Disarming Boat ----')
    # await drone.action.disarm()
    await termination_task
    print('---- Mission Complete ----')
    await boat.action.kill()


if __name__ == "__main__":
    asyncio.run(main())
