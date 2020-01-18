#include <iostream>
#include "opencv2/core.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/imgcodecs.hpp"
#include "opencv2/features2d.hpp"
#include "opencv2/calib3d.hpp"

using namespace cv;
using namespace std;

const char* keys =
    "{ help h |                  | Print help message. }"
    "{ input1 | coral_before.png          | Path to input image 1. }"
    "{ input2 | coral_after.png | Path to input image 2. }";

// Calculate the the Contours for the coral and throw out contours that are too small
void calculateCoralContours(Mat img, vector<vector<Point> > *contours, vector<Vec4i> *hierarchy, 
		Scalar lowColorThreshold, Scalar highColorThreshold, int minArcLength, Size blurSize)
{
    // Blur images
    Mat img_thresh;
    blur(img, img_thresh, blurSize);

    // Create threshold 
    inRange(img_thresh, lowColorThreshold, highColorThreshold, img_thresh);
    vector<vector<Point>> originalContours;

    findContours( img_thresh, originalContours, *hierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE );
    contours->resize(originalContours.size());
    int j = 0;
    for(int i = 0; i < originalContours.size(); i++)
    {
	if(arcLength(originalContours[i], true) > minArcLength){
		(*contours)[j] = originalContours[i];
		j++;
	}
    }
    contours->resize(j);
}

// Find the contours in ContourImg and display the bounding rectangles in displayImg
void drawContourBoundingRects(Mat contourImg, Mat displayImg, Scalar color, int thickness)
{
    vector<vector<Point>> contours;
    vector<Vec4i> hierarchy;
    findContours(contourImg, contours, hierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

    // Display bounding boxes on after picture
    for(size_t i = 0; i < contours.size(); i++)
    {
	    Rect boundRect = boundingRect(contours[i]);
	    rectangle(displayImg, boundRect.tl(), boundRect.br(), color, thickness);
    }
}

// Draw the contours to an image with only those contours, an image with the all the contours from that picture, and an image where the contours are expanded
void drawMultipleContours(vector<vector<Point>> contours, vector<Vec4i> hierarchy, Mat exclusive, Mat total, Mat totalExpanded, int expandAmount)
{
    for( size_t i = 0; i< contours.size(); i++ )
    {
        drawContours(exclusive, contours, (int)i, Scalar(255), FILLED, LINE_8, hierarchy, 0 );
        drawContours(total, contours, (int)i, Scalar(255), FILLED, LINE_8, hierarchy, 0 );
        drawContours(totalExpanded, contours, (int)i, Scalar(255), FILLED, LINE_8, hierarchy, 0 );
        drawContours(totalExpanded, contours, (int)i, Scalar(255), expandAmount, LINE_8, hierarchy, 0 );
    }
}

// Apply a perspective transform to a list of contours
void transformContours(Mat contourTransform, vector<vector<Point>>* contours)
{
    for(size_t i = 0; i < contours->size(); i++)
    {
    	vector<Point2f> originalPoints, projectedPoints;
	Mat((*contours)[i]).copyTo(originalPoints);
	perspectiveTransform(originalPoints,  projectedPoints, contourTransform);
	Mat(projectedPoints).copyTo((*contours)[i]);
    }
}

int main( int argc, char* argv[] )
{
    CommandLineParser parser( argc, argv, keys );

    Mat img1 = imread( samples::findFile( parser.get<String>("input1") ), IMREAD_COLOR );
    Mat img2 = imread( samples::findFile( parser.get<String>("input2") ), IMREAD_COLOR );
    
    if ( img1.empty() || img2.empty() )
    {
        cout << "Could not open or find the image!\n" << endl;
        parser.printMessage();
        return -1;
    }

    //Detect the keypoints using KAZE features 
    Ptr<KAZE> detector = KAZE::create();
    std::vector<KeyPoint> keypoints1, keypoints2;
    Mat descriptors1, descriptors2;

    detector->detectAndCompute( img1, noArray(), keypoints1, descriptors1 );
    detector->detectAndCompute( img2, noArray(), keypoints2, descriptors2 );
    
    // Matching descriptor vectors with a FLANN based matcher
    Ptr<DescriptorMatcher> matcher = DescriptorMatcher::create(DescriptorMatcher::FLANNBASED);
    std::vector< std::vector<DMatch> > knn_matches;
    matcher->knnMatch( descriptors1, descriptors2, knn_matches, 2 );

    // Filter matches using the Lowe's ratio test
    const float ratio_thresh = 0.7f;
    std::vector<DMatch> good_matches;
    for (size_t i = 0; i < knn_matches.size(); i++)
    {
        if (knn_matches[i][0].distance < ratio_thresh * knn_matches[i][1].distance)
        {
            good_matches.push_back(knn_matches[i][0]);
        }
    }
    
    // Localize the object
    std::vector<Point2f> coral_before;
    std::vector<Point2f> coral_after;

    for( size_t i = 0; i < good_matches.size(); i++ )
    {
        // Get the keypoints from the good matches
        coral_before.push_back( keypoints1[ good_matches[i].queryIdx ].pt );
        coral_after.push_back( keypoints2[ good_matches[i].trainIdx ].pt );
    }

    Mat H = findHomography( coral_before, coral_after, RANSAC );

    // Find Contours in before and after pictures
    int minArc = 30;
    Size blurSize = Size(8, 8);

    Scalar lowBleach(175, 175, 175);
    Scalar highBleach(256, 256, 256);
    Scalar lowHealthy(100, 0, 160);
    Scalar highHealthy(256, 140, 256);

    vector<vector<Point> > contoursHealthy1, contoursHealthy2, contoursBleach1, contoursBleach2;
    vector<Vec4i> hierarchyHealthy1, hierarchyHealthy2, hierarchyBleach1, hierarchyBleach2;

    calculateCoralContours(img1, &contoursBleach1, &hierarchyBleach1, lowBleach, highBleach, minArc, blurSize);
    calculateCoralContours(img2, &contoursBleach2, &hierarchyBleach2, lowBleach, highBleach, minArc, blurSize);
    calculateCoralContours(img1, &contoursHealthy1, &hierarchyHealthy1, lowHealthy, highHealthy, minArc, blurSize);
    calculateCoralContours(img2, &contoursHealthy2, &hierarchyHealthy2, lowHealthy, highHealthy, minArc, blurSize);

    // Create masks for after picture
    Mat afterHealth = Mat::zeros(img2.size(), CV_8UC1);
    Mat afterBleach = Mat::zeros(img2.size(), CV_8UC1);
    Mat afterTotal = Mat::zeros(img2.size(), CV_8UC1);
    Mat afterTotalExpanded = Mat::zeros(img2.size(), CV_8UC1);

    drawMultipleContours(contoursHealthy2, hierarchyHealthy2, afterHealth, afterTotal, afterTotalExpanded, 20);
    drawMultipleContours(contoursBleach2, hierarchyBleach2, afterBleach, afterTotal, afterTotalExpanded, 20);

    // Transfrom before coral onto after picture and create masks 
    Mat beforeHealth = Mat::zeros(img2.size(), CV_8UC1);
    Mat beforeBleach = Mat::zeros(img2.size(), CV_8UC1);
    Mat beforeTotal = Mat::zeros(img2.size(), CV_8UC1);
    Mat beforeTotalExpanded = Mat::zeros(img2.size(), CV_8UC1);

    transformContours(H, &contoursHealthy1);
    transformContours(H, &contoursBleach1);

    drawMultipleContours(contoursHealthy1, hierarchyHealthy1, beforeHealth, beforeTotal, beforeTotalExpanded, 20);
    drawMultipleContours(contoursBleach1, hierarchyBleach1, beforeBleach, beforeTotal, beforeTotalExpanded, 20);
    
    // Combine masks to create new masks for growth, damage, bleaching, and recovery
    Mat growth = Mat::zeros(img2.size(), CV_8UC1);
    Mat damage = Mat::zeros(img2.size(), CV_8UC1);
    Mat bleaching = Mat::zeros(img2.size(), CV_8UC1); 
    Mat recovery = Mat::zeros(img2.size(), CV_8UC1); 

    bitwise_not(beforeTotalExpanded, growth);
    bitwise_and(growth, afterTotal, growth);

    bitwise_not(afterTotalExpanded, damage);
    bitwise_and(damage, beforeTotal, damage);

    bitwise_and(afterHealth, beforeBleach, recovery);

    bitwise_and(afterBleach, beforeHealth, bleaching);

    // Find contours in combined masks and draw bounding boxes
    int lineThickness = 2;

    drawContourBoundingRects(growth, img2, Scalar(0, 255, 0), lineThickness);
    drawContourBoundingRects(damage, img2, Scalar(0, 255, 255), lineThickness);
    drawContourBoundingRects(recovery, img2, Scalar(255, 0, 0), lineThickness);
    drawContourBoundingRects(bleaching, img2, Scalar(0, 0, 255), lineThickness);

    // Show the bounding boxes 
    imshow("Coral Changes", img2);
    waitKey();
    return 0;
}
