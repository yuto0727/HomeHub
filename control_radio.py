from time import sleep
import RPi.GPIO as GPIO
import global_val as g

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
    g.data_radio = [0, 0, 0, 0]

    while True:
        g.data_radio[0] = GPIO.input(INPUT_SW_PINS["REMOTE_A"])
        g.data_radio[1] = GPIO.input(INPUT_SW_PINS["REMOTE_B"])
        g.data_radio[2] = GPIO.input(INPUT_SW_PINS["REMOTE_C"])
        g.data_radio[3] = GPIO.input(INPUT_SW_PINS["REMOTE_D"])

        sleep(0.1)
except:
    pass