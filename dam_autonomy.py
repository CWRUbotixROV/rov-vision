import cv2, time, subprocess
from pymavlink import mavutil
from line_follower import LineFollower, Direction

# RC channel IDs (constants)
RC_CHAN_PITCH = 1
RC_CHAN_ROLL = 2
RC_CHAN_THROTTLE = 3
RC_CHAN_YAW = 4
RC_CHAN_FORWARD = 5
RC_CHAN_LATERAL = 6

# PWM values
UP_PWM = 1550
DOWN_PWM = 1450
LEFT_PWM = 1450
RIGHT_PWM = 1550

# mavproxy.py --master=udpin:192.168.2.1:14540 --out=udpout:192.168.2.2:14540


def set_rc_channel_pwm(id, pwm=1500):
    """ Set RC channel pwm value

    Args:
        id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if id < 1:
        return
    if id < 9:  # don't set values for channels above 8, since those are used for other things
        rc_channel_values = [65535 for _ in range(8)]
        rc_channel_values[id-1] = pwm
        master.mav.rc_channels_override_send(master.target_system, master.target_component, *rc_channel_values)


def go_down():
    set_rc_channel_pwm(RC_CHAN_THROTTLE, pwm=DOWN_PWM)

def go_up():
    set_rc_channel_pwm(RC_CHAN_THROTTLE, pwm=UP_PWM)

def go_left():
    set_rc_channel_pwm(RC_CHAN_LATERAL, pwm=LEFT_PWM)

def go_right():
    set_rc_channel_pwm(RC_CHAN_LATERAL, pwm=RIGHT_PWM)

def stop():
    for i in range(6):
        set_rc_channel_pwm(i+1, 1500)

def disarm(_master):
    _master.mav.command_long_send(1, 1, 400, 0, 0, 0, 0, 0, 0, 0, 0) # disarm

master = mavutil.mavlink_connection('udpin:192.168.2.1:14540')
# p = subprocess.Popen(['python3', 'follow_line.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

master.wait_heartbeat()
# Should be armed manually from QGroundControl
# master.mav.command_long_send(1, 1, 400, 0, 1, 0, 0, 0, 0, 0, 0)    # arm

lf = LineFollower(port=4777)

direction = Direction.STOP
period = 50   # loop period in milliseconds
tn = 0

try:
    while True:     # run until stopped with Ctrl-C
        tn = tn + period
        direction = lf.next_direction()
        print(direction)
        if direction == Direction.UP:
            go_up()
        elif direction == Direction.DOWN:
            go_down()
        elif direction == Direction.LEFT:
            go_left()
        elif direction == Direction.RIGHT:
            go_right()
        else:
            stop()
        time.sleep(tn - int(round(time.time()*1000)))   # ensure that we update the direction at a constant rate
except KeyboardInterrupt:
    pass

stop()
disarm(master)
