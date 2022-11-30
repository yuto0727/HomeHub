import irrp as ir

ir.GPIO = 18

ir.GLITCH = 100
ir.PRE_MS = 200
ir.POST_MS = 15
ir.VERBOSE = False
ir.SHORT = 10
ir.TOLERANCE = 15

ir.POST_US = POST_MS * 1000
ir.PRE_US = PRE_MS * 1000
ir.TOLER_MIN = (100 - TOLERANCE) / 100.0
ir.TOLER_MAX = (100 + TOLERANCE) / 100.0


def main():
    pi = pigpio.pi()

    if not pi.connected:
        exit(0)

    with open('codes_for_control') as f:
        key_config = json.load(f)
        pi.set_mode(ir.GPIO, pigpio.INPUT)
        pi.set_glitch_filter(ir.GPIO, ir.GLITCH)

        cb = pi.callback(ir.GPIO, pigpio.EITHER_EDGE, ir.cbf)

        try:
            while True:
                ir.code = []
                ir.fetching_code = True
                while ir.fetching_code:
                    time.sleep(0.1)

                time.sleep(0.5)

                for key, val in key_config.items():
                    if ir.compare(val, ir.code[:]):
                        key_name = key

                if key_name == "power":
                    print("press power")
                elif key_name == "volume_up":
                    print("press volume_up")
                elif key_name == "volume_down":
                    print("press volume_down")
                elif key_name == "volume_mute":
                    print("press volume_mute")
                else:
                    pass

        except KeyboardInterrupt:
            pass
        finally:
            pi.stop()