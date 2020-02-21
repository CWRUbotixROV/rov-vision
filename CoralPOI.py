import cv2
import imutils
import numpy as np

# Use otsu threshholding to find contours of shapes in image and count number of sides in contours
# to determine which shapes and how many are present in the image
image = cv2.imread('real_shapes.png', cv2.IMREAD_COLOR)
class CoralPOI:
    # Take in image and determine the shapes with the number of sides
    def detect(self, c):
        shape = 'unidentified'
        # perimeter
        peri = cv2.arcLength(c, True)
        # use RDP algorithm to simplify shape
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)   

        # Check what shape is in image
        # Shapes can only be square, triangle, line, or circle
        print(len(approx))
        
        AREARATIO = 0.4
        ARUPPER = 0.8
        ARLOWER = (1/0.75)

        # Check if number of sides equals 2, 4, or 10 which correspond to line, square and star respectively
        if len(approx)==2:
            shape = 'line'
        # Check if square or rect
        elif len(approx)==4:    
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w/float(h)
            print(ar)
            area = cv2.contourArea(c)
            if area/float(w*h) <= AREARATIO or ar <= ARUPPER or ar >= ARLOWER:
                shape = 'rect'
            else:
                shape = 'square'
        elif len(approx) >=10:
            shape = 'star'
        else:
            shape = 'circle'   

        return shape

    # Adds shape to array and increases count for that shape
    def add_shape(shape, d):
        if shape in d:
            d[shape] = int(d[shape])+1
        else:
            d[shape] = 1
    def Location():
        #determine location of each shape and return coordinates for GridMap
        img = cv2.imread('real_shapes.png', cv2.IMREAD_COLOR)
        M = im.shape[0]//2
        N = im.shape[1]//2
        x, y = img.shape[:2]
        for x in range(0,im.shape[0],M):
            for y in range(0,im.shape[1],N):
                tiles = [im[x:x+M,y:y+N] 
    
    def GridMap():
        # Draw a grid
        #  with 80 btwn yy
        CELL_SIZE = 100
        PADDING = 20
        HEIGHT = CELL_SIZE * 3 + (2 * PADDING)
        WIDTH = CELL_SIZE * 9 + (2 * PADDING)
        THICKNESS = 2
        # Create white image
        image2 = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
        cv2.rectangle(image2, (0, 0), (WIDTH, HEIGHT), (255, 255, 255), -1)
        # Draw grid
        for n in range(10):
            cv2.line(image2, (CELL_SIZE * n + PADDING, PADDING), (CELL_SIZE * n + PADDING, CELL_SIZE * 3 + PADDING), (0, 0, 0), THICKNESS)
        for n in range(4):
            cv2.line(image2, (PADDING, CELL_SIZE * n + PADDING), (CELL_SIZE * 9 + PADDING, CELL_SIZE * n + PADDING), (0, 0, 0), THICKNESS)
        CIRCLECENTER = (100,275)
        CIRCLERADIUS= 25
        circle = cv2.circle(image2, CIRCLECENTER, CIRCLERADIUS, (0,0,255),0)
        cv2.imshow("grid", image2)

    # detects shapes on a given image after finding edges
    def detect_shapes():
        # created a new screen for the display of the counts for the shapes
        blank = cv2.imread('blank.png', cv2.IMREAD_COLOR) 
        # resize to simplify shapes
        resized = imutils.resize(image, width=300)
        ratio = image.shape[0] / float(resized.shape[0])
        #finds edges of the image
        edges = cv2.Canny(image,100,200) 
        
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Use an adaptive threshold on the image, since lighting is expected to be non-uniform.
        ret, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU) 
        #ret is the optimal threshold value for a bimodal image
        #otsu is the name of the thresholded image
        cv2.imshow("otsu", otsu)
        cv2.waitKey(0)

        num_shapes = {}

        cnts_ = cv2.findContours(otsu.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = None
        if cv2.__version__[0]=='3':
            cnts = cnts_[1]
        else:
            cnts = cnts_[0]
        sd = CoralPOI()

        for c in cnts:
            area = cv2.contourArea(c)
            # compute centroid of the contour as it would be on the original image
            M = cv2.moments(c)

            # ignore contours that are too small to be species
            UPPERCONTOURTHRESH = 0.25
            LOWERCONTOURTHRESH = 0.002

            if c.shape[0] > 2 and\
            area/(resized.shape[0]*resized.shape[1]) > LOWERCONTOURTHRESH and\
            area/(resized.shape[0]*resized.shape[1]) < UPPERCONTOURTHRESH:
                # find centroid of contour
                # if M['m00'] == 0 shape = line
                cx = int((M["m10"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
                cy = int((M["m01"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
                shape = sd.detect(c)
                add_shape(shape, num_shapes)

                c = c.astype(float)
                c = c*ratio
                c = c.astype(int)
                cv2.drawContours(image, [c], -1, (255, 0, 0), 2)
                cv2.putText(image, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        #CIRCLECENTER = (100,275)
        #CIRCLERADIUS= 50
        #circle = cv2.circle(blank, CIRCLECENTER, CIRCLERADIUS, (0,0,255),-1)
        
        cv2.imshow("Image", image)

        # Display Results
        if __name__ == "__main__":
            GridMap()
            Location()
            cv2.waitKey(0)
            return num_shapes

num_shapes = detect_shapes()
print(num_shapes)
