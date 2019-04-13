# Opens a UDP video stream from the Pi Zero to the Pi 3.
gst-launch-1.0 -v udpsrc port=4791 caps='application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264' ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink sync=false
