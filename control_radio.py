from time import sleep
import RPi.GPIO as GPIO
import global_val as g

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
        if GPIO.input(INPUT_PINS["REMOTE_A"]) == GPIO.HIGH:
            print("press A")
            g.data_radio[0] = 1
        if GPIO.input(INPUT_PINS["REMOTE_B"]) == GPIO.HIGH:
            print("press B")
            g.data_radio[1] = 1
        if GPIO.input(INPUT_PINS["REMOTE_C"]) == GPIO.HIGH:
            print("press C")
            g.data_radio[2] = 1
        if GPIO.input(INPUT_PINS["REMOTE_D"]) == GPIO.HIGH:
            print("press D")
            g.data_radio[3] = 1

        sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()