import cv2, time, subprocess
from pymavlink import mavutil
from line_follower_2 import LineFollower, Direction
from video import Video
from grid_map import GridMap
import multiprocessing as mp
from multiprocessing import Value

# RC channel IDs (constants)
RC_CHAN_PITCH = 1
RC_CHAN_ROLL = 2
RC_CHAN_THROTTLE = 3
RC_CHAN_YAW = 4
RC_CHAN_FORWARD = 5
RC_CHAN_LATERAL = 6

# PWM values
UP_PWM = 1500
DOWN_PWM = 1700
LEFT_PWM = 1400
RIGHT_PWM = 1600

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
    for i in range(1,7):
        if i==RC_CHAN_THROTTLE:
            set_rc_channel_pwm(RC_CHAN_THROTTLE, 1600)
        else:
            set_rc_channel_pwm(i, 1500)

def motion_child(exit, data):
    while exit.value == 0:
        if data.value == Direction.up.value:
            go_up()
        elif data.value == Direction.down.value:
            go_down()
        elif data.value == Direction.left.value:
            go_left()
        elif data.value == Direction.right.value:
            go_right()
        else:
            stop()

if __name__=='__main__':
    # master = mavutil.mavlink_connection('udpin:192.168.2.1:14540')

    # master.wait_heartbeat()

    lf = LineFollower()
    cap = Video(port=4777)

    # direction = Direction.down

    print("Beginning autonomy")
    # master.arducopter_arm()

    while not cap.frame_available():
        continue
    # frame = cap.frame()
    # lf.direction = Direction.down
    # lf.find_start_dir(frame)
    # direction = lf.direction
    # dirval = Value('d', direction.value)
    # g = Value('d', 0)
    # child = mp.Process(target=motion_child, args=(g, dirval))
    # last_dir = direction
    # child.start()

    map = GridMap(frame)

    try:
        while True:     # run until stopped with Ctrl-C, will change once everything else works
            frame = cap.frame()
            # lf.determine_find_dir(frame)
            # direction = lf.direction
            # dirval = direction.value
            
            # print(direction)
            # if cv2.waitKey(1)==ord('p'):
            #     cv2.imwrite('underwater.png', frame)
            # last_dir = direction

            map.update(frame)
    except KeyboardInterrupt:
        g = Value('d', 1)
        child.join()

    # print("Disarming")
    # stop()
    # master.arducopter_disarm()

