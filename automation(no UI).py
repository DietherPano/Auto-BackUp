import os
import shutil
import time
import win32api
import win32file
from datetime import datetime

"""
How to use:
    1.Install the requirement.txt pip install -r requirement.txt
    2.Change the back_up_usb_name to your USB name.
    3.Change the src_dir, you want to back up.
    4.Plug the USB and Run.
Remember:
    if the you don't know what is the label or 
    name of your USB then go to the test.py and run the program,
    it will show you the Drive and Label of your USB
"""

def create_time_stamps():
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def create_if_not_exist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def print_action(action, src_path, dest_path):
    message = f"[{action}] {src_path} to {dest_path}"
    print(message)

def log_action(action, src_path, dest_path):
    timestamp = create_time_stamps()
    message = f"[{timestamp}] [{action}] {src_path} to {dest_path}"
    print_action(action, src_path, dest_path)
    with open('backup_log.txt', 'a') as log_file:
        log_file.write(message + '\n')

def backup_files(src_path, dest_dir):
    backup_dir = os.path.join(dest_dir, 'Backup')
    create_if_not_exist(backup_dir)

    timestamp = create_time_stamps()
    src_name = os.path.basename(src_path)
    backup_name = f"{src_name}_Backup_{timestamp}"

    backup_path = os.path.join(backup_dir, backup_name)
    create_if_not_exist(backup_path)

    for folder in os.listdir(src_path):
        source_path = os.path.join(src_path, folder)
        destination_path = os.path.join(backup_path, folder)

        if os.path.isdir(source_path):
            if not os.path.exists(destination_path):
                shutil.copytree(source_path, destination_path)
                log_action('Copied', source_path, destination_path)
            else:
                print_action('Skipped', source_path, destination_path)
        else:
            if not os.path.exists(destination_path):
                shutil.copy2(source_path, destination_path)
                log_action('Copied', source_path, destination_path)
            else:
                print_action('Skipped', source_path, destination_path)

    log_action('Backup Completed', src_path, backup_path)

def find_usb_name(usb_name):
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]

    for drive in drives:
        drive_type = win32file.GetDriveType(drive)
        if drive_type == win32file.DRIVE_REMOVABLE:
            try:
                volume_label = win32api.GetVolumeInformation(drive)[0]
                if volume_label == usb_name:
                    return drive
            except Exception as e:
                print(f'Could not retrieve label for drive {drive}: {e}')
    return None

def main(src_dir, usb_name):
    while True:
        usb_mount = find_usb_name(usb_name)

        if usb_mount:
            print(f'BackUp USB ({usb_name}) detected at {usb_mount}')
            backup_files(src_dir, usb_mount)
            break
        else:
            print(f'{usb_name} not detected. Checking again in 15 seconds.')
            time.sleep(15)

if _name_ == '_main_':
    src_dir = 'C:/Users/panos/OneDrive/Desktop/New folder (2)'
    backup_usb_name = "2GIG ONLY"
    main(src_dir, backup_usb_name)
