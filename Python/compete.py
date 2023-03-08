import time
import cv2
import asyncio

from samminhch.vision import BuoyDetector
from samminhch.autopilot import AutoBoat

async def main():
    detector = BuoyDetector()
    boat = AutoBoat()

if __name__ == '__main__':
    asyncio.run(main())
    
# ---------------------------------------------------------------------------- #
#                                   CODE DUMP                                  #
# ---------------------------------------------------------------------------- #

    # while True:
    #     frame = detector.get_latest_frame()
    #     if frame is not None:
    #         result = detector.detect(frame)
    #         out = cv2.circle(frame, result[0], 4, (255, 255, 255), 1)
    #         out = cv2.circle(out, result[1], 4, (255, 100, 255), 1)
    #         out = cv2.circle(out, result[2], 4, (255, 255, 255), 1)
    #         out = cv2.circle(out, result[3], 4, (100, 255, 255), 1)
    #         cv2.imshow("Buoys", out)
        
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
        
    #     # don't want computer to die
    #     await asyncio.sleep(0.5)