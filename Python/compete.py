import asyncio
import cv2

from samminhch.vision import BuoyDetector
from samminhch.autopilot import AutoBoat


async def main():
    # Create the boat and arm it!
    detector = BuoyDetector()
    boat = AutoBoat()
    await boat.connect()

    # ready the boat

    try:
        await boat.ready()
        # find the buoys to go to
        while True:
            frame = detector.get_latest_frame()
            detector.detect(frame)
            detector.logger.log_debug(f'Delta is {detector.delta}')

            if abs(detector.delta) > 10:
                amount_to_turn = 15 if detector.delta > 0 else -15
                await boat.forward(distance=10,
                                   heading=amount_to_turn, error_bound=1)
            else:
                await boat.forward(10, heading=0, error_bound=1)
            await asyncio.sleep(0.1)
        # await boat.forward(100, heading=-45, error_bound=5)
    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()

    # get goal coordinates
    # detection_info = None

    # go to those goal coordinates
    # boat.turn(detection_info.heading)

    # while boat isn't at goal:
    #   find_obstacle_buoys
    #   find a way around them
    #   head to the goal
    #
    #   ⬆ check for failsafes while doing all that

    # await boat.unready()


async def main_jerry():
    # boat = AutoBoat_Jerry()
    # await boat.connect()
    # await boat.arm()
    # await boat.enable_offboard()
    # await boat.set_position_ned_yaw(float(-2),
    #                                 float(0),
    #                                 float(0),
    #                                 float(-180))
    # await boat.disable_offboard()
    # await boat.disarm()
    pass


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
    # asyncio.run(detector_test())
    # asyncio.run(main_jerry())
