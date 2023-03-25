import asyncio
import time
import samminhch.coordinate_helper as coords

from samminhch.vision import BuoyDetector, LibrealsenseBuoyDetector
from samminhch.autopilot import AutoBoat
from mavsdk.telemetry import FlightMode

connection_string = 'serial:///dev/ttyACM0'


async def love_puerto_rico():
    """Thank you for these coordinates :D"""
    boat = AutoBoat()
    await boat.connect()


    current_coords = await boat.get_position()
    current_heading = await boat.get_heading()

    waypoints = [
            (27.3729721, -82.456359),    # 2
            (27.3729148, -82.4528368),   # 3
            (27.3729036, -82.4528549),   # 4
    ]
    idx = 0

    try:
        await boat.ready()
        mode = await boat.get_flight_mode()
        armed = await boat.is_armed()
        while True:
            if (not armed) or (mode != FlightMode.OFFBOARD):
                boat.logger.log_warn("Unarmed or not in offboard... waiting...!")
            else:
                if idx == len(waypoints):
                    break
                latitude, longitude = waypoints[idx]
                await boat.goto(latitude, longitude)
                idx += 1

            mode = await boat.get_flight_mode()
            armed = await boat.is_armed()
            await asyncio.sleep(1)
    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()
    pass

async def main():
    detector = LibrealsenseBuoyDetector()
    boat = AutoBoat()
    await boat.connect(connection_string)

    mode = boat.get_flight_mode()
    armed = boat.is_armed()

    try:
        while True:
            if mode != FlightMode.OFFBOARD and not armed:
                await asyncio.sleep(0.5)
                continue
            else:
                # THIS PART IS FOR BEN AND I TO INTEGRATE
                # if can't find buoys in 30 seconds, break out while loop
                heading = detector.get_heading()
                await asyncio.wait_for(boat.forward(20, heading=heading, error_bound=5), timeout=30)


            # update ending conditions
            mode = boat.get_flight_mode()
            armed = boat.is_armed()

            await asyncio.sleep(0.5)

    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()


async def simulation_test():
    detector = BuoyDetector()

    boat = AutoBoat()
    await boat.connect()

    start_time = time.time()
    try:
        await boat.ready()

        while True:
            frame = detector.get_latest_frame()
            detector.detect(frame)

            boat.logger.log_debug(f"Delta: {detector.delta}")
            if abs(detector.delta) > 10:
                heading = 15 if detector.delta > 0 else -15
                start_time = time.time()
                try:
                    await asyncio.wait_for(boat.forward(30, heading, error_bound=5), timeout=30)
                except Exception:
                    boat.logger.log_error("Timeout exceeded to move... Continuing program")
            else:
                # if it hasn't seen a buoy in 30 seconds, then break out of loop
                boat.logger.log_debug(f"Timeout so far: {time.time() - start_time}")
                if time.time() - start_time > 60:
                    boat.logger.log_warn("it's been 20 seconds since last buoy... returning home!")
                    break

                try:
                    await asyncio.wait_for(boat.forward(30, error_bound=5), timeout=30)
                except Exception:
                    boat.logger.log_error("Timeout exceeded to move... Continuing program")

    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()


async def simulation_actuator():
    detector = BuoyDetector()

    boat = AutoBoat()
    await boat.connect()
    start_time = time.time()

    try:
        await boat.ready()
        while True:
            frame = detector.get_latest_frame()
            detector.detect(frame)

            if abs(detector.delta) > 10:
                start_time = 0
                await boat.vehicle.action.set_actuator(1 if detector.delta > 0 else 2,
                                                       0.5)
            else:
                # maintain thrusters
                # if it hasn't seen a buoy in 30 seconds, then break out of loop
                if start_time - time.time() > 30:
                    break

                await boat.vehicle.action.set_actuator(1, 0.25)
                await boat.vehicle.action.set_actuator(2, 0.25)
                pass

    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()


async def test_actuator():
    boat = AutoBoat()
    await boat.connect()

    try:
        await boat.ready()
        await boat.vehicle.action.set_actuator(1, 1)
        await asyncio.sleep(10)

    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()
if __name__ == '__main__':
    asyncio.run(love_puerto_rico())
    # asyncio.run(main())
    # asyncio.run(test_actuator())
    # asyncio.run(simulation_test())
    # asyncio.run(simulation_actuator())
    # asyncio.run(main_actuator())
