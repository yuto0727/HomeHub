from time import sleep
import RPi.GPIO as GPIO
import sys, spidev

GPIO.setmode(GPIO.BCM)

OUTPUT_PINS = {}
OUTPUT_PINS["MOTOR_A"] = 20
OUTPUT_PINS["MOTOR_B"] = 21

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

    def move(self, speed, direction):
        print(f"direction:{direction}, speed:{speed}")

        if direction == 1:
            self.pwm_A.ChangeDutyCycle(speed)
            self.pwm_B.ChangeDutyCycle(0)
        elif direction == -1:
            self.pwm_A.ChangeDutyCycle(0)
            self.pwm_B.ChangeDutyCycle(speed)
        elif direction == 0:
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

def main():
    motor = Move_Motor(OUTPUT_PINS["MOTOR_A"], OUTPUT_PINS["MOTOR_B"])
    rotation_sensor = AD_Converter()

    try:
        while True:
            print(rotation_sensor.get_val())
            sleep(0.1)
    except:
        GPIO.cleanup()

if __name__ == "__main__":
    main()