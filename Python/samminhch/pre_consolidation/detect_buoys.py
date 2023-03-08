from typing import Tuple
import cv2
from cv2 import Mat
import numpy as np
import time
from gstream import Video

def process_frame(frame: np.ndarray):
    """This takes a frame from an openCV capture, and draws circles at the center 
    of the detected buoys, and the midpoint between those two buoy centers

    Args:
        frame (np.ndarray): The frame to process
    """
    hsv: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Hue Saturation Vibrance
    # Demon Magic
    # https://stackoverflow.com/questions/32522989/opencv-better-detection-of-red-color
    red1_lower = (0, 50, 50)
    red1_upper = (10, 255, 255)
    red2_lower = (170, 70, 50)
    red2_upper = (180, 255, 255)
    green_lower = (36,  50,  50)
    green_upper = (86, 255, 255)
    
    
    red1_mask = cv2.inRange(hsv, red1_lower, red1_upper)
    red2_mask = cv2.inRange(hsv, red2_lower, red2_upper)
    red_mask = red1_mask | red2_mask
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    
    cv2.imshow('Red Mask', red_mask)
    cv2.imshow('Green Mask', green_mask)

    red_x, red_y = find_buoy(hsv, red_mask)
    green_x, green_y = find_buoy(hsv, green_mask)
    mid_x, mid_y = (red_x + green_x) // 2, (red_y + green_y) // 2

    # draw circles around the centers of the buoys
    imageFrame = cv2.circle(frame, (red_x, red_y), 4, (255, 255, 255), 1)
    imageFrame = cv2.circle(frame, (green_x, green_y), 4, (255, 100, 255), 1)

    # draw circle at the midpoint of the two buoys
    imageFrame = cv2.circle(frame, (mid_x, mid_y), 4, (255, 255, 255), 1)


def main():
    """This draws gets frames from the UDP video capture, and sends it to process_frame()
    """
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
        
        # don't want computer to die
        time.sleep(0.5)


def find_buoy(frame: np.ndarray, mask: Mat) -> Tuple[int, int]:
    """Finds a buoy with the given lower and upper bounds for a color mask

    Args:
        frame (np.ndarray): The frame to find the buoys in
        lower_bound (Tuple[int, int, int]): The lower bound color, in HSV values
        upper_bound (Tuple[int, int, int]): The upper bound color, in HSV values

    Returns:
        Tuple[int, int]: The (x,y) pixel coordinate of the center of the detected buoy
    """
    
    # Get the biggest contour (the closest buoy in the frame)
    contours, _ = cv2.findContours(mask,
                                   cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return (-1, -1)

    contour = sorted(
        contours, key=lambda c: cv2.contourArea(c), reverse=True)[0]
    x, y, w, h = cv2.boundingRect(contour)

    return (x + w // 2, y + h // 2)


def get_gate_delta(debug = False) -> int:
    """Returns the pixel difference between the current heading pixel (middle pixel of the video frame)
    and the midpoint of the detected green and red gates. Negative = gate is to the left, Positive = gate to the right

    Returns:
        int: A number that dictates the difference between the middle pixel and the midgate pixel.
    """
    # capture a frame from the Video sensor
    video = Video()

    while not video.frame_available():
        time.sleep(1)

    frame = cv2.cvtColor(video.frame(), cv2.COLOR_BGR2HSV)

    red1_lower = (0, 50, 50)
    red1_upper = (10, 255, 255)
    red2_lower = (170, 70, 50)
    red2_upper = (180, 255, 255)
    green_lower = (36,  50,  50)
    green_upper = (86, 255, 255)

    red1_mask = cv2.inRange(frame, red1_lower, red1_upper)
    red2_mask = cv2.inRange(frame, red2_lower, red2_upper)
    red_mask = red1_mask | red2_mask
    green_mask = cv2.inRange(frame, green_lower, green_upper)

    # find the red and green buoy
    red_x, _ = find_buoy(frame, red_mask)
    green_x, _ = find_buoy(frame, green_mask)

    # find the midpoint between the red and green buoy
    mid_x = (red_x + green_x) // 2

    # return the difference from that and the center of the camera
    _, width, _ = frame.shape

    if debug:
        print(f"""red_x: {red_x}
green_x: {green_x}
mid_x: {mid_x}
frame_width: {width}
""")
    return mid_x - width // 2


if __name__ == "__main__":
    main()
