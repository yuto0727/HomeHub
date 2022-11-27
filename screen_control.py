from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

OUTPUT_PINS = {}
OUTPUT_PINS["MOTOR_A"] = 20
OUTPUT_PINS["MOTOR_B"] = 21
OUTPUT_PINS["MOTOR_PWM"] = 13

SPI_PINS = {}
SPI_PINS["MOSI"] = 10
SPI_PINS["MISO"] = 9
SPI_PINS["CLK"] = 11
SPI_PINS["CE0"] = 8

class Move_Motor:
    def __init__(self, pin_motor_A, pin_motor_B, pin_pwm):
        self.pin_motor_A = pin_motor_A
        self.pin_motor_B = pin_motor_B
        self.pin_pwm = pin_pwm

        GPIO.setup(self.pin_motor_A, GPIO.OUT)
        GPIO.setup(self.pin_motor_B, GPIO.OUT)
        GPIO.setup(self.pin_pwm, GPIO.OUT)
        # self.pwm = GPIO.PWM(self.pin_pwm, 50)

        GPIO.output(self.pin_motor_A, GPIO.LOW)
        GPIO.output(self.pin_motor_B, GPIO.LOW)

        GPIO.output(self.pin_pwm, GPIO.HIGH)
        # self.pwm.start(0)

    def move(self, direction, speed):

        if direction == 1:
            print("modeA", direction, speed)
            GPIO.output(self.pin_motor_A, GPIO.HIGH)
            GPIO.output(self.pin_motor_B, GPIO.LOW)
            # self.pwm.ChangeDutyCycle(speed)
        elif direction == -1:
            print("modeB", direction, speed)
            GPIO.output(self.pin_motor_A, GPIO.LOW)
            GPIO.output(self.pin_motor_B, GPIO.HIGH)
            # self.pwm.ChangeDutyCycle(speed)
        elif direction == 0:
            print("modeC", direction, speed)
            GPIO.output(self.pin_motor_A, GPIO.LOW)
            GPIO.output(self.pin_motor_B, GPIO.LOW)
            # self.pwm.ChangeDutyCycle(0)
        else:
            pass

def main():
    motor = Move_Motor(OUTPUT_PINS["MOTOR_A"], OUTPUT_PINS["MOTOR_B"], OUTPUT_PINS["MOTOR_PWM"])

    try:
        while True:
            # for i in range(100):
            #     motor.move(1, i)
            #     sleep(0.1)

            motor.move(100, 1)
            sleep(5)

            # for i in range(100):
            #     motor.move(-1, i)
            #     sleep(0.1)

            motor.move(100, -1)
            sleep(5)
    except:
        GPIO.cleanup()

if __name__ == "__main__":
    main()