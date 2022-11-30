from time import sleep
import RPi.GPIO as GPIO
import sys, spidev
import mmap_global_val as mg


GPIO.setmode(GPIO.BCM)

MOTOR_A = 20
MOTOR_B = 21
LED = 16

TARGET_CLOSE = 30
TARGET_OPEN = 1018

MARGIN = 2
SLOW_DIFF = 150
MOTOR_POWER_MAX = 100
MOTOR_POWER_MIN = 25

def main():
    motor = Move_Motor(MOTOR_A, MOTOR_B)
    led = LED_light(LED)
    rotation_sensor = AD_Converter()

    # ファイル間通信初期化
    global_val = mg.mmap_global_val("global_val.txt")

    # motor     -> 0:停止  1:出す 2:しまう
    # screen_st -> 0: 中間 1:出切 2:巻切
    dic = {"led":0, "motor":0, "screen_st":2}
    global_val.write_val(dic)

    try:
        while True:
            dic = global_val.read_val()
            enc = rotation_sensor.get_val()
            print(dic, enc, end="")


            # screen_st 更新
            if TARGET_CLOSE-MARGIN <= enc <= TARGET_CLOSE+MARGIN:
                dic["screen_st"] = 2
            elif TARGET_OPEN-MARGIN <= enc <= TARGET_OPEN+MARGIN:
                dic["screen_st"] = 1
            else:
                dic["screen_st"] = 0

            # モーター動作
            if dic["motor"] == 0:
                motor.move(speed=0, action="stop")

            elif dic["motor"] == 1:
                if TARGET_OPEN-enc >= SLOW_DIFF:
                    motor.move(speed=MOTOR_POWER_MAX, action="down")
                elif TARGET_OPEN-MARGIN <= enc <= TARGET_OPEN+MARGIN:
                    motor.move(speed=0, action="stop")
                    dic["motor"] = 0
                else:
                    power = min(max(MOTOR_POWER_MIN, TARGET_OPEN-enc), 100)
                    motor.move(speed=power, action="down")

            elif dic["motor"] == 2:
                if enc-TARGET_CLOSE >= SLOW_DIFF:
                    motor.move(speed=MOTOR_POWER_MAX, action="up")
                elif TARGET_CLOSE-MARGIN <= enc <= TARGET_CLOSE+MARGIN:
                    motor.move(speed=0, action="stop")
                    dic["motor"] = 0
                else:
                    power = min(max(MOTOR_POWER_MIN, enc-TARGET_CLOSE), 100)
                    motor.move(speed=power, action="up")

            global_val.write_val(dic)
            led.switch(dic["led"])
            sleep(0.02)

    except KeyboardInterrupt:
        motor.move(speed=0, action="stop")
        GPIO.cleanup()


def _setup():
    motor = Move_Motor(MOTOR_A, MOTOR_B)
    rotation_sensor = AD_Converter()
    # down: 1020, up: 32

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
    main()
    # _setup()
