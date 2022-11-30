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

    global_val = mg.mmap_global_val("global_val.txt")
    dic = {"ir":[0, 0, 0, 0], "radio":[0, 0, 0, 0], "led":0, "motor":0}
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
                for i in range(25):
                    if not ir.fetching_code:
                        break
                    sleep(0.02)

                for key, val in key_config.items():
                    if ir.compare(val, ir.code[:]):
                        key_name = key

                dic = global_val.read_val()

                if key_name == "firetv:power":
                    # print("press power")
                    dic["ir"] = [1, 0, 0, 0]
                elif key_name == "firetv:volume_up":
                    # print("press volume_up")
                    dic["ir"] = [0, 1, 0, 0]
                elif key_name == "firetv:volume_down":
                    # print("press volume_down")
                    dic["ir"] = [0, 0, 1, 0]
                elif key_name == "firetv:volume_mute":
                    # print("press volume_mute")
                    dic["ir"] = [0, 0, 0, 1]
                else:
                    dic["ir"] = [0, 0, 0, 0]

                global_val.write_val(dic)

    except KeyboardInterrupt:
        ir.pi.stop()

if __name__ == "__main__":
    main()
