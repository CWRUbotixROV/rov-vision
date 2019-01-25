#! /usr/bin/env python3
import cv2, time, subprocess
import numpy as np
from pymavlink import mavutil
import gi
from video import Video

# RC channel IDs (constants)
RC_CHAN_PITCH = 1
RC_CHAN_ROLL = 2
RC_CHAN_THROTTLE = 3
RC_CHAN_YAW = 4
RC_CHAN_FORWARD = 5
RC_CHAN_LATERAL = 6

# mavproxy.py --master=udpin:192.168.2.1:14540 --out=udpout:192.168.2.2:14540


def set_rc_channel_pwm(id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if id < 1:
        return
    if id < 9:
        rc_channel_values = [65535 for _ in range(8)]
        rc_channel_values[id-1] = pwm
        master.mav.rc_channels_override_send(master.target_system, master.target_component, *rc_channel_values)


def go_down():
    set_rc_channel_pwm(RC_CHAN_THROTTLE, 1450)  # half speed, I think

def go_up():
    set_rc_channel_pwm(RC_CHAN_THROTTLE, 1550)

def go_left():
    set_rc_channel_pwm(RC_CHAN_LATERAL, 1450)

def go_right():
    set_rc_channel_pwm(RC_CHAN_LATERAL, 1550)

def get_direction():
    return

master = mavutil.mavlink_connection('udpin:192.168.2.1:14540')
# p = subprocess.Popen(['python3', 'follow_line.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

master.wait_heartbeat()
master.mav.command_long_send(1, 1, 400, 0, 1, 0, 0, 0, 0, 0, 0)    # arm

# cap = cv2.VideoCapture('udp://@192.168.2.1:4777')
stream = Video(port=4777)

img = None
cnt_crack = None
found = False
last_time = 0

while(True):
    if not stream.frame_available():
        continue
    img = stream.frame()

    new_time = time.time()
    print(1/float(new_time-last_time))  # update rate, for debugging
    last_time = new_time

    # img = cv2.imread('/home/sam/Pictures/screwdriver.jpg')
    # img = cv2.GaussianBlur(img, (5, 5), 0)
    lower_red = np.array([0, 0, 50])
    upper_red = np.array([80, 80, 255])
    lower_blue = np.array([50, 0, 0])
    upper_blue = np.array([255, 50, 50])

    # apply masks
    mask_red = cv2.inRange(img, lower_red, upper_red)
    mask_blue = cv2.inRange(img, lower_blue, upper_blue)
    im_red = cv2.bitwise_and(img, img, mask=mask_red)
    im_blue = cv2.bitwise_and(img, img, mask=mask_blue)

    # threshold
    ret_r, im_red = cv2.threshold(im_red, 60, 255, cv2.THRESH_BINARY)
    ret_b, im_blue = cv2.threshold(im_blue, 60, 255, cv2.THRESH_BINARY)

    # flatten so findContours doesn't get mad
    im_red = cv2.cvtColor(im_red, cv2.COLOR_BGR2GRAY)
    im_blue = cv2.cvtColor(im_blue, cv2.COLOR_BGR2GRAY)

    # find contours
    im_red, contours_r, hierarchy_r = cv2.findContours(im_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    im_blue, contours_b, hierarchy_b = cv2.findContours(im_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours_r) > 0:
        cnt = max(contours_r, key=cv2.contourArea)    # find largest contour
        x, y, w, h = cv2.boundingRect(cnt)
        hull = cv2.convexHull(cnt)
        if cv2.contourArea(hull)/cv2.contourArea(cnt) > 2.5:     # has a bend in it
            # print("Looks like a turn")
            go_left()
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        else:
            # print('Keep going')
            go_down()

        # cv2.drawContours(img, [hull], 0, (0, 255, 0), 2)
        # cv2.drawContours(img, [cnt], 0, (255, 0, 0), 2)
        if len(contours_b) > 0:
            crack = max(contours_b, key=cv2.contourArea)
            # if cv2.contourArea(crack) > 1000:
            #     print('Crack found!')
            #     x, y, w, h = cv2.boundingRect(crack)
            #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            #     cnt_crack = crack
            #     found = True
    else:
        print('No red line found')

    cv2.imshow('image', img)
    if (cv2.waitKey(1) & 0xFF == ord('q')) or found:
        break

cv2.imshow('image', img)
cv2.waitKey(0)

if cnt_crack is not None:
    print(cv2.boundingRect(cnt_crack)[2])

cv2.destroyAllWindows()