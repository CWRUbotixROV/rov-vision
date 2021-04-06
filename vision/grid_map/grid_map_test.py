from vision.grid_map.grid_map import *
from vision.colors import *
from vision.images import *

def draw_lines(frame, mask):
    """Draws HoughLines on image
    For example: 'draw_lines(frame, edges)'"""
    lines = cv2.HoughLinesP(mask, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=100)

    if lines is not None:
        for i in range(len(lines)):
            line = lines[i]

            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

# Used for trackbar
def empty(a):
    pass

def start_mapping(grid_mapper, video):

    cv2.namedWindow("Trackbar")
    cv2.createTrackbar("Thresh1", "Trackbar", 200, 255, empty)
    cv2.createTrackbar("Thresh2", "Trackbar", 210, 255, empty)

    clear_folder("transect", "squares")

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        ksize = 7
        blur = cv2.GaussianBlur(frame, (ksize, ksize), 1)

        thresh1 = cv2.getTrackbarPos("Thresh1", "Trackbar")
        thresh2 = cv2.getTrackbarPos("Thresh2", "Trackbar")

        canny = cv2.Canny(frame, thresh1, thresh2)

        lines = np.zeros_like(frame)
        draw_lines(lines, canny)

        ksize2 = 10
        kernel = np.ones((ksize2, ksize2))
        lines = cv2.dilate(lines, kernel, iterations=1)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        contours = grid_mapper.get_contours(lines, frame)
        grid_mapper.find_squares(contours, frame, grid_mapper)

        show_debug(frame, name="frame", wait=False)
        show_debug(canny, name="canny", wait=False)

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
grid_mapper = GridMapper()

# start_mapping(grid_mapper, video3)
grid_mapper.display_grid()