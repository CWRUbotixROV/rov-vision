#! /usr/bin/env python3

import time, subprocess
from pymavlink import mavutil

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


# TODO implement positive control so the robot isn't moving unless it is actively told to
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

# p = subprocess.Popen(['sl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# while p.poll() is None:
#     output = p.stdout.readline()
#     print(output)
