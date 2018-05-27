# Detects whether a particular USB drive is connected and reacts to that connection.
# I'm pretending all removable drives are USB drives.

# PRE: Install Python 3.6.5 or later in Windows 10 (both 64-bit).
# PRE: Add %USERPROFILE%\AppData\Local\Programs\Python\Python36 to your PATH env var.
# PRE: Add %USERPROFILE%\AppData\Local\Programs\Python\Python36\Scripts to your PATH env var.
# PRE: pip install pypiwin32
# PRE: You're running this from Windows (PowerShell) as with admin rights, not Cygwin.

import win32file
import time
import copy


#==============================================================================
# Functions
#==============================================================================

def get_removable_drives():
    """ Returns a list of all connected removable drives. """
    removable_drives = []
    drivebits = win32file.GetLogicalDrives()
    for drive_number in range(1, 26):
        mask = 1 << drive_number
        if drivebits & mask:
            drive_name = '%c:\\' % chr(ord('A') + drive_number) # E.g., C:\
            drive_type = win32file.GetDriveType(drive_name)
            if drive_type == win32file.DRIVE_REMOVABLE:
                removable_drives.append(drive_name)
    return removable_drives


def react_to_drive_connection(drive):
    print(f"usb-reactor: Drive {drive} was disconnected.");


def react_to_drive_disconnection(drive):
    print(f"usb-reactor: Drive {drive} was connected.");


#==============================================================================
# Main
#==============================================================================

print('usb-reactor: Engaged!');

# Previous and current connection states of all removable drives.
previous = {}
current = {}

while True:
    ## print('usb-reactor: Scanning for removable drives.')
    current.clear();
    removable_drives = get_removable_drives();
    for drive in removable_drives:
        ## print(drive)
        current[drive] = 1; # Connected.

    ## print(previous);
    ## print(current);

    for drive, state in list(previous.items()):
        if drive not in current:
            react_to_drive_connection(drive);

    for drive, state in list(current.items()):
        if drive not in previous:
            react_to_drive_disconnection(drive);

    previous = copy.deepcopy(current);
    time.sleep(2) # Two seconds.



