# noinspection PyUnusedLocal
import subprocess
import time
def main(device, *args, **kwargs):
    print("sleep")
    subprocess.call("adb shell input keyevent KEYCODE_SLEEP", shell=True)
    print("wakeup")
    subprocess.call("adb shell input keyevent KEYCODE_WAKEUP", shell=True)
    print("swipe")
    subprocess.call("adb shell input touchscreen swipe 530 1420 530 0", shell=True)
    time.sleep(2)
    print("swipe second time")
    subprocess.call("adb shell input touchscreen swipe 530 1420 530 0", shell=True)
    time.sleep(2)
    print("Input code")
    subprocess.call("adb shell input text 0000", shell=True)

    print("Press okay")
    subprocess.call("adb shell input keyevent 66", shell=True)

    time.sleep(2)
