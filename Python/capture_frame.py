from gstream import Video
import time
import cv2

def main():
    video = Video()
    while not video.frame_available():
        time.sleep(1)

    frame = video.frame()
    cv2.imwrite('./frames/frame-1.jpg', frame)
    cv2.imshow(frame)
    cv2.destroyAllWindows()
    pass


if __name__ == '__main__':
    main()
