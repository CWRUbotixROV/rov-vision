#! /bin/bash

# start a second camera feed from the Pi 3. Needs to be run in background with './start_second_cam.sh &'.

gstOptions=$(tr '\n' ' ' < $HOME/gstreamer3.param)

gst-launch-1.0 -v v4l2src device=/dev/video2 do-timestamp=true ! video/x-h264, width=640, height=480, framerate=30 $gstOptions
