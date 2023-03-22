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
                await boat.set_speed(10, 3)
            else:
                await boat.set_speed(10, 3)
    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()

async def velocity_test():
    boat = AutoBoat()
    await boat.connect()

    try:
        await boat.ready()
        await boat.set_speed(10, 10)
    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready()


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
