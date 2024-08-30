import os
import shutil
import time
import win32api
import win32file
from datetime import datetime
import tkinter as tk
import threading
import json
from tkinter import messagebox,filedialog,scrolledtext

class LabelEntryGenerator:
	def __init__(self):
		self.label = []
		self.entry = []
	def add_label(self, frame,label_text,font_style,font_size,bg_color,side):
		label = tk.Label(frame,text=label_text ,font=(font_style,font_size),bg=bg_color)
		label.pack(side=side)
		self.label.append(label)
		return label
    
	def add_label_with_grid(self, frame,label_text,font_style,font_size,bg_color,image,row,column,padx,pady):
		label = tk.Label(frame,text=label_text ,font=(font_style,font_size),bg=bg_color,anchor='center',image=image)
		label.grid(row=row,column=column,padx=padx,pady=pady,sticky=tk.W)
		self.label.append(label)
		return label
		
	def add_entry(self,frame,side,anchor,padx,show):
		entry = tk.Entry(frame,show=show,width=15,font=("Arial 15"))
		entry.pack(side=side,anchor=anchor,padx=padx)
		self.entry.append(entry)
		return entry
	def add_entry_with_grid(self,frame,row,column,padx,pady,show):
		entry = tk.Entry(frame,show=show,width=50,font=("Arial 15"))
		entry.grid(row=row,column=column,padx=padx,pady=pady,sticky=tk.W)
		self.entry.append(entry)
		return entry
		
	def destroy_label_entry(self):
		for label in self.label:
			label.pack_forget()
		for entry in self.entry:
			entry.pack_forget()


class autoBackUp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.__configure_window()
        self.__directory = {}
        self.__usb_name = {}
        self.__button = {}
        self.__settings_btn = {}
        self.__backup_thread = None
        self.__is_running = False
        self.__backupusb = "2GIG ONLY"
        self.__data = self.load_data()
        self.__label_entry = LabelEntryGenerator()
        self.directory_frame = tk.Frame(self,bg='#AFDDE5')
        self.settings_frame = tk.Frame(self,bg='#AFDDE5')
        self.help_frame = tk.Frame(self,bg='#AFDDE5')
        self.change_backup_usb_frame = tk.Frame(self,bg='#AFDDE5')
        self.log_area = None

    def main(self):
        self.settings_frame.grid_forget()
        self.directory_frame.grid(row=0,column=1)
        
        directory_label = self.__label_entry.add_label_with_grid(self.directory_frame,"Select Directory:", "Open Sans Condensed", 15,'#AFDDE5',None,0,0,10,5)
        self.__directory['Directory'] = self.__label_entry.add_entry_with_grid(self.directory_frame,0,1,10,5,'')
        self.__button['Browse'] = tk.Button(self.directory_frame,text='Browse',command=self.browse_directory,font=("Times New Roman", 15),height=1,width=10,bg='#AFDDE5')
        self.__button['Browse'].grid(row=0,column=2,padx=10,pady=5)
        usb_label = self.__label_entry.add_label_with_grid(self.directory_frame,"USB BackUp Name:", "Open Sans Condensed", 15,'#AFDDE5',None,1,0,10,5)
        usb_name_label = self.__label_entry.add_label_with_grid(self.directory_frame,f"{self.__data['usb_backup']}", "Open Sans Condensed", 15,'#AFDDE5',None,1,1,10,5)
        
        self.log_area = scrolledtext.ScrolledText(self.directory_frame,font=("Times New Roman", 15),height=10,width=90,state=tk.DISABLED)
        self.log_area.grid(row=3,column=0,padx=10,pady=5)
        self.log_area.grid_configure(columnspan=3)

        self.__button['Settings_btn'] = tk.Button(self.directory_frame,text='Settings',command=self.settings,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Settings_btn'].grid(row=2,column=0,padx=10,pady=5)

        self.__button['Start_btn'] = tk.Button(self.directory_frame,text='Start',command=self.start_backup,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Start_btn'].grid(row=2,column=1,padx=10,pady=5)

        self.__button['Stop_btn'] = tk.Button(self.directory_frame,text='Stop',command=self.stop_backup,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Stop_btn'].grid(row=2,column=2,padx=10,pady=5)
    
    def create_directory_if_not_exist(self,directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def create_time_stamps(self):
        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    def backup_files(self,src_dir,dest_dir):
        backup_dir = os.path.join(dest_dir,'Backup')
        self.create_directory_if_not_exist(backup_dir)

        timestamp = self.create_time_stamps()
        src_name = os.path.basename(src_dir)
        backup_name = f"{src_name} Backup {timestamp}"

        backup_path = os.path.join(backup_dir,backup_name)
        self.create_directory_if_not_exist(backup_path)

        for folder in os.listdir(src_dir):
            source_path = os.path.join(src_dir,folder)
            destination_path = os.path.join(backup_path,folder)

            if os.path.isdir(source_path):
                if not os.path.exists(destination_path):
                    shutil.copytree(source_path,destination_path)
                    self.log_message(f'{source_path} Copied to  {destination_path}')
                else:
                    self.log_message(f'Directory {destination_path} already exists, skipping')
            else:
                if not os.path.exists(destination_path):
                    shutil.copy2(source_path,destination_path)
                    self.log_message(f'{source_path} Copied to  {destination_path}')
                else:
                    self.log_message(f'File {destination_path} alread exists, skippig.')
        self.log_message(f'Finished Back Up to {backup_path}')

    def find_usb_name(self, usb_name):
        drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
        
        for drive in drives:
            drive_type = win32file.GetDriveType(drive)
            if drive_type == win32file.DRIVE_REMOVABLE:
                try:
                    volume_label = win32api.GetVolumeInformation(drive)[0]
                    if volume_label == usb_name:
                        return drive
                except Exception as e:
                    messagebox.showerror('Error',f'Could not retrieve label for drive {drive}: {e}')
        return None
    
    def main_process(self,src_dir,usb_name):
        while self.__is_running:
                try:
                    usb_mount = self.find_usb_name(usb_name)

                    if usb_mount:
                        self.log_message(f'BackUp USB ({usb_name}) detected at {usb_mount}')
                        self.backup_files(src_dir,usb_mount)
                        break
                    else:
                        self.log_message(f'{usb_name} not Detected. Checking again in 15seconds')
                        time.sleep(15)
                except Exception as e:
                    print(f"Error occurred during backup: {str(e)}")
                    messagebox.showerror("Backup Error", f"An error occurred during backup: {str(e)}")
                    self.__is_running = False
                    self.__button['Browse'].config(state=tk.NORMAL)
                    self.__button['Settings_btn'].config(state=tk.NORMAL)
                    self.__button['Start_btn'].config(state=tk.NORMAL)
                    self.__button['Stop_btn'].config(state=tk.DISABLED)
    
    def load_data(self):
        try:
            with open('backup_usb.json','r') as file:
                return json.load(file)
        except Exception as e:
            return {"usb_backup": ""}

    def save_data(self):
        with open('backup_usb.json','w') as file:
            json.dump(self.__data,file,indent=4)
    
    def overwrite_usb(self):
        new_backup_usb = self.__usb_name['Change_backup_usb'].get()
        self.__data['usb_backup'] = new_backup_usb
        self.save_data()
        messagebox.showinfo('INFO',f'Change Successfully Your Backup USB registered now: {new_backup_usb}')

    def help(self):
        self.settings_frame.grid_forget()
        self.help_frame.grid(row=0,column=1)

        title = self.__label_entry.add_label_with_grid(self.help_frame,"HELP","Open Sans Condensed",50,'#AFDDE5',None,0,0,10,5)
        title.grid_configure(columnspan=2)

        help_text = (
        "How to use:\n"
        "1. Install the requirement.txt using pip install -r requirement.txt\n"
        "2. Change the src_dir to the directory you want to back up.\n"
        "3. Change the back_up_usb_name to your USB name.\n"
        "4. Plug in the USB and click 'Start Backup'.\n"
        "Reminders"
        "If you don't know the label or name of your USB, run the test.py program,\n"
        "it will show you the drive and label of your USB."
        )

        help_text_label = tk.Label(self.help_frame,text=help_text,font=('Open Sans Condensed',15),bg='#AFDDE5',justify='left')
        help_text_label.grid(row=1,column=1,padx=10,pady=5)
        
        self.back_btn = tk.Button (self.help_frame,text='Back',command=self.settings,font=("Times New Roman",15),height= 1,width= 10,bg='#AFDDE5')
        self.back_btn.grid(row=2,column=1,padx=10,pady=5)

    def change_usb(self):
        self.settings_frame.grid_forget()
        self.change_backup_usb_frame.grid(row=0,column=1)
        change_backup_usb_label = self.__label_entry.add_label_with_grid(self.change_backup_usb_frame,"New Backup Usb Name:", "Open Sans Condensed", 15,'#AFDDE5',None,0,0,10,5)
        self.__usb_name['Change_backup_usb'] = self.__label_entry.add_entry_with_grid(self.change_backup_usb_frame,0,1,10,5,'')
        
        self.__button['Change_backup_usb_btn'] = tk.Button(self.change_backup_usb_frame,text='Change',command=self.overwrite_usb,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Change_backup_usb_btn'].grid(row=1,column=0,padx=10,pady=5)

        self.back_btn = tk.Button (self.change_backup_usb_frame,text='Back',command=self.settings,font=("Times New Roman",15),height= 1,width= 10,bg='#AFDDE5')
        self.back_btn.grid(row=1,column=1,padx=10,pady=5)

    def check_usb_name(self):
        drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
        usb_found = False

        for drive in drives:
            drive_type = win32file.GetDriveType(drive)
            if drive_type == win32file.DRIVE_REMOVABLE:
                volume_label = win32api.GetVolumeInformation(drive)[0]
                messagebox.showinfo('INFO',f'Drive: {drive} - Label: {volume_label}')
                usb_found = True
                break
        if not usb_found:
                messagebox.showwarning('warning','No USB Drive Inserted!!!')

    def settings(self):
        self.directory_frame.grid_forget()
        self.change_backup_usb_frame.grid_forget()
        self.help_frame.grid_forget()
        self.settings_frame.grid(row=0, column=0)

        text_label = tk.Label(self.settings_frame,text='Settings',font=('Open Sans Condensed',60),bg='#AFDDE5',justify='center')
        text_label.grid(row=0,column=0,padx=10,pady=5)
        text_label.grid_configure(columnspan=4)

        self.__button['Help_btn'] = tk.Button(self.settings_frame,text='Help',command=self.help,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Help_btn'].grid(row=1,column=0,padx=10,pady=5)

        self.__button['Change_usb_btn'] = tk.Button(self.settings_frame,text='Change Backup Usb',command=self.change_usb,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Change_usb_btn'].grid(row=1,column=1,padx=10,pady=5)

        self.__button['Check_usb_name_btn'] = tk.Button(self.settings_frame,text='Check Usb Name',command=self.check_usb_name,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Check_usb_name_btn'].grid(row=1,column=2,padx=10,pady=5)

        self.__button['Back_btn'] = tk.Button(self.settings_frame,text='Back',command=self.main,font=("Times New Roman",15),height=1,width=15,bg='#AFDDE5')
        self.__button['Back_btn'].grid(row=1,column=3,padx=10,pady=5)

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.yview(tk.END)
    
    def clear_log_message(self):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)

    def start_backup(self):
        src_dir = self.__directory['Directory'].get()
        usb_name = self.__data['usb_backup']
        if not src_dir:
            messagebox.showwarning('Input Error',"Please Select a Source Directory!!")
            return
        
        if not self.__is_running:
            self.__is_running = True
            self.clear_log_message()
            self.__button['Browse'].config(state=tk.DISABLED)
            self.__button['Settings_btn'].config(state=tk.DISABLED)
            self.__button['Start_btn'].config(state=tk.DISABLED)
            self.__button['Stop_btn'].config(state=tk.NORMAL)
            self.__backup_thread = threading.Thread(target=self.main_process, args=(src_dir, usb_name))
            self.__backup_thread.start()

    def stop_backup(self):
        if self.__is_running:
            self.__is_running = False
            self.__button['Browse'].config(state=tk.NORMAL)
            self.__button['Settings_btn'].config(state=tk.NORMAL)
            self.__button['Start_btn'].config(state=tk.NORMAL)
            self.__button['Stop_btn'].config(state=tk.DISABLED)

    def browse_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.__directory['Directory'].delete(0,tk.END)
            self.__directory['Directory'].insert(0,directory_path)
        
    def __configure_window(self):
        self.title('AutoBackUp')
        self.configure(bg='light blue')

    
    def display(self):
        self.main()
        self.mainloop()


app = autoBackUp()
app.display()