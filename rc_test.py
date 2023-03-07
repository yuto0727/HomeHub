from time import sleep
from threading import Thread
import RPi.GPIO as GPIO
import sys, spidev, subprocess, pigpio, json, os, logging

PATH = os.path.dirname(__file__)
print(f"path: {PATH}")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s:%(name)s - %(message)s", filename=f"{PATH}/logs/test.log")
logging.info("script start")

# 外部スクリプトimport
try:
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
    logging.info("irrp init ok")

except Exception as e:
    logging.warning(str(e))