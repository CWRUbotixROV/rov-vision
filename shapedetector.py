import cv2
import imutils
import numpy as np

class ShapeDetector:
    def detect(self, c):
        shape = 'unidentified'
        # perimeter
        peri = cv2.arcLength(c, True)   
        # use RDP algorithm to simplify shape
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)   

        # Check what shape is in image
         # shapes can only be square, triangle, line, or circle
        print(len(approx))
        
        AREARATIO = 0.4
        ARUPPER = 0.8
        ARLOWER = (1/0.75)

        # Check if number of sides equals 2,3 or 4 which correspond to line, triangle and square respectively
        if len(approx)==2:
            shape = 'line'
        elif len(approx)==3:
            shape = 'triangle'
        # Check if square or line
        elif len(approx)==4:    
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w/float(h)
            print(ar)
            area = cv2.contourArea(c)
            if area/float(w*h) <= AREARATIO or ar <= ARUPPER or ar >= ARLOWER:
                shape = 'line'
            else:
                shape = 'square'
        else:
            shape = 'circle'   

        return shape


def add_shape(shape, d):
    if shape in d:
        d[shape] = int(d[shape])+1
    else:
        d[shape] = 1

# detects shapes on a given image after finding edges
def detect_shapes():
    image = cv2.imread('real_shapes.png', cv2.IMREAD_COLOR)
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
    ret, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU) #ret is the optimal threshold value for a bimodal image. otsu is the name of the thresholded image
    cv2.imshow("otsu", otsu)
    cv2.waitKey(0)

    num_shapes = {}

    cnts_ = cv2.findContours(otsu.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = None
    if cv2.__version__[0]=='3':
        cnts = cnts_[1]
    else:
        cnts = cnts_[0]
    sd = ShapeDetector()

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
	
    # Draw line, Square, Circle and Triangle shapes
    # Coordinates determines through trial and error until appropriate proportions of shapes were found
    LINECOORD1 = (25,25)
    LINECOORD2 = (190,45)
    line = cv2.rectangle(blank,LINECOORD1,LINECOORD2, (0,0,255),-1)

    SQUARECOORD1 = (50,95)
    SQUARECOORD2 = (150,200)
    square = cv2.rectangle(blank,SQUARECOORD1, SQUARECOORD2, (0,0,255),-1)

    CIRCLECENTER = (100,275)
    CIRCLERADIUS= 50
    circle = cv2.circle(blank, CIRCLECENTER, CIRCLERADIUS, (0,0,255),-1)

    TRIANGLECOORD1 = (100,350)
    TRIANGLECOORD2 = (50,450)
    TRIANGLECOORD3 = (150,450)
    triangle = np.array([TRIANGLECOORD1,TRIANGLECOORD2,TRIANGLECOORD3])
    triangle = cv2.drawContours(blank, [triangle], 0, (0,0,255), -1)

    # Display number of shapes next to each shape
    # Coordinates determines through trial and error until each number was across from its corresponding shape
    font = cv2.FONT_HERSHEY_SIMPLEX

    LINENUMBCOORD = (400,75)
    LineNumb = cv2.putText(blank,str(num_shapes['line']),LINENUMBCOORD,font,3,(0,0,255),2,cv2.LINE_AA)

    SQUARENUMBCOORD = (400,175)
    SquareNumb = cv2.putText(blank,str(num_shapes['square']),SQUARENUMBCOORD,font,3,(0,0,255),2,cv2.LINE_AA)
    
    CIRCLENUMBCOORD = (400,290)
    CircleNumb = cv2.putText(blank,str(num_shapes['circle']), CIRCLENUMBCOORD,font,3,(0,0,255),2,cv2.LINE_AA)
    
    TRIANGLENUMBCOORD =(400,430)
    TriangleNumb = cv2.putText(blank,str(num_shapes['triangle']),TRIANGLENUMBCOORD,font,3,(0,0,255),2,cv2.LINE_AA)
    
    cv2.imshow("Image", image)

    # Display Results
    if __name__ == "__main__":
        cv2.imshow("Line", line)
        cv2.waitKey(0)
        return num_shapes

num_shapes = detect_shapes()
print(num_shapes)
