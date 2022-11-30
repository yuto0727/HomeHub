import irrp as ir
from time import sleep
import pigpio, json
import mmap_global_val as mg

ir.GPIO = 18

ir.GLITCH = 100
ir.PRE_MS = 200
ir.POST_MS = 15
ir.VERBOSE = False
ir.SHORT = 10
ir.TOLERANCE = 15

ir.POST_US = ir.POST_MS * 1000
ir.PRE_US = ir.PRE_MS * 1000
ir.TOLER_MIN = (100 - ir.TOLERANCE) / 100.0
ir.TOLER_MAX = (100 + ir.TOLERANCE) / 100.0


def main():
    ir.pi = pigpio.pi()
    ir.last_tick = 0
    ir.in_code = False
    ir.code = []
    ir.fetching_code = False

    if not ir.pi.connected:
        exit(0)

    # ファイル間通信初期化
    global_val = mg.mmap_global_val("global_val.txt")

    # motor     -> 0:停止  1:出す 2:しまう
    # screen_st -> 0: 中間 1:出切 2:巻切
    dic = {"led":0, "motor":0, "screen_st":0}
    global_val.write_val(dic)

    try:
        with open('codes_for_control') as f:
            key_config = json.load(f)
            ir.pi.set_mode(ir.GPIO, pigpio.INPUT)
            ir.pi.set_glitch_filter(ir.GPIO, ir.GLITCH)

            cb = ir.pi.callback(ir.GPIO, pigpio.EITHER_EDGE, ir.cbf)

            print("reading...")
            while True:
                ir.code = []
                ir.fetching_code = True
                i = 0
                while ir.fetching_code:
                    sleep(0.02)

                key_name = ""
                for key, val in key_config.items():
                    if ir.compare(val, ir.code[:]):
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

                    elif dic["screen_st"] == 1:
                        # 出切 -> 収納
                        dic["motor"] = 2

                    elif dic["screen_st"] == 2:
                        # 巻切 -> 展開
                        dic["motor"] = 1

                    global_val.write_val(dic)

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
        ir.pi.stop()

if __name__ == "__main__":
    main()
