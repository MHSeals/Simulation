import asyncio
import cv2

from samminhch.vision import BuoyDetector
from samminhch.autopilot import AutoBoat

connection_string = 'serial:///dev/ttyACM0'

async def main():
    # Create the boat and arm it!
    detector = BuoyDetector()
    boat = AutoBoat()
    await boat.connect(connection_string)

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

# make the motors spin kinda slow for 5 seconds
async def velocity_test():
    boat = AutoBoat()
    await boat.connect(connection_string)

    try:
        await boat.ready()
        await boat.set_speed(0.25, 5)
    except Exception as e:
        boat.logger.log_error(str(e))

    await boat.unready(rtl=False)


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
    # asyncio.run(main())
    asyncio.run(velocity_test())
    # asyncio.run(detector_test())
    # asyncio.run(main_jerry())
