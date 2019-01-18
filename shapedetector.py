import cv2, imutils


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        shape = 'unidentified'
        peri = cv2.arcLength(c, True)   # perimeter
        approx = cv2.approxPolyDP(c, 0.04*peri, True)   # use RDP algorithm to simplify shape

        print(len(approx))
        if len(approx)==2:
            shape = 'line'
        elif len(approx)==3:
            shape = 'triangle'
        elif len(approx)==4:    # could be square or line
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w/float(h)
            area = cv2.contourArea(c)
            if area/float(w*h) <= 0.4 or ar <= 0.9 or ar >= 1.1:
                shape = 'line'
            else:
                shape = 'square'
        else:
            shape = 'circle'    # shapes can only be square, triangle, line, or circle

        return shape


def add_shape(shape, d):
    if shape in d:
        d[shape] = int(d[shape])+1
    else:
        d[shape] = 1


def detect_shapes():
    image = cv2.imread('shapes.png', cv2.IMREAD_COLOR)
    resized = imutils.resize(image, width=300)  # resize to simplify shapes
    ratio = image.shape[0] / float(resized.shape[0])

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Here we use an adaptive threshold on the image, since we expect the lighting to be non-uniform.
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 0)
    cv2.imshow("thresh", thresh)
    cv2.waitKey(0)

    num_shapes = {}

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    sd = ShapeDetector()

    for c in cnts:
        # compute centroid of the contour as it would be on the original image
        M = cv2.moments(c)
        if c.shape[0] > 2:  # ignore contours that can't possibly be closed
            cx = int((M["m10"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            cy = int((M["m01"] / M["m00"]) * ratio) if M['m00'] != 0 else 0
            shape = sd.detect(c)
            add_shape(shape, num_shapes)

            c = c.astype(float)
            c = c*ratio
            c = c.astype(int)
            cv2.drawContours(image, [c], -1, (255, 0, 0), 2)
            cv2.putText(image, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            cv2.imshow("Image", image)
            cv2.waitKey(0)

    return num_shapes


num_shapes = detect_shapes()
print(num_shapes)
