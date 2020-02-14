#include "shapedetector.h"
#include <string>

class ShapeDetector

{ public:
    void cv::GaussianBlur();

    void ShapeDetector::detect(self,c){
        std::string shape = "unidentified";
        // perimeter
        double::peri = cv2.arcLength(c, True);   
        //use RDP algorithm to simplify shape
        //std::vector<std::vector<cv::Point> > contours;
        //std::vector<cv::Point> approx;
        c::approxPolyDP(c,approx,0.04 * peri, True);  
        
        
        // Check what shape is in image
        // Shapes can only be square, triangle, line, or circle
        std::cout << (len(approx));
        
        double::AREARATIO = 0.4;
        double::ARUPPER = 0.8;
        double::ARLOWER = (4/3);

        // Check if number of sides equals 2,3 or 4 which correspond to line, triangle and square respectively
        if approx.size() ==2{
            shape = "line";
        }
        else if approx.size() ==3{
            shape = "triangle";
        }
        // Check if square or line
        else if approx.size() ==4{  
            Rect::rectangle = boundingRect(approx);
            double::ar = rectangle.width/float(rectangle.height);
            print(ar);
            area = cv2.contourArea(c)
            if area/float(rectangle.width*rectangle.height) <= AREARATIO or ar <= ARUPPER or ar >= ARLOWER:
               { shape = "line";}
            else
                {shape = "square";}
        }
        else
        {
            shape = 'circle';   
        }
        return shape

    }

}
