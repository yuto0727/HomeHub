from time import sleep
import RPi.GPIO as GPIO
import mmap_global_val as mg

INPUT_PINS = {}
INPUT_PINS["REMOTE_A"] = 6
INPUT_PINS["REMOTE_B"] = 26
INPUT_PINS["REMOTE_C"] = 5
INPUT_PINS["REMOTE_D"] = 19

def main():
    GPIO.setmode(GPIO.BCM)
    input_pin_names = [i for i in INPUT_PINS.keys()]
    for j in input_pin_names:
        GPIO.setup(INPUT_PINS[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    global_val = mg.mmap_global_val("global_val.txt")
    dic = {"ir":[0, 0, 0, 0], "radio":[0, 0, 0, 0], "led":0, "motor":0}

    try:
        while True:
            dic["radio"][0] = GPIO.input(INPUT_PINS["REMOTE_A"])
            dic["radio"][1] = GPIO.input(INPUT_PINS["REMOTE_B"])
            dic["radio"][2] = GPIO.input(INPUT_PINS["REMOTE_C"])
            dic["radio"][3] = GPIO.input(INPUT_PINS["REMOTE_D"])

            global_val.write_val(dic)
            print(dic["radio"])

            sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()