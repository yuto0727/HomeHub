from time import sleep
from threading import Thread
import RPi.GPIO as GPIO
import sys, spidev, subprocess, pigpio, json

import irrp


GPIO.setmode(GPIO.BCM)

# GPIOピン設定
MOTOR_A = 20
MOTOR_B = 21
LED = 16
irrp.GPIO = 18

# ロータリーエンコーダしきい値設定
TARGET_CLOSE = 18
TARGET_OPEN = 1020

# スクリーン巻き上げ判定定数設定
MARGIN = 3
MOTOR_POWER_MAX = 100
MOTOR_POWER_MIN = 25
SLOW_DIFF = MOTOR_POWER_MAX-MOTOR_POWER_MIN

# IR関連定数設定
irrp.GLITCH = 100
irrp.PRE_MS = 200
irrp.POST_MS = 15
irrp.VERBOSE = False
irrp.SHORT = 10
irrp.TOLERANCE = 15
irrp.POST_US = irrp.POST_MS * 1000
irrp.PRE_US = irrp.PRE_MS * 1000
irrp.TOLER_MIN = (100 - irrp.TOLERANCE) / 100.0
irrp.TOLER_MAX = (100 + irrp.TOLERANCE) / 100.0

# IR送信コマンドパス設定
CMD_PROJECTOR = "python3 /home/yuto/HomeHub/irrp.py -p -g17 -f /home/yuto/HomeHub/codes_for_devices projector"
CMD_light_ON = "python3 /home/yuto/HomeHub/irrp.py -p -g17 -f /home/yuto/HomeHub/codes_for_devices light:on"
CMD_light_OFF = "python3 /home/yuto/HomeHub/irrp.py -p -g17 -f /home/yuto/HomeHub/codes_for_devices light:off"

# デバイス制御変数
enable_ir_control = False
status_light = False
status_motor = "stop"
is_upward_possible = False
is_downward_possible = False

# プロセス停止用変数
Run = True

def main():
    global enable_ir_control, status_light, status_motor, Run

    # IR関連pigpio初期化
    irrp.pi = pigpio.pi()
    irrp.pi.set_mode(irrp.GPIO, pigpio.INPUT)
    irrp.pi.set_glitch_filter(irrp.GPIO, irrp.GLITCH)
    irrp.pi.callback(irrp.GPIO, pigpio.EITHER_EDGE, irrp.cbf)
    if not irrp.pi.connected:
        exit(0)

    # IR関連変数初期化
    irrp.last_tick = 0
    irrp.in_code = False
    irrp.code = []
    irrp.fetching_code = False

    Thread(target=sub1).start()

    try:
        with open('codes_for_control') as f:
            key_config = json.load(f)
            print("reading...")

            # IR読み取り開始
            while True:
                irrp.code = []
                irrp.fetching_code = True

                # 読み取り待ち
                while irrp.fetching_code:
                    sleep(0.02)

                # 読み取り結果を照合
                key_name = ""
                for key, val in key_config.items():
                    if irrp.compare(val, irrp.code[:]):
                        key_name = key

                # 照合結果によって分岐
                if key_name == "firetv:power":
                    print("press power")
                    # powerボタン -> LEDライト点灯・消灯 & IR制御有効化・無効化
                    status_light = not status_light
                    enable_ir_control = not enable_ir_control

                    # LED切り替え
                    led.switch(status_light)

                elif key_name == "firetv:volume_up" and enable_ir_control:
                    print("press volume_up")
                    if is_upward_possible:
                        status_motor = "up"

                elif key_name == "firetv:volume_down" and enable_ir_control:
                    print("press volume_down")
                    if is_downward_possible:
                        status_motor = "down"

                elif key_name == "firetv:volume_mute":
                    print("press volume_mute")
                    # muteボタン -> 無条件モーター停止
                    status_motor = "stop"

                else:
                    pass

                print("\r                 ", status_motor, is_downward_possible, is_upward_possible, "      ", end="")

    except KeyboardInterrupt:
        Run = False
        irrp.pi.stop()
        motor.stop()
        GPIO.cleanup()

def sub1():
    global status_motor, is_downward_possible, is_upward_possible
    print("sub1 start")
    while Run:
        # print("\r                 ", status_motor, is_downward_possible, is_upward_possible, "      ", end="")
        enc = rotation_sensor.get_val()

        # モーター動作終了判定
        if status_motor != "stop" and (enc <= TARGET_CLOSE+MARGIN or TARGET_OPEN-MARGIN <= enc):
            status_motor = "stop"

        if enc <= TARGET_CLOSE+MARGIN:
            is_downward_possible = True
            is_upward_possible = False
        elif TARGET_OPEN-MARGIN <= enc:
            is_downward_possible = False
            is_upward_possible = True

        # モーター動作分岐
        if status_motor == "stop":
            motor.stop()

        elif status_motor == "up":
            # しきい値とSLOW_DIFF以上の差がある場合 -> 通常スピードで動作
            if enc-TARGET_CLOSE >= SLOW_DIFF:
                motor.move(speed=MOTOR_POWER_MAX, action="up")

            # しきい値とSLOW_DIFF以内の差の場合 -> 差からパワー算出
            else:
                power = min(max(MOTOR_POWER_MIN, enc-TARGET_CLOSE), 100)
                motor.move(speed=power, action="up")

        elif status_motor == "down":
            # しきい値とSLOW_DIFF以上の差がある場合 -> 通常スピードで動作
            if TARGET_OPEN-enc >= SLOW_DIFF:
                motor.move(speed=MOTOR_POWER_MAX, action="down")

            # しきい値とSLOW_DIFF以内の差の場合 -> 差からパワー算出
            else:
                power = min(max(MOTOR_POWER_MIN, TARGET_OPEN-enc), 100)
                motor.move(speed=power, action="down")



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
        # print(f"action: {action}, speed: {speed}")

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

    def stop(self):
        self.pwm_A.ChangeDutyCycle(0)
        self.pwm_B.ChangeDutyCycle(0)

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



def _dev():
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


# 制御インスタンス作成
motor = Move_Motor(MOTOR_A, MOTOR_B)
led = LED_light(LED)
rotation_sensor = AD_Converter()
if __name__ == "__main__":
    main()
    # _dev()
