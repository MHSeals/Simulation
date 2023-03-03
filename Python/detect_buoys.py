import cv2
import numpy as np
import time
import colorsys
from gstream import Video

def draw_box(frame, mask, boxName):
    contours, _ = cv2.findContours(mask,
                                   cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return

    contour = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)[0]
    x, y, w, h = cv2.boundingRect(contour)
    imageFrame = cv2.rectangle(frame, (x, y), 
                               (x + w, y + h), 
                               (0, 0, 255), 2)
      
    imageFrame = cv2.circle(frame, 
                            (x + w // 2, y + h // 2),
                            4,
                            (100, 100, 255),
                            2)

    cv2.putText(frame, boxName, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                (0, 0, 255))


def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # filter red
    lower_red = np.array([ 0, 50, 50])
    upper_red = np.array([10,255,255])
    red_mask    = cv2.inRange(hsv, lower_red, upper_red)

    # filter green
    lower_green = np.array([36,0,0])
    upper_green = np.array([86,255,255])
    green_mask  = cv2.inRange(hsv, lower_green, upper_green)

    cv2.imshow("Red Mask", red_mask)
    cv2.imshow("Green Mask", green_mask)

    draw_box(frame, red_mask, "Red Buoy")
    draw_box(frame, green_mask, "Green Buoy")


# Create the video object
# Add port= if is necessary to use a different one
video = Video()

while True:
    # Wait for the next frame
    if not video.frame_available():
        continue

    frame = video.frame()
    process_frame(frame)
    cv2.imshow("Raw Image", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(0.25)
