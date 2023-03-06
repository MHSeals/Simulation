from gstream import Video
import time
import cv2

def main(num_frames = 1):
    video = Video()
    for i in range(num_frames):
        while not video.frame_available():
            time.sleep(1)

        frame = video.frame()
        cv2.imwrite(f'./frames/frame-{i:02d}.jpg', frame)


if __name__ == '__main__':
    main(100)
