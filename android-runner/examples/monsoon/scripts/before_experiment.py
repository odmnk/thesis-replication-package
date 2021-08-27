# noinspection PyUnusedLocal
import time
def main(device, *args, **kwargs):
    # Clean the android browser.
    print("Before Experiment: clear the browser")
    device.shell("pm clear com.android.chrome")
    time.sleep(5)
    # Sleep for 60 seconds so device is 
    print("Sleep for 60 seconds")
    time.sleep(60)
