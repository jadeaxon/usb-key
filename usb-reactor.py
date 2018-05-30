# Detects whether a particular USB drive is connected and reacts to that connection.
# I'm pretending all removable drives are USB drives.

# PRE: Install Python 3.6.5 or later in Windows 10 (both 64-bit).
# PRE: Add %USERPROFILE%\AppData\Local\Programs\Python\Python36 to your PATH env var.
# PRE: Add %USERPROFILE%\AppData\Local\Programs\Python\Python36\Scripts to your PATH env var.
# PRE: pip install pypiwin32 # For win32file.
# PRE: pip install pyautogui # For AHK-like automation in Windows.
# PRE: pip install pywinauto # Also for AHK-like automation in Windows.
# PRE: You're running this from Windows (PowerShell) as with admin rights, not Cygwin.
# PRE: Cisco AnyConnect VPN client GUI is not started at boot.
# It starts late and interferes with the LastPass login.

import win32file
import win32gui
import time
import copy
import os
import pyautogui
bot = pyautogui
import pywinauto
from tkinter import Tk
from sys import stdout
from sys import argv

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Turns raw bytes into characters you can safely store in a text file.
# Necessary since I want to read the encrypted message back from a non-binary file.
import base64

import ctypes # To implement get_all_window_titles().


#==============================================================================
# Globals
#==============================================================================

# Process command-line args.
S = 'unknown'
arg1 = 'unknown'
try:
    S, arg1 = argv
except ValueError:
    S = argv[0]
    arg1 = '' # Not boottime.
S = os.path.basename(S)

# Check the environment.
user = os.environ['USERNAME'];
home = os.environ['USERPROFILE'];

local_keyfile_path = f'{home}\\.ssh\\jadeaxon.usb.key'

usb_keyfile_path = ""
usb_key = []

firefox_window_title = ""


#==============================================================================
# Functions
#==============================================================================

# PRE: Install Visual Studio 2017 Build Tools (?)--might only apply to pycrypto (which failed).
# PRE: pip install pycryptodome
# Using pycryptodome instead of pycrypto because pycrypto failed to install.
# PRE: You've used ssh-keygen to create an public/private RSA key pair.
# PRE: The key pair is not passphrase-protected.
# PRE: The line was encrypted using the public key.
def read_encrypted_line(path, n):
    """ Reads encrypted line n from the given key file. """
    global home

    private_key_path = f'{home}\\.ssh\\usb_key_rsa'
    private_key_file = open(private_key_path)
    private_key = private_key_file.read()
    private_key_object = RSA.importKey(private_key)

    encrypted_file = open(path)
    encrypted_lines = encrypted_file.readlines()
    encoded_encrypted_line_from_file_utf8 = encrypted_lines[n].rstrip()
    encrypted_line_from_file_base64 = encoded_encrypted_line_from_file_utf8.encode("utf-8") # UTF8 -> base 64 bytes.
    encrypted_line_from_file = base64.b64decode(encrypted_line_from_file_base64) # base64 bytes -> bytes.

    decryption_cipher = PKCS1_OAEP.new(private_key_object)
    decrypted_line_from_file = decryption_cipher.decrypt(encrypted_line_from_file) # bytes -> bytes.
    decoded_decrypted_line_from_file = decrypted_line_from_file.decode("utf-8") # bytes -> UTF8.

    return decoded_decrypted_line_from_file


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
    global usb_key, user, home, local_keyfile_path, usb_keyfile_path
    global lastpass_password

    print(f"{S}: Drive {drive} was connected.")
    if not os.path.exists(local_keyfile_path):
        print(f"{S}: ERROR: Local key file DNE.")
        return

    usb_keyfile_path = f'{drive}jadeaxon.usb.key'
    if not os.path.exists(usb_keyfile_path):
        print(f"{S}: ERROR: USB key file DNE.")
        return

    local_keyfile = open(local_keyfile_path)
    local_key = local_keyfile.readlines()

    usb_keyfile = open(usb_keyfile_path)
    usb_key = usb_keyfile.readlines()

    if local_key[0] != usb_key[0]:
        print(f"{S}: ERROR: Keys do not match.")
        return

    launch_KeePass()
    launch_LastPass()
    launch_Cygwin()

    # Sometimes the LastPass login fails.  Let's retry it if so.
    if not window_exists('My LastPass Vault - Mozilla Firefox'):
        print(f"{S}: Retrying LastPass login.  First attempt failed.")
        launch_LastPass()

    lastpass_password = ""


def launch_KeePass():
    global home, usb_keyfile_path, lastpass_password

    password = read_encrypted_line(usb_keyfile_path, 1)

    # Launch KeePass and get my LastPass password from it.
    # TO DO: Detect if KeePass was already running.
    # This just activates KeePass if it is already launched.
    time.sleep(2)
    os.startfile(f'{home}\\Dropbox\\KeePass Database.kdbx')
    time.sleep(2)
    bot.typewrite(password)
    bot.press('enter')
    time.sleep(1)
    bot.typewrite('LastPass')
    bot.press('enter')
    time.sleep(1)
    bot.hotkey('ctrl', 'c')
    time.sleep(1)
    lastpass_password = read_clipboard()


# PRE: launch_KeePass() was successful so that you have the LastPass password saved.
def launch_LastPass():
    global lastpass_password, firefox_window_title

    # Launch Firefox and enter the LastPass password.
    if not firefox_is_running():
        os.startfile('C:\\Program Files\\Mozilla Firefox\\firefox.exe')
        time.sleep(5)
    else:
        # Activate the existing Firefox window.
        activate_firefox_window()
        time.sleep(1)
        # FAIL: This technique is not reliable.  May be Programmer Dvorak interacting badly with the bot.
        # bot.hotkey('win', 't')
        # bot.press(firefox_window_title[0])
        # bot.press('enter')

    bot.hotkey('ctrl', 'l') # Address bar.
    time.sleep(1)
    bot.typewrite('https://lastpass.com/?ac=1&lpnorefresh=1')
    bot.press('enter')
    time.sleep(15)

    # Yes indeed!  Having Programmer Dvorak keyboard layout changes what pyautogui
    # types into the LastPass login.  Specifically, the @ becomes a ^.  So, I have
    # to put my e-mail address on the clipboard and paste it instead.
    save_to_clipboard('jadeaxon@hotmail.com')

    bot.hotkey('ctrl', 'v')
    bot.press('tab')
    bot.typewrite(lastpass_password)
    bot.press('enter')
    # BAM!


# PRE: mintty.exe (the Cygwin terminal) must not be running as admin.
# CON: You cannot automate keystokes in the UAC dialog.
# CON: You cannot automate keystrokes to Cygwin (if it is running as admin).
# CON: pyautogui mouse automation doesn't work in Cygwin (if it is running as admin)!
def launch_Cygwin():
    global usb_keyfile_path

    password1 = read_encrypted_line(usb_keyfile_path, 2)
    password2 = read_encrypted_line(usb_keyfile_path, 3)

    os.startfile('C:\\Users\\Public\\Desktop\\Cygwin64 Terminal.lnk')
    time.sleep(15)
    bot.typewrite(password1)
    bot.press('enter')
    bot.typewrite(password2)
    bot.press('enter')


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
    print(f"{S}: Drive {drive} was disconnected.")


def get_all_window_titles():
    """ Returns a list of all window titles. """
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    titles = []
    def foreach_window(hwnd, lParam):
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            titles.append(buff.value)
        return True
    EnumWindows(EnumWindowsProc(foreach_window), 0)

    return titles


def window_exists(title):
    titles = get_all_window_titles()
    if title in titles:
        return True
    return False


def firefox_is_running():
    global firefox_window_title
    titles = get_all_window_titles()
    for title in titles:
        if title.endswith('- Mozilla Firefox'):
            firefox_window_title = title
            return True
    return False


def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def activate_firefox_window():
    # FAIL:
    # app = pywinauto.application.Application()
    # t, c = firefox_window_title, 'MozillaWindowClass'
    # print(t)
    # print(c)
    # # handle = pywinauto.findwindows.find_windows(title=t, class_name=c)[0]
    # handle = pywinauto.findwindows.find_windows(title=t)[0]
    # app.connect(title=t)
    # window = app.window_(handle=handle)
    # window.SetFocus()

    windows = [] # Top-level windows.
    win32gui.EnumWindows(windowEnumerationHandler, windows)
    # Each window is a (handle, title) tuple.
    for window in windows:
        if "firefox" in window[1].lower():
            ## print(window)
            win32gui.ShowWindow(window[0], 5)
            win32gui.SetForegroundWindow(window[0])
            break


#==============================================================================
# Tests
#==============================================================================

def test__read_encrypted_line():
    kfpath = 'E:\\jadeaxon.usb.key'
    if not os.path.exists(kfpath):
        kfpath = 'D:\\jadeaxon.usb.key'
    password1 = read_encrypted_line(kfpath, 1)
    print(password1)
    password2 = read_encrypted_line(kfpath, 2)
    print(password2)
    password3 = read_encrypted_line(kfpath, 3)
    print(password3)


def test__get_all_window_titles():
    titles = get_all_window_titles()
    search = 'My LastPass Vault - Mozilla Firefox'
    print(titles)


def test__window_exists():
    title = 'My LastPass Vault - Mozilla Firefox'
    exists = window_exists(title)
    print(exists)

    title = 'This window does not exist'
    exists = window_exists(title)
    print(exists)


def test__firefox_is_running():
    running = firefox_is_running()
    print(running)


def test__activate_firefox_window():
    activate_firefox_window()


#==============================================================================
# Main
#==============================================================================

if arg1 == '--test':
    test__read_encrypted_line()
    test__get_all_window_titles()
    test__window_exists()
    test__firefox_is_running()
    test__activate_firefox_window()
    exit(0)

pid = os.getpid()
print(f'{S}: Engaged!')
print(f'{S}: PID = {pid}.')
# This gets passed in by the .bat wrapper that is used for start-at-boot.
if arg1 == 'boot':
    print(f'{S}: Waiting a moment for system boot to gel.')
    time.sleep(15) # Let stuff gel at boot time.

# To kill in Windows:
# taskkill /F /PID <pid>

# Previous and current connection states of all removable drives.
previous = {}
current = {}

while True:
    current.clear();
    removable_drives = get_removable_drives();
    for drive in removable_drives:
        current[drive] = 1; # Connected.

    for drive, state in list(previous.items()):
        if drive not in current:
            react_to_drive_disconnection(drive)

    for drive, state in list(current.items()):
        if drive not in previous:
            react_to_drive_connection(drive)

    previous = copy.deepcopy(current);
    stdout.flush();
    time.sleep(3)


