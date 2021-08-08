from vision.grid_map.grid_map import *
from vision.images import *

# Used for trackbar
def empty(a):
    pass

def start_mapping(mapper, video):
    cv2.namedWindow("Trackbar")

    # For test video 1 and 2
    # cv2.createTrackbar("Thresh1", "Trackbar", 87, 255, empty)
    # cv2.createTrackbar("Thresh2", "Trackbar", 230, 255, empty)

    # For test video 5
    cv2.createTrackbar("Thresh1", "Trackbar", 0, 255, empty)
    cv2.createTrackbar("Thresh2", "Trackbar", 100, 255, empty)

    # Getting frame dimensions
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    mapper.frame_area = width * height

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        mapper.update_frame(frame)

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

def get_color_thresholds(image):
    cv2.namedWindow("HSV")

    cv2.createTrackbar("HUE min", "HSV", 0, 179, empty)
    cv2.createTrackbar("HUE max", "HSV", 179, 179, empty)
    cv2.createTrackbar("SAT min", "HSV", 0, 255, empty)
    cv2.createTrackbar("SAT max", "HSV", 255, 255, empty)
    cv2.createTrackbar("VAL min", "HSV", 0, 255, empty)
    cv2.createTrackbar("VAL max", "HSV", 255, 255, empty)

    while True:
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        h_min = cv2.getTrackbarPos("HUE min", "HSV")
        h_max = cv2.getTrackbarPos("HUE max", "HSV")
        s_min = cv2.getTrackbarPos("SAT min", "HSV")
        s_max = cv2.getTrackbarPos("SAT max", "HSV")
        v_min = cv2.getTrackbarPos("VAL min", "HSV")
        v_max = cv2.getTrackbarPos("VAL max", "HSV")

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        mask = cv2.inRange(image_hsv, lower, upper)

        cv2.imshow("HSV", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"HUE min: {h_min}")
            print(f"HUE max: {h_max}")
            print(f"SAT min: {s_min}")
            print(f"SAT max: {s_max}")
            print(f"VAL min: {v_min}")
            print(f"VAL max: {v_max}")

            break

config.debug = True

# Testing videos
video = get_video("transect", "transect.MOV")
video2 = get_video("transect", "transect2.mp4")
video3 = get_video("transect", "1", "1.mp4")
video4 = get_video("transect", "1", "2.mp4")
video5 = get_video("transect", "2", "1.mp4")

# Testing images
test_image = get_image("transect", "transect_image.png")
# get_color_thresholds(test_image)

# Tests square detection
mapper = GridMapper()

start_mapping(mapper, video5)
# show_neighbors(mapper)
# mapper.map_squares()
# test_display_grid(mapper)

