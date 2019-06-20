import cv2

class CannonVolume:


    refPt = [] #identifies the length between the clicked points
    line = False
    def click_and_measure(event, a, b, flags, param):
    # defines the length of the bump-stick
        image = cv2.imread('real_shapes.png', cv2.IMREAD_COLOR)
        cv2.imshow("image",image)
        cv2.namedWindow('image')
        cv2.waitkey(0)
        global refPt
        line = param[0]

        if event == cv2.EVENT_LBUTTONDOWN:
            refPt = [(a , b)] # a and b are x and y coordinates for line segment
            line = False

        elif event == cv2.EVENT_LBUTTONUP:
            refPt.append[(a , b)]
            line = True

        cv2.line(image,refPt[0],refPt[1],(0,255,0),thickness=1, lineType=8, shift=0)
    cv2.setMouseCallback("image", click_and_measure)
    print(refPt)