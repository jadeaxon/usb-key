pid = -1

import time

print("Monitoring usb-reactor.")
while True:
    time.sleep(5)
    try:
        with open('usb-reactor.pid') as f:
            pid = f.read().strip()
    except:
        print('WARNING: Failed to read usb-reactor.pid.')
        pid = -1

    print(f'usb-reactor PID = {pid}')
    if pid == -1: continue



