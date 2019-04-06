#!/bin/bash

gstOptions=$(tr '\n' ' ' < $HOME/gstreamer3.param)

gst-launch-1.0 -v v4l2src device=/dev/video2 do-timestamp=true ! video/x-h264, width=640, height=480, framerate=30 $gstOptions
