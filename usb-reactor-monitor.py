# Monitors whether the usb-reactor process is running.
# If not, restarts it.

pid = -1

import time
import os

def is_running(pid):
    """ Check if given process is running. """
    try:
        # Signal 0 just asks if the process is running.
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

print("Monitoring usb-reactor.")
while True:
    time.sleep(5)
    try:
        with open('usb-reactor.pid') as f:
            pid = int(f.read().strip())
    except:
        print('WARNING: Failed to read usb-reactor.pid.')
        pid = -1

    print(f'usb-reactor PID = {pid}')
    if pid == -1: continue

    if is_running(pid):
        print(f"Process {pid} is running.")
    else:
        print(f"Process {pid} is NOT running.")





