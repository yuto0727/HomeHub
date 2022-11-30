from time import sleep
import RPi.GPIO as GPIO
import sys, spidev
import mmap_global_val as mg


GPIO.setmode(GPIO.BCM)

MOTOR_A = 20
MOTOR_B = 21
LED = 16

def main():
    motor = Move_Motor(MOTOR_A, MOTOR_B)
    led = LED_light(LED)
    rotation_sensor = AD_Converter()
    global_val = mg.mmap_global_val("global_val.txt")

    try:
        while True:
            dic = global_val.read_val()
            print(dic)


            led.switch(dic["led"])
            sleep(0.2)

    except KeyboardInterrupt:
        GPIO.cleanup()


def _setup():
    motor = Move_Motor(MOTOR_A, MOTOR_B)
    rotation_sensor = AD_Converter()

    try:
        s = int(input("sec*10: "))
        d = input("action: ")

        motor.move(speed=50, action=d)
        for i in range(s):
            enc = rotation_sensor.get_val()
            print(enc)
            sleep(0.1)
        motor.move(speed=0, action="stop")

    except KeyboardInterrupt:
        motor.move(speed=0, action="stop")
        GPIO.cleanup()


class Move_Motor:
    def __init__(self, pin_motor_A, pin_motor_B):
        self.pin_motor_A = pin_motor_A
        self.pin_motor_B = pin_motor_B

        GPIO.setup(self.pin_motor_A, GPIO.OUT)
        GPIO.setup(self.pin_motor_B, GPIO.OUT)

        self.pwm_A = GPIO.PWM(self.pin_motor_A, 50)
        self.pwm_B = GPIO.PWM(self.pin_motor_B, 50)

        self.pwm_A.start(0)
        self.pwm_B.start(0)

    def move(self, speed, action):
        print(f"action: {action}, speed: {speed}")

        if action == "down":
            self.pwm_A.ChangeDutyCycle(speed)
            self.pwm_B.ChangeDutyCycle(0)
        elif action == "up":
            self.pwm_A.ChangeDutyCycle(0)
            self.pwm_B.ChangeDutyCycle(speed)
        elif action == "stop":
            self.pwm_A.ChangeDutyCycle(0)
            self.pwm_B.ChangeDutyCycle(0)
        else:
            print("Error")

class AD_Converter:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000

    def get_val(self):
        resp = self.spi.xfer2([0x78, 0x00])
        val = ((resp[0] << 8) + resp[1]) & 0x3FF
        return val

class LED_light:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def switch(self, status):
        if status:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

if __name__ == "__main__":
    # main()
    _setup()
