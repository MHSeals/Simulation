import asyncio
import time

from samminhch.vision import BuoyDetector, LibrealsenseBuoyDetector
from samminhch.autopilot import AutoBoat
from mavsdk.telemetry import FlightMode
from mavsdk.offboard import VelocityBodyYawspeed, ActuatorControl, ActuatorControlGroup

connection_string = 'serial:///dev/ttyACM0'

async def main():
    detector = LibrealsenseBuoyDetector()
    boat = AutoBoat()
    await boat.connect(connection_string)

    mode = boat.get_flight_mode()
    armed = boat.is_armed()
    start_time = time.time()

    try:
        while True:
            if mode != FlightMode.OFFBOARD and not armed:
                await asyncio.sleep(0.5)
                continue
            else:
                # THIS PART IS FOR BEN AND I TO INTEGRATE
                # if can't find buoys in 30 seconds, break out while loop
                if not detector.has_buoy():
                    if time.time() - start_time >= 30:
                        break
                else:
                    heading = detector.get_heading()

                    if heading > 10:
                        await boat.forward(10, heading, error_bound=5)
                    else:
                        await boat.forward(10, error_bound=5)

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

            if abs(detector.delta) > 10:
                start_time = time.time()
                heading = 15 if detector.delta > 0 else -15
                await boat.forward(10, heading, error_bound=5)
            else:
                # if it hasn't seen a buoy in 30 seconds, then break out of loop
                if start_time - time.time() > 30:
                    break

                await boat.forward(10, error_bound=5)

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
        boat.logger.log_warn("Making the boat go for 10 seconds...")
        actuator_control = ActuatorControl(ActuatorControlGroup([0.5, 0.5]))

        await boat.vehicle.offboard.set_actuator_control(actuator_control)
        await asyncio.sleep(10)
        boat.logger.log_ok("Operation complete!")

    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready(rtl=True)
if __name__ == '__main__':
    # asyncio.run(main())
    # asyncio.run(test_actuator())
    asyncio.run(simulation_test())
    # asyncio.run(simulation_actuator())
    # asyncio.run(main_actuator())
