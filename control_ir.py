import irrp as ir
from time import sleep
import pigpio, json
import global_val as g

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

    with open('codes_for_control') as f:
        key_config = json.load(f)
        ir.pi.set_mode(ir.GPIO, pigpio.INPUT)
        ir.pi.set_glitch_filter(ir.GPIO, ir.GLITCH)

        cb = ir.pi.callback(ir.GPIO, pigpio.EITHER_EDGE, ir.cbf)

        try:
            print("reading...")
            while True:
                ir.code = []
                ir.fetching_code = True
                while ir.fetching_code:
                    sleep(0.02)

                sleep(0.5)

                for key, val in key_config.items():
                    if ir.compare(val, ir.code[:]):
                        key_name = key

                if key_name == "firetv:power":
                    print("press power")
                    g.data_ir[0] = 1
                elif key_name == "firetv:volume_up":
                    print("press volume_up")
                    g.data_ir[1] = 1
                elif key_name == "firetv:volume_down":
                    print("press volume_down")
                    g.data_ir[2] = 1
                elif key_name == "firetv:volume_mute":
                    print("press volume_mute")
                    g.data_ir[3] = 1
                else:
                    pass

        except KeyboardInterrupt:
            pass
        finally:
            ir.pi.stop()

if __name__ == "__main__":
    main()
