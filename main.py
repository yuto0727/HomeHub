from time import sleep
from threading import Thread
import RPi.GPIO as GPIO
import sys, spidev, subprocess, pigpio, json, os

# コマンドパス設定
PATH = os.path.dirname(__file__)
print(f"path: {PATH}")
PATH_IR = f"{PATH}/ir_codes/codes_for_control"
CMD_PROJECTOR = f"{PATH}/irrp.py -p -g17 -f {PATH}/ir_codes/codes_for_devices projector"
CMD_light_ON = f"{PATH}/irrp.py -p -g17 -f {PATH}/ir_codes/codes_for_devices light:on"
CMD_light_OFF = f"{PATH}/irrp.py -p -g17 -f {PATH}/ir_codes/codes_for_devices light:off"


# 外部スクリプトimport
sys.path.append(PATH)
import irrp

irrp.GPIO = 18
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

# GPIOピン設定
MOTOR_A = 20
MOTOR_B = 21
LED = 16

# ロータリーエンコーダしきい値設定
TARGET_CLOSE = 18
TARGET_OPEN = 1023

# スクリーン巻き上げ判定定数設定
MARGIN = 3
MOTOR_POWER_MAX = 100
MOTOR_POWER_MIN = 25
SLOW_DIFF = MOTOR_POWER_MAX-MOTOR_POWER_MIN

# デバイス制御変数
enable_ir_control = False
status_light = False
status_motor = "stop"
is_upward_possible = False
is_downward_possible = False

# プロセス停止用変数
is_running = True

def main():
    global status_motor, enable_ir_control, status_light, is_running, is_upward_possible, is_downward_possible

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

    # スクリーンの状態取得
    set_init_status()

    # サブプロセススタート
    Thread(target=sub_loop_motor).start()

    for i in range(3):
        led.switch(True)
        sleep(0.25)
        led.switch(False)
        sleep(0.25)

    try:
        with open(PATH_IR) as f:
            key_config = json.load(f)

            # IR読み取り開始
            print("main start")
            while True:
                irrp.code = []
                irrp.fetching_code = True

                # 読み取り待ち
                print("reading...")
                while irrp.fetching_code:
                    sleep(0.02)

                # 読み取り結果を照合
                key_name = ""
                for key, val in key_config.items():
                    if irrp.compare(val, irrp.code[:]):
                        key_name = key

                # 照合結果によって分岐
                # powerボタン -> LEDライト点灯・消灯 & IR制御有効化・無効化
                if key_name == "firetv:power":
                    print("press power")
                    if enable_ir_control:
                        enable_ir_control = False

                        if status_light:
                            status_light = False
                            led.switch(False)
                        else:
                            status_light = True
                            led.switch(False)
                            sleep(0.1)
                            led.switch(True)
                    else:
                        print("press power -> enable")
                        enable_ir_control = True

                        if status_light:
                            led.switch(False)
                            sleep(0.1)
                            led.switch(True)
                        else:
                            led.switch(True)

                # volume_upボタン -> モーターup & 下降可能フラグたてる
                elif key_name == "firetv:volume_up" and enable_ir_control:
                    print("press volume_up")
                    if is_upward_possible:
                        status_motor = "up"
                        is_downward_possible = True
                        enable_ir_control = False
                        led.switch(status_light)

                # volume_downボタン -> モーターdown & 上昇可能フラグたてる
                elif key_name == "firetv:volume_down" and enable_ir_control:
                    print("press volume_down")
                    if is_downward_possible:
                        status_motor = "down"
                        is_upward_possible = True
                        enable_ir_control = False
                        led.switch(status_light)

                # volume_muteボタン -> 無条件モーター停止
                elif key_name == "firetv:volume_mute":
                    print("press volume_mute")
                    status_motor = "stop"
                    enable_ir_control = False

                else:
                    enable_ir_control = False

    except KeyboardInterrupt:
        is_running = False
        irrp.pi.stop()
        motor.stop()
        GPIO.cleanup()

def sub_loop_motor():
    global status_motor, is_running, is_upward_possible, is_downward_possible
    sleep(2)
    print("sub_loop_motor start")
    enc_prev = 0

    while is_running:
        enc = rotation_sensor.get_val()
        if (enc < 10):
            # print(f"prev: {enc_prev}, now: {enc} def: {enc-enc_prev} !!pass")
            continue

        elif abs(enc-enc_prev) > 3:
            # print(f"prev: {enc_prev}, now: {enc} def: {enc-enc_prev} !!pass")
            enc_prev = enc
            continue

        # else:
            # print(f"prev: {enc_prev}, now: {enc} def: {enc-enc_prev}")

        # モーター動作分岐
        if status_motor == "stop":
            motor.stop()

        elif status_motor == "up":
            # しきい値とSLOW_DIFF以上の差がある場合 -> 通常スピードで動作
            if enc-TARGET_CLOSE >= SLOW_DIFF:
                motor.move(speed=MOTOR_POWER_MAX, action="up")

            # しきい値を超えた場合 -> モーター停止
            elif enc <= TARGET_CLOSE:
                    motor.stop()
                    status_motor = "stop"
                    is_downward_possible = True
                    is_upward_possible = False
                    # print(f"stop prev: {enc_prev}, now: {enc} def: {enc-enc_prev}")

            # しきい値とSLOW_DIFF以内の差の場合 -> 差からパワー算出
            else:
                power = min(max(MOTOR_POWER_MIN, enc-TARGET_CLOSE), 100)
                motor.move(speed=power, action="up")

        elif status_motor == "down":
            # しきい値とSLOW_DIFF以上の差がある場合 -> 通常スピードで動作
            if TARGET_OPEN-enc >= SLOW_DIFF:
                motor.move(speed=MOTOR_POWER_MAX, action="down")

            # しきい値を超えた場合 -> モーター停止
            elif TARGET_OPEN <= enc:
                    motor.stop()
                    status_motor = "stop"
                    is_downward_possible = False
                    is_upward_possible = True
                    # print(f"stop prev: {enc_prev}, now: {enc} def: {enc-enc_prev}")

            # しきい値とSLOW_DIFF以内の差の場合 -> 差からパワー算出
            else:
                power = min(max(MOTOR_POWER_MIN, TARGET_OPEN-enc), 100)
                motor.move(speed=power, action="down")

        enc_prev = enc

class Move_Motor:
    def __init__(self, pin_motor_A, pin_motor_B):
        self.pin_motor_A = pin_motor_A
        self.pin_motor_B = pin_motor_B

        GPIO.setmode(GPIO.BCM)
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
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def switch(self, status):
        if status:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)

def set_init_status():
    global is_downward_possible, is_upward_possible
    enc = rotation_sensor.get_val()

    # スクリーンが閉じきった場合
    if enc <= TARGET_CLOSE+MARGIN:
        is_downward_possible = True
        is_upward_possible = False

    # スクリーンが開ききった状態の場合
    elif TARGET_OPEN-MARGIN <= enc:
        is_downward_possible = False
        is_upward_possible = True

    else:
        is_downward_possible = True
        is_upward_possible = True

# def _dev():
#     motor = Move_Motor(MOTOR_A, MOTOR_B)
#     rotation_sensor = AD_Converter()
#     # down: 1020, up: 32

#     try:
#         s = int(input("sec*10: "))
#         d = input("action: ")

#         motor.move(speed=50, action=d)
#         for i in range(s):
#             enc = rotation_sensor.get_val()
#             print(enc)
#             sleep(0.1)
#         motor.move(speed=0, action="stop")

#     except KeyboardInterrupt:
#         motor.move(speed=0, action="stop")
#         GPIO.cleanup()

if __name__ == "__main__":
    # try:
    led = LED_light(LED)
    rotation_sensor = AD_Converter()
    motor = Move_Motor(MOTOR_A, MOTOR_B)

    main()
        # _dev()
    # except Exception as e:
        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # logging.warning(f"error:{e} ({exc_type}) at line{exc_tb.tb_lineno} in {fname}")

