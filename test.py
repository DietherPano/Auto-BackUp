import win32api
import win32file

#Test to see the label and the drive
drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]

for drive in drives:
    drive_type = win32file.GetDriveType(drive)
    if drive_type == win32file.DRIVE_REMOVABLE:
        volume_label = win32api.GetVolumeInformation(drive)[0]
        print(f'Drive: {drive} - Label: {volume_label}')
    else:
        print('No USB Drive Inserted!!!')