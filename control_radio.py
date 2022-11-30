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

    # ファイル間通信初期化
    global_val = mg.mmap_global_val("global_val.txt")

    # motor     -> 0:停止  1:出す 2:しまう
    # screen_st -> 0: 中間 1:出切 2:巻切
    dic = {"led":0, "motor":0, "screen_st":2}
    global_val.write_val(dic)

    prev_status = {}

    try:
        while True:
            if GPIO.input(INPUT_PINS["REMOTE_A"]) and not prev_status["REMOTE_A"]:
                # Aボタン -> スクリーンアップ・ダウン
                dic = global_val.read_val()

                if dic["screen_st"] == 0:
                    # 中間
                    if dic["motor"] == 0 or dic["motor"] == 1:
                        # 中間で停止状態または中間で展開中 -> 収納
                        dic["motor"] = 2
                    elif dic["motor"] == 2:
                        # 中間で収納中 -> 展開
                        dic["motor"] = 1

                elif dic["screen_st"] == 1:
                    # 出切 -> 収納
                    dic["motor"] = 2

                elif dic["screen_st"] == 2:
                    # 巻切 -> 展開
                    dic["motor"] = 1

                global_val.write_val(dic)

            elif GPIO.input(INPUT_PINS["REMOTE_B"]) and not prev_status["REMOTE_B"]:
                # Bボタン -> スクリーン停止
                dic = global_val.read_val()
                dic["motor"] = 0
                global_val.write_val(dic)

            elif GPIO.input(INPUT_PINS["REMOTE_C"]) and not prev_status["REMOTE_C"]:
                # Cボタン -> プロジェクター電源
                pass

            elif GPIO.input(INPUT_PINS["REMOTE_D"]) and not prev_status["REMOTE_D"]:
                # Dボタン -> LEDライト電源
                dic = global_val.read_val()
                if dic["led"] == 1:
                    dic["led"] = 0
                else:
                    dic["led"] = 1
                global_val.write_val(dic)

            for i in input_pin_names:
                prev_status[i] = GPIO.input(INPUT_PINS[i])

            sleep(0.02)

    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()