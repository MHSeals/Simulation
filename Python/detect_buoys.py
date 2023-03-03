import cv2
import numpy as np
import time
from gstream import Video

capture = Video()
try:
    while True:
        if not capture.frame_available():
            continue

        # Take each frame
        frame = capture.frame()

        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # filter red
        lower_red   = np.array([ 0,  20,  20])
        upper_red   = np.array([ 0, 255, 255])
        red_mask = cv2.inRange(hsv, lower_red, upper_red)

        # filter green
        lower_green = np.array([50,  20,  20])
        upper_green = np.array([50, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        kernel = np.ones((5, 5), "uint8")

        red_mask = cv2.dilate(red_mask, kernel)
        res_red  = cv2.bitwise_and(frame, frame, mask = red_mask)

        green_mask = cv2.dilate(green_mask, kernel)
        res_green  = cv2.bitwise_and(frame, frame, mask = green_mask)

        contours, hierarchy = cv2.findContours(red_mask,
                                                cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 300:
                x, y, w, h = cv2.boundingRect(contour)
                imageFrame = cv2.rectangle(frame, (x, y), 
                                           (x + w, y + h), 
                                           (0, 0, 255), 2)
                  
                cv2.putText(frame, "Red Buoy", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            (0, 0, 255))
        
        contours, hierarchy = cv2.findContours(green_mask,
                                                cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_SIMPLE)

        for pic, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 300:
                x, y, w, h = cv2.boundingRect(contour)
                imageFrame = cv2.rectangle(frame, (x, y), 
                                           (x + w, y + h), 
                                           (0, 0, 255), 2)
                  
                cv2.putText(frame, "Green Buoy", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            (0, 0, 255))

        cv2.imshow("Buoy Detection", frame)
        time.sleep(.5)
except KeyboardInterrupt as err:
    cv2.destroyAllWindows()

