import os
import shutil
import send2trash
import subprocess
from ctypes import windll, wintypes
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

downloads_folder = None

def list_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def move_file(file, source_folder, dest_folder):
    shutil.move(os.path.join(source_folder, file), os.path.join(dest_folder, file))
    desktop_path = os.path.normpath(os.path.join(os.path.expanduser('~'), 'Desktop'))
    if os.path.normpath(dest_folder) == desktop_path:
        refresh_desktop()

def open_file(file, source_folder):
    file_path = os.path.join(source_folder, file)
    os.startfile(file_path)

def view_in_explorer(file, source_folder):
    file_path = os.path.join(source_folder, file)
    if os.name == 'nt': 
        subprocess.run(f'explorer /select,"{file_path}"', shell=True)

def refresh_desktop():
    SHCNE_ASSOCCHANGED = 0x8000000
    SHCNF_FLUSH = 0x1000
    windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_FLUSH, None, None)

def update_file_list():
    if downloads_folder:
        listbox_files.delete(0, tk.END)
        files = os.listdir(downloads_folder)
        for file in files:
            listbox_files.insert(tk.END, file)

def select_next_item(previous_index):
    list_size = listbox_files.size()
    if list_size > 0:
        next_index = min(previous_index[0], list_size - 1)
        listbox_files.select_set(next_index)
        listbox_files.activate(next_index)
        listbox_files.see(next_index)  # Scroll to the selected item
    else:
        listbox_files.selection_clear(0, tk.END)

def on_move():
    if downloads_folder:
        selected_index = listbox_files.curselection()
        if selected_index:
            selected_file = listbox_files.get(selected_index)
            dest_folder = filedialog.askdirectory()
            if dest_folder:
                move_file(selected_file, downloads_folder, dest_folder)
                update_file_list()
                new_index = (selected_index[0],) if selected_index[0] < listbox_files.size() else (listbox_files.size() - 1,)
                select_next_item(new_index)

def on_trash():
    if downloads_folder:
        selected_index = listbox_files.curselection()
        if selected_index:
            selected_file = listbox_files.get(selected_index)
            file_path = os.path.join(downloads_folder, selected_file)
            normalized_path = os.path.normpath(file_path)
            if os.path.exists(normalized_path):
                try:
                    send2trash.send2trash(normalized_path)
                    update_file_list()
                    new_index = (selected_index[0],) if selected_index[0] < listbox_files.size() else (listbox_files.size() - 1,)
                    select_next_item(new_index)
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {e}")
            else:
                messagebox.showinfo("Info", "File does not exist.")


def on_open():
    if downloads_folder:
        selected_index = listbox_files.curselection()
        if selected_index:
            selected_file = listbox_files.get(selected_index)
            open_file(selected_file, downloads_folder)

def on_view_in_explorer():
    if downloads_folder:
        selected_index = listbox_files.curselection()
        if selected_index:
            selected_file = listbox_files.get(selected_index)
            view_in_explorer(selected_file, downloads_folder)
        
def choose_directory():
    global downloads_folder
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        downloads_folder = folder_selected
        update_file_list()

def rename_file(file, source_folder):
    new_name = simpledialog.askstring("Rename", "New name for the file:", initialvalue=file)
    if new_name and new_name != file:
        old_file_path = os.path.join(source_folder, file)
        new_file_path = os.path.join(source_folder, new_name)
        try:
            os.rename(old_file_path, new_file_path)
            update_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while renaming: {e}")
    elif not new_name:
        messagebox.showinfo("Info", "Rename cancelled.")

def on_rename():
    if downloads_folder:
        selected_index = listbox_files.curselection()
        if selected_index:
            selected_file = listbox_files.get(selected_index)
            rename_file(selected_file, downloads_folder)

# Set up the main application window
root = tk.Tk()
root.title("File Organizer")

# Listbox for files
listbox_files = tk.Listbox(root, width=50, height=20)
listbox_files.pack(pady=20)

# Buttons for actions
button_choose_dir = tk.Button(root, text="Choose Folder", command=choose_directory)
button_choose_dir.pack(side=tk.LEFT, padx=10)

button_open = tk.Button(root, text="Open", command=on_open)
button_open.pack(side=tk.LEFT, padx=10)

button_rename = tk.Button(root, text="Rename", command=on_rename)
button_rename.pack(side=tk.LEFT, padx=10)

button_move = tk.Button(root, text="Move", command=on_move)
button_move.pack(side=tk.LEFT, padx=10)

button_trash = tk.Button(root, text="Trash", command=on_trash)
button_trash.pack(side=tk.LEFT, padx=10)

button_view = tk.Button(root, text="View in Explorer", command=on_view_in_explorer)
button_view.pack(side=tk.LEFT, padx=10)

# Start the GUI event loop
root.mainloop()
