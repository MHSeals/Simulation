import cv2
import time

from .pre_consolidation.gstream import Video

class BuoyDetector:
    def __init__(self, im_width=640, im_height=360):
        self.video = Video()
        self.heading = im_width // 2
        self.delta = 0

    def get_latest_frame(self, timeout=2, delay=0.1):
        for _ in range(int(timeout/delay)):
            if self.video.frame_available():
                frame = self.video.frame()
                return frame
            time.sleep(delay)
        return None
            
    def detect(self, frame):
        redx, redy = self.find_buoy(frame, color='red')
        grnx, grny = self.find_buoy(frame, color='green')
        midx, midy = (redx + grnx) // 2, (redy + grny) // 2
        self.delta = midx - self.heading
        return [(redx, redy),
                (grnx, grny),
                (midx, midy),
                (self.heading, midy)]
            
    def find_buoy(self, frame, color='red'):
        mask = None
        if color == 'red':
            mask = self.red_mask(frame)
        elif color == 'green':
            mask = self.green_mask(frame)
        else:
            raise NotImplementedError
        contours, _ = cv2.findContours(mask,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return (-1, -1)
        
        contour = sorted(contours, 
                         key=lambda c: cv2.contourArea(c), 
                         reverse=True)[0]
        x, y, w, h = cv2.boundingRect(contour)
        return (x + w // 2, y + h // 2)
    
    def red_mask(self, frame):
        # https://stackoverflow.com/a/32523532
        inverted = cv2.bitwise_not(frame)
        hsv = cv2.cvtColor(inverted, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (80, 70, 50), (100, 255, 255))
        return mask
    
    def green_mask(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (36, 25, 25), (70, 255,255))
        return mask