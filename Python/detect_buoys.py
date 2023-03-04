from typing import Tuple
import cv2
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

    red_x, red_y = find_buoy(hsv, (0, 50, 50), (10, 255, 255))
    green_x, green_y = find_buoy(hsv, (36,  50,  50), (86, 255, 255))
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
        
        # dont want computer to die
        time.sleep(0.5)


def find_buoy(frame: np.ndarray, lower_bound: Tuple[int, int, int], upper_bound: Tuple[int, int, int]) -> Tuple[int, int]:
    """Finds a buoy with the given lower and upper bounds for a color mask

    Args:
        frame (np.ndarray): The frame to find the buoys in
        lower_bound (Tuple[int, int, int]): The lower bound color, in HSV values
        upper_bound (Tuple[int, int, int]): The upper bound color, in HSV values

    Returns:
        Tuple[int, int]: The (x,y) pixel coordinate of the center of the detected buoy
    """
    
    # Color mask the image
    mask = cv2.inRange(frame, lower_bound, upper_bound)

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


def get_gate_delta() -> int:
    """Returns the pixel difference between the current heading pixel (middle pixel of the video frame)
    and the midpoint of the detected green and red gates. Negative = gate is to the left, Positive = gate to the right

    Returns:
        int: A number that dictates the difference between the middle pixel and the midgate pixel.
    """
    # capture a frame from the Video sensor
    video = Video()

    while not video.frame_available():
        time.sleep(1)

    frame = video.frame()

    # find the red and green buoy
    red_x, _ = find_buoy(frame, (0, 50, 50), (10, 255, 255))
    green_x, _ = find_buoy(frame, (36,  50,  50), (86, 255, 255))

    # find the midpoint between the red and green buoy
    mid_x = (red_x + green_x) / 2

    # return the difference from that and the center of the camera
    _, width, _ = frame.shape

    return mid_x - width // 2


if __name__ == "__main__":
    main()
