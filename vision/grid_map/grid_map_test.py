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
    cv2.createTrackbar("Thresh1", "Trackbar", 87, 255, empty)
    cv2.createTrackbar("Thresh2", "Trackbar", 230, 255, empty)

    clear_folder("transect", "squares")

    # Getting frame dimensions
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    grid_mapper.frame_area = width * height

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        ksize = 7
        blur = cv2.GaussianBlur(frame, (ksize, ksize), 1)

        thresh1 = cv2.getTrackbarPos("Thresh1", "Trackbar")
        thresh2 = cv2.getTrackbarPos("Thresh2", "Trackbar")

        canny = cv2.Canny(blur, thresh1, thresh2)

        lines = np.zeros_like(frame)
        draw_lines(lines, canny)

        ksize2 = 10
        kernel = np.ones((ksize2, ksize2))
        lines = cv2.dilate(lines, kernel, iterations=1)
        lines = cv2.cvtColor(lines, cv2.COLOR_BGR2GRAY)

        contours = grid_mapper.get_contours(lines, frame)
        grid_mapper.find_squares(contours, frame)

        show_debug(frame, name="frame", wait=False)

        # if cv2.waitKey(25) & 0xFF == ord('q'):
        #     break

        key = cv2.waitKey(25)
        if key == ord('q'):
            break  # Quit out of video
        elif key == ord('p'):
            cv2.waitKey(-1)  # Pause video

    video.release()
    cv2.destroyAllWindows()


def test_display_grid(mapper):
    squares = []

    for i in range(5):
        squares.append(Grid_Square(i + 1))

    squares[0].classification = Object.FRAGMENT
    squares[0].grid_num = 2

    squares[1].classification = Object.SPONGE
    squares[1].grid_num = 15

    squares[2].classification = Object.STAR
    squares[2].grid_num = 25

    squares[3].classification = Object.CORAL
    squares[3].grid_num = 17

    squares[4].classification = Object.CORAL
    squares[4].grid_num = 18

    mapper.display_grid(squares)

def show_neighbors(mapper):
    print("Format: ID, neighbors[up, down, left, right]")

    for s in mapper.all_squares:
        up = None
        down = None
        left = None
        right = None

        if s.up is not None:
            up = s.up.id

        if s.down is not None:
            down = s.down.id

        if s.left is not None:
            left = s.left.id

        if s.right is not None:
            right = s.right.id

        print(f"ID: {s.id} [{up}, {down}, {left}, {right}]")

config.debug = True

# Testing videos
video = get_video("transect", "transect.MOV")
video2 = get_video("transect", "transect2.mp4")
video3 = get_video("transect", "1", "1.mp4")
video4 = get_video("transect", "1", "2.mp4")

# Tests square detection
mapper = GridMapper()

start_mapping(mapper, video3)
show_neighbors(mapper)
# mapper.map_squares()
# test_display_grid(mapper)


