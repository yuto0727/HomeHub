import irrp
from time import sleep
import pigpio, json
import mmap_global_val as mg
import subprocess

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

CMD_PROJECTOR = "python3 /home/yuto/HomeHub/irrp.py -p -g17 -f /home/yuto/HomeHub/codes_for_devices projector"
CMD_light_ON = "python3 /home/yuto/HomeHub/irrp.py -p -g17 -f /home/yuto/HomeHub/codes_for_devices light:on"
CMD_light_OFF = "python3 /home/yuto/HomeHub/irrp.py -p -g17 -f /home/yuto/HomeHub/codes_for_devices light:off"


def main():
    irrp.pi = pigpio.pi()
    irrp.last_tick = 0
    irrp.in_code = False
    irrp.code = []
    irrp.fetching_code = False

    if not irrp.pi.connected:
        exit(0)

    # ファイル間通信初期化
    global_val = mg.mmap_global_val("/home/yuto/HomeHub/global_val.txt")

    # motor     -> 0:停止  1:出す 2:しまう
    # screen_st -> 0: 中間 1:出切 2:巻切
    dic = {"led":0, "motor":0, "screen_st":2}
    global_val.write_val(dic)

    try:
        with open('codes_for_control') as f:
            key_config = json.load(f)
            irrp.pi.set_mode(irrp.GPIO, pigpio.INPUT)
            irrp.pi.set_glitch_filter(irrp.GPIO, irrp.GLITCH)

            cb = irrp.pi.callback(irrp.GPIO, pigpio.EITHER_EDGE, irrp.cbf)

            print("reading...")
            while True:
                irrp.code = []
                irrp.fetching_code = True
                i = 0
                while irrp.fetching_code:
                    sleep(0.02)

                key_name = ""
                for key, val in key_config.items():
                    if irrp.compare(val, irrp.code[:]):
                        key_name = key

                if key_name == "firetv:power":
                    # print("press power")
                    # powerボタン -> スクリーンアップ・ダウン
                    dic = global_val.read_val()

                    if dic["screen_st"] == 0:
                        # 中間
                        if dic["motor"] == 0 or dic["motor"] == 1:
                            # 中間で停止状態または中間で展開中 -> 収納
                            dic["motor"] = 2
                        elif dic["motor"] == 2:
                            # 中間で収納中 -> 展開
                            dic["motor"] = 1
                        global_val.write_val(dic)

                    elif dic["screen_st"] == 1:
                        # 出切 -> 収納

                        # モーター回転、間接照明消灯
                        dic["motor"] = 2
                        dic["led"] = 0
                        global_val.write_val(dic)

                        # プロジェクターOFF
                        subprocess.run(CMD_PROJECTOR.split())
                        sleep(1)
                        subprocess.run(CMD_PROJECTOR.split())

                        # シーリングライト点灯
                        subprocess.run(CMD_light_ON.split())

                    elif dic["screen_st"] == 2:
                        # 巻切 -> 展開

                        # モーター回転
                        dic["motor"] = 1
                        global_val.write_val(dic)

                        # シーリングライト消灯
                        subprocess.Popen(CMD_light_ON.split())
                        sleep(0.08)
                        subprocess.run(CMD_light_OFF.split())

                        sleep(1)

                        # 間接照明点灯
                        dic["led"] = 1
                        global_val.write_val(dic)

                        # プロジェクターON
                        subprocess.run(CMD_PROJECTOR.split())


                elif key_name == "firetv:volume_up":
                    # print("press volume_up")
                    pass
                elif key_name == "firetv:volume_down":
                    # print("press volume_down")
                    pass
                elif key_name == "firetv:volume_mute":
                    # print("press volume_mute")
                    pass
                else:
                    pass

    except KeyboardInterrupt:
        irrp.pi.stop()

if __name__ == "__main__":
    main()
