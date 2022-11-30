from time import sleep
import RPi.GPIO as GPIO
import global_val as g

INPUT_PINS = {}
INPUT_PINS["REMOTE_A"] = 19
INPUT_PINS["REMOTE_B"] = 5
INPUT_PINS["REMOTE_C"] = 26
INPUT_PINS["REMOTE_D"] = 6

GPIO.setmode(GPIO.BCM)
input_pin_names = [i for i in INPUT_PINS.keys()]
for j in input_pin_names:
    GPIO.setup(INPUT_PINS[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        g.data_radio[0] = GPIO.input(INPUT_PINS["REMOTE_A"])
        g.data_radio[1] = GPIO.input(INPUT_PINS["REMOTE_B"])
        g.data_radio[2] = GPIO.input(INPUT_PINS["REMOTE_C"])
        g.data_radio[3] = GPIO.input(INPUT_PINS["REMOTE_D"])

        print(g.data_radio)

        sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()