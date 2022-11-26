from time import time, sleep
import RPi.GPIO as GPIO
import rospy
from std_msgs.msg import Int32MultiArray

CTRL_PERIOD = 0.02

INPUT_PINS = {}
INPUT_PINS["REMOTE_A"] = 5
INPUT_PINS["REMOTE_B"] = 6
INPUT_PINS["REMOTE_C"] = 19
INPUT_PINS["REMOTE_D"] = 26

GPIO.setmode(GPIO.BCM)
input_pin_names = [i for i in INPUT_PINS.keys()]
for j in input_pin_names:
    GPIO.setup(INPUT_PINS[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    rospy.init_node('remote')
    pub_remote = rospy.Publisher('remote', Int32MultiArray)
    loop_rate = rospy.Rate(1/CTRL_PERIOD)

    message = [0, 0, 0, 0]

    while True:
        message[0] = GPIO.input(INPUT_SW_PINS["REMOTE_A"])
        message[1] = GPIO.input(INPUT_SW_PINS["REMOTE_B"])
        message[2] = GPIO.input(INPUT_SW_PINS["REMOTE_C"])
        message[3] = GPIO.input(INPUT_SW_PINS["REMOTE_D"])

        pub_remote.publish(Int32MultiArray(data=message))
        loop_rate.sleep()
except:
    pass