from vision.grid_map.grid_map import *
from vision.colors import *
from vision.images import *

# Used for trackbar
def empty(a):
    pass

def start_mapping(video):

    grid_mapper = GridMapper(0)

    cv2.namedWindow("Trackbar")
    cv2.createTrackbar("Thresh1", "Trackbar", 87, 255, empty)
    cv2.createTrackbar("Thresh2", "Trackbar", 230, 255, empty)

    clear_folder("transect", "squares")

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        blur = cv2.GaussianBlur(frame, (7, 7), 1)

        thresh1 = cv2.getTrackbarPos("Thresh1", "Trackbar")
        thresh2 = cv2.getTrackbarPos("Thresh2", "Trackbar")

        canny = cv2.Canny(blur, thresh1, thresh2)

        lines = np.zeros_like(frame)
        draw_lines(lines, canny)

        kernel = np.ones((10, 10))
        lines = cv2.dilate(lines, kernel, iterations=1)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        contours = get_contours(lines, frame)
        find_squares(contours, frame, grid_mapper)

        show_debug(frame, name="frame", wait=False)
        # show_debug(canny, name="canny", wait=False)

        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     break

        key = cv2.waitKey(25)
        if key == ord('q'):
            break  # Quit out of video
        elif key == ord('p'):
            cv2.waitKey(-1)  # Pause video

    video.release()
    cv2.destroyAllWindows()

config.debug = True

# Testing videos
video = get_video("transect", "transect.MOV")
video2 = get_video("transect", "transect2.mp4")
video3 = get_video("transect", "1", "1.mp4")
video4 = get_video("transect", "1", "2.mp4")

# Tests square detection

start_mapping(video)
# display_grid()