# Monitors whether the usb-reactor process is running.
# If not, restarts it.

# From Windows Powershell:
# PRE: pip3 install wmi

import time
import os
import sys
import subprocess

pid = -1

host = os.environ['HOSTNAME']

time.sleep(5) # Give usb-reactor a chance to start at boot.

def is_running(pid):
    # tasklist /FI "PID eq <pid>"
    # If first line starts with INFO:, then not found.
    command = f'tasklist /FI "PID eq {pid}"'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, error) = p.communicate() # Returns byte sequence.
    output = output.decode("utf-8") # Convert to string.
    p_status = p.wait() # Wait for process to finish.
    if output.startswith("INFO: "):
        return False
    else:
        return True


print("Monitoring usb-reactor.")
while True:
    sys.stdout.flush()
    time.sleep(5)
    try:
        with open(f'usb-reactor.{host}.pid') as f:
            pid = int(f.read().strip())
    except:
        print(f'WARNING: Failed to read usb-reactor.{host}.pid.')
        pid = -1

    if pid == -1: continue

    if is_running(pid):
        print(f"Process {pid} is running.")
    else:
        print(f"Process {pid} is NOT running.  Restarting process.")
        os.system("usb-reactor-restart.bat")




