from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

OUTPUT_PINS = {}
OUTPUT_PINS["MOTOR_A"] = 20
OUTPUT_PINS["MOTOR_B"] = 21

SPI_PINS = {}
SPI_PINS["MOSI"] = 10
SPI_PINS["MISO"] = 9
SPI_PINS["CLK"] = 11
SPI_PINS["CE0"] = 8

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

def main():
    motor = Move_Motor(OUTPUT_PINS["MOTOR_A"], OUTPUT_PINS["MOTOR_B"])

    try:
        while True:
            for i in range(30, 101, 2):
                motor.move(i, -1)
                sleep(0.02)

            sleep(2)

            for i in range(100, 0, -2):
                motor.move(i, -1)
                sleep(0.01)

            motor.move(0, 0)
            sleep(2)
    except:
        GPIO.cleanup()

if __name__ == "__main__":
    main()