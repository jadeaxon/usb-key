# Detects whether a particular USB drive is connected and reacts to that connection.
# I'm pretending all removable drives are USB drives.

# PRE: Install Python 3.6.5 or later in Windows 10 (both 64-bit).
# PRE: Add %USERPROFILE%\AppData\Local\Programs\Python\Python36 to your PATH env var.
# PRE: Add %USERPROFILE%\AppData\Local\Programs\Python\Python36\Scripts to your PATH env var.
# PRE: pip install pypiwin32 # For win32file.
# PRE: pip install pyautogui # For AHK-like automation in Windows.
# PRE: You're running this from Windows (PowerShell) as with admin rights, not Cygwin.

import win32file
import time
import copy
import os
import pyautogui
bot = pyautogui
from tkinter import Tk
from sys import stdout


#==============================================================================
# Globals
#==============================================================================

user = os.environ['USERNAME'];
home = os.environ['USERPROFILE'];

local_keyfile_path = f'{home}\\.ssh\\jadeaxon.usb.key'

usb_key = []


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
    global usb_key, user, home, local_keyfile_path

    print(f"usb-reactor: Drive {drive} was connected.")
    if not os.path.exists(local_keyfile_path):
        print("usb-reactor: ERROR: Local key file DNE.")
        return

    usb_keyfile_path = f'{drive}jadeaxon.usb.key'
    if not os.path.exists(usb_keyfile_path):
        print("usb-reactor: ERROR: USB key file DNE.")
        return

    local_keyfile = open(local_keyfile_path)
    local_key = local_keyfile.readlines()

    usb_keyfile = open(usb_keyfile_path)
    usb_key = usb_keyfile.readlines()

    if local_key[0] != usb_key[0]:
        print("usb-reactor: ERROR: Keys do not match.")
        return

    launch_KeePass()
    launch_LastPass()
    ## launch_Cygwin()


def launch_KeePass():
    global usb_key, user, home, local_keyfile_path

    password = usb_key[1].rstrip()

    # Launch KeePass and get my LastPass password from it.
    # TO DO: Detect if KeePass was already running.
    # This just activates KeePass if it is already launched.
    time.sleep(2)
    os.startfile(f'C:\\Users\\{user}\\Dropbox\\KeePass Database.kdbx')
    time.sleep(2)
    bot.typewrite(password)
    bot.press('enter')
    time.sleep(1)
    bot.typewrite('LastPass')
    bot.press('enter')
    time.sleep(1)
    bot.hotkey('ctrl', 'c')


# PRE: launch_KeePass() was successful so that you have the LastPass password in clipboard.
def launch_LastPass():
    # Launch Firefox and enter the LastPass password.
    os.startfile('C:\\Program Files\\Mozilla Firefox\\firefox.exe')
    time.sleep(5)
    bot.hotkey('ctrl', 'l') # Address bar.
    bot.typewrite('https://lastpass.com/?ac=1&lpnorefresh=1')
    ## bot.typewrite('https://lastpass.com/?&ac=1&fromwebsite=1&newvault=1&nk=1')
    bot.press('enter')
    time.sleep(10)

    # Yes indeed!  Having Programmer Dvorak keyboard layout changes what pyautogui
    # types into the LastPass login.  Specifically, the @ becomes a ^.  So, I have
    # to put my e-mail address on the clipboard and paste it instead.
    password = read_clipboard()
    save_to_clipboard('jadeaxon@hotmail.com')

    bot.hotkey('ctrl', 'v')
    bot.press('tab')
    bot.typewrite(password)
    bot.press('enter')
    # BAM!


# CON: You cannot automate keystokes in the UAC dialog.
# CON: You cannot automate keystrokes to Cygwin.
# CON: pyautogui mouse automation doesn't work in Cygwin!
def launch_Cygwin():
    global usb_key, user, home, local_keyfile_path

    password1 = usb_key[2].rtrim()
    password2 = usb_key[3].rtrim()

    print(f"usb-reactor: password1 = {password1}.")
    print(f"usb-reactor: password2 = {password2}.")

    os.startfile('C:\\Users\\Public\\Desktop\\Cygwin64 Terminal.lnk')
    time.sleep(10)
    # PROBLEM: It's a pain to disable UAC for one app.  You can't automate keystrokes in that window.
    save_to_clipboard(password1)
    time.sleep(1)
    print(f"usb-reactor: Moving mouse.")
    bot.moveTo(300, 300)
    bot.rightClick()


def save_to_clipboard(s):
    tk = Tk()
    tk.withdraw()
    tk.clipboard_clear()
    tk.clipboard_append(s)
    tk.update()
    tk.destroy()


def read_clipboard():
    tk = Tk()
    tk.withdraw()
    contents = tk.clipboard_get()
    tk.destroy()
    return contents


def react_to_drive_disconnection(drive):
    print(f"usb-reactor: Drive {drive} was disconnected.")


#==============================================================================
# Main
#==============================================================================

pid = os.getpid()
print('usb-reactor: Engaged!')
print(f'usb-reactor: PID = {pid}.')
# To kill in Windows:
# taskkill /F /PID <pid>

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
            react_to_drive_disconnection(drive)

    for drive, state in list(current.items()):
        if drive not in previous:
            react_to_drive_connection(drive)

    previous = copy.deepcopy(current);
    stdout.flush();
    time.sleep(3) # Two seconds.



