# noinspection PyUnusedLocal
import time
from AndroidRunner.Device import Device

def tap(device: Device, x: int, y: int, sleep = 4) -> None:
    device.shell('input tap %s %s' % (x, y))
    # We need to wait for the display to update after the last click.
    # The time to update is vary.
    time.sleep(sleep)

def main(device, *args, **kwargs):
    print("Chrome TOS") 
    # Do not send data
    tap(device, 115, 1277)

    # Accept TOS
    tap(device, 510, 1960)

    # "No thanks" do not turn on sync.
    tap(device, 236, 1987)

