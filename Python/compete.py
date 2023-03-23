import asyncio
import time

from samminhch.vision import BuoyDetector
from samminhch.autopilot import AutoBoat
from mavsdk.telemetry import FlightMode

connection_string = 'serial:///dev/ttyACM0'

async def main():
    # Connect to the boat on startup
    # Check the status of the boat
    # # start the autonomous code if the status is set to OFFBOARD

    # Create the boat and arm it!
    boat = AutoBoat()
    await boat.connect(connection_string)

    mode = boat.get_flight_mode()
    armed = boat.is_armed()

    timeout = 10
    start_time = time.time()

    try:
        while mode == FlightMode.OFFBOARD and armed:
            if time.time() - start_time >= timeout:
                break
            await boat.vehicle.action.set_actuator(0, 0.125)

    except Exception as e:
        print(str(e))

    await boat.unready(rtl=False)

    # try:
    #     await boat.ready()
    #     # find the buoys to go to
    #     while True:
    #         frame = detector.get_latest_frame()
    #         detector.detect(frame)
    #         detector.logger.log_debug(f'Delta is {detector.delta}')
    #
    #         if abs(detector.delta) > 10:
    #             amount_to_turn = 15 if detector.delta > 0 else -15
    #             await boat.forward(20, amount_to_turn, error_bound=5)
    #         else:
    #             # forward
    #             await boat.forward(20, 0, error_bound=5)
    # except Exception as e:
    #     boat.logger.log_error(str(e))
    #
    # await boat.unready()

# make the motors spin kinda slow for 5 seconds
async def velocity_test():
    boat = AutoBoat()
    await boat.connect(connection_string)


async def detector_test():
    detector = BuoyDetector()
    while True:
        frame = detector.get_latest_frame()
        cv2.imshow('raw image', frame)
        detector.detect(frame)
        cv2.waitKey(1)
        detector.logger.log_debug(f"Delta is {detector.delta}")
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())
    # asyncio.run(velocity_test())
    # asyncio.run(detector_test())
    # asyncio.run(main_jerry())
