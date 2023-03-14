import cv2
import time

from .pre_consolidation.gstream import Video
from .simutils import ColorLogger


class BuoyDetector:
    def __init__(self, im_width=640):
        self.video = Video()
        self.heading = im_width // 2
        self.delta = 0
        self.logger = ColorLogger()

    def get_latest_frame(self, timeout=2, delay=0.1):
        for i in range(int(timeout/delay)):
            if self.video.frame_available():
                self.logger.log_ok("Frame found!", beg='\n')
                frame = self.video.frame()
                return frame
            self.logger.log_warn(
                f"Grabbing frame from camera{'.' * ((i % 3) + 1)}   ",
                beg='\r', end='')
            time.sleep(delay)
        return None

    def detect(self, frame):
        redX, redY = self.find_buoy(frame, color='red')
        grnX, grnY = self.find_buoy(frame, color='green')

        if redX is None or redY is None or grnX is None or grnY is None:
            self.delta = 0
            return

        midX, midY = (redX + grnX) // 2, (redY + grnY) // 2

        self.delta = midX - self.heading
        return [(redX, redY),
                (grnX, grnY),
                (midX, midY),
                (self.heading, midY)]

    def find_buoy(self, frame, color='red'):
        mask = None
        if color == 'red':
            mask = self.__red_mask(frame)
        elif color == 'green':
            mask = self.__green_mask(frame)
        else:
            raise NotImplementedError
        contours, _ = cv2.findContours(mask,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        contours = [c for c in contours if cv2.contourArea(c) > 25]

        if len(contours) == 0:
            self.logger.log_error(f'No {color} buoy found!')
            return (None, None)

        contour = sorted(contours,
                         key=lambda c: cv2.contourArea(c),
                         reverse=True)[0]
        self.logger.log_debug(f'{color} area is {cv2.contourArea(contour)}')
        x, y, w, h = cv2.boundingRect(contour)
        return (x + w // 2, y + h // 2)

    def __red_mask(self, frame):
        # https://stackoverflow.com/a/32523532
        inverted = cv2.bitwise_not(frame)
        hsv = cv2.cvtColor(inverted, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (80, 70, 50), (100, 255, 255))
        return mask

    def __green_mask(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (36, 25, 25), (70, 255, 255))
        return mask
