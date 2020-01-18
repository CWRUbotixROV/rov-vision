
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

void calculateCoralContours(Mat img, vector<vector<Point> > *contours, vector<Vec4i> *hierarchy,
	       	int cannyThreshold, Scalar lowColorThreshold, Scalar highColorThreshold, int minArcLength)
{
    // Blur images
    Mat img_thresh;
    blur(img, img_thresh, Size(8, 8));

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
    int threshold = 50;
    int minArc = 30;

    Scalar lowBleach(175, 175, 175);
    Scalar highBleach(256, 256, 256);
    Scalar lowHealthy(100, 0, 160);
    Scalar highHealthy(256, 140, 256);

    vector<vector<Point> > contoursHealthy1, contoursHealthy2, contoursBleach1, contoursBleach2;
    vector<Vec4i> hierarchyHealthy1, hierarchyHealthy2, hierarchyBleach1, hierarchyBleach2;

    calculateCoralContours(img1, &contoursBleach1, &hierarchyBleach1, threshold, lowBleach, highBleach, minArc);
    calculateCoralContours(img2, &contoursBleach2, &hierarchyBleach2, threshold, lowBleach, highBleach, minArc);
    calculateCoralContours(img1, &contoursHealthy1, &hierarchyHealthy1, threshold, lowHealthy, highHealthy, minArc);
    calculateCoralContours(img2, &contoursHealthy2, &hierarchyHealthy2, threshold, lowHealthy, highHealthy, minArc);

    // Create masks for after picture
    Mat afterHealth = Mat::zeros(img2.size(), CV_8UC1);
    Mat afterBleach = Mat::zeros(img2.size(), CV_8UC1);
    Mat afterTotal = Mat::zeros(img2.size(), CV_8UC1);
    Mat afterTotalExpanded = Mat::zeros(img2.size(), CV_8UC1);

    for( size_t i = 0; i< contoursHealthy2.size(); i++ )
    {
        drawContours(afterHealth, contoursHealthy2, (int)i, Scalar(255), FILLED, LINE_8, hierarchyHealthy2, 0 );
        drawContours(afterTotal, contoursHealthy2, (int)i, Scalar(255), FILLED, LINE_8, hierarchyHealthy2, 0 );
        drawContours(afterTotalExpanded, contoursHealthy2, (int)i, Scalar(255), FILLED, LINE_8, hierarchyHealthy2, 0 );
        drawContours(afterTotalExpanded, contoursHealthy2, (int)i, Scalar(255), 20, LINE_8, hierarchyHealthy2, 0 );
    }
    for( size_t i = 0; i< contoursBleach2.size(); i++ )
    {
        drawContours(afterBleach, contoursBleach2, (int)i, Scalar(255), FILLED, LINE_8, hierarchyBleach2, 0 );
        drawContours(afterTotal, contoursBleach2, (int)i, Scalar(255), FILLED, LINE_8, hierarchyBleach2, 0 );
        drawContours(afterTotalExpanded, contoursBleach2, (int)i, Scalar(255), FILLED, LINE_8, hierarchyBleach2, 0 );
        drawContours(afterTotalExpanded, contoursBleach2, (int)i, Scalar(255), 20, LINE_8, hierarchyBleach2, 0 );
    }
    

    // Transfrom before coral onto after picture and create masks 
    Mat beforeHealthy = Mat::zeros(img2.size(), CV_8UC1);
    Mat beforeBleach = Mat::zeros(img2.size(), CV_8UC1);
    Mat beforeTotal = Mat::zeros(img2.size(), CV_8UC1);
    Mat beforeTotalExpanded = Mat::zeros(img2.size(), CV_8UC1);

    for(size_t i = 0; i < contoursHealthy1.size(); i++)
    {
    	vector<Point2f> originalPoints, projectedPoints;
	Mat(contoursHealthy1[i]).copyTo(originalPoints);
	perspectiveTransform(originalPoints,  projectedPoints, H);
	Mat(projectedPoints).copyTo(contoursHealthy1[i]);
    	drawContours(beforeHealthy, contoursHealthy1, int(i), Scalar(255), FILLED, LINE_8, hierarchyHealthy1, 0 );
    	drawContours(beforeTotal, contoursHealthy1, int(i), Scalar(255), FILLED, LINE_8, hierarchyHealthy1, 0 );
    	drawContours(beforeTotalExpanded, contoursHealthy1, int(i), Scalar(255), FILLED, LINE_8, hierarchyHealthy1, 0 );
    	drawContours(beforeTotalExpanded, contoursHealthy1, int(i), Scalar(255), 20, LINE_8, hierarchyHealthy1, 0 );
    }
    for(size_t i = 0; i < contoursBleach1.size(); i++)
    {
    	vector<Point2f> originalPoints, projectedPoints;
	Mat(contoursBleach1[i]).copyTo(originalPoints);
	perspectiveTransform(originalPoints,  projectedPoints, H);
	Mat(projectedPoints).copyTo(contoursBleach1[i]);
    	drawContours(beforeBleach, contoursBleach1, int(i), Scalar(255), FILLED, LINE_8, hierarchyBleach1, 0 );
    	drawContours(beforeTotal, contoursBleach1, int(i), Scalar(255), FILLED, LINE_8, hierarchyBleach1, 0 );
    	drawContours(beforeTotalExpanded, contoursBleach1, int(i), Scalar(255), FILLED, LINE_8, hierarchyBleach1, 0 );
    	drawContours(beforeTotalExpanded, contoursBleach1, int(i), Scalar(255), 20, LINE_8, hierarchyBleach1, 0 );
    }
    
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

    bitwise_and(afterBleach, beforeHealthy, bleaching);

    // Find contours in combined masks
    vector<vector<Point>> growthContours, damageContours, recoveryContours, bleachingContours;
    vector<Vec4i> growthHierarchy, damageHierarchy, recoveryHierarchy, bleachingHierarchy;
    findContours(growth, growthContours, growthHierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    findContours(damage, damageContours, damageHierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    findContours(recovery, recoveryContours, recoveryHierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    findContours(bleaching, bleachingContours, bleachingHierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

    // Display bounding boxes on after picture
    for(size_t i = 0; i < growthContours.size(); i++)
    {
	    Rect boundRect = boundingRect(growthContours[i]);
	    rectangle(img2, boundRect.tl(), boundRect.br(), Scalar(0, 255, 0), 2);
    }
    for(size_t i = 0; i < damageContours.size(); i++)
    {
	    Rect boundRect = boundingRect(damageContours[i]);
	    rectangle(img2, boundRect.tl(), boundRect.br(), Scalar(0, 255, 255), 2);
    }
    for(size_t i = 0; i < recoveryContours.size(); i++)
    {
	    Rect boundRect = boundingRect(recoveryContours[i]);
	    rectangle(img2, boundRect.tl(), boundRect.br(), Scalar(255, 0, 0), 2);
    }
    for(size_t i = 0; i < bleachingContours.size(); i++)
    {
	    Rect boundRect = boundingRect(bleachingContours[i]);
	    rectangle(img2, boundRect.tl(), boundRect.br(), Scalar(0, 0, 255), 2);
    }


    // Show the bounding boxes 
    imshow("Coral Changes", img2);
    waitKey();
    return 0;
}
