#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


def moving_target(s_file):
    dot_pos = s_file[0]
    time_sec = s_file[3]
    time_diff = np.diff(time_sec)
    idx_interval = np.where(time_diff > 10)[0][0]

    mt_01_start = time_sec.iloc[0]
    mt_01_stop = time_sec.iloc[idx_interval]
    mt_02_start = time_sec.iloc[idx_interval+1]
    mt_02_stop = time_sec.iloc[-1]

    fr = 60
    binary = np.zeros(int(fr * (time_sec.max() + time_sec.min())))
    binary[int(fr * mt_01_start):int(fr * mt_01_stop)] = 1
    binary[int(fr * mt_02_start):int(fr * mt_02_stop)] = 1
    return binary

def grating(s_file):
    rec_duration = 90
    grating_status = s_file[0]
    time_sec = s_file[3]
    starts = grating_status == 1
    stops = grating_status == -1

    start_times = time_sec[starts].to_numpy()
    stop_times = time_sec[stops].to_numpy()

    fr = 60
    binary = np.zeros(int(fr * rec_duration))
    binary[int(fr * start_times[0]):int(fr * stop_times[0])] = 1
    binary[int(fr * start_times[1]):int(fr * stop_times[1])] = 1
    return binary

def looming(s_file):
    rec_duration = 90
    disc_size = s_file[0]
    time_sec = s_file[3]
    fr = np.ceil(1 / np.diff(time_sec).mean())
    binary = np.zeros(int(fr * rec_duration))
    binary[0:int(np.ceil(time_sec.max() * fr))] = disc_size
    return binary

def flash(s_file):
    rec_duration = 90
    flash_status = s_file[0]
    time_sec = s_file[1]
    idx = flash_status == 1
    flash_on = time_sec[idx].to_numpy()

    fr = 60
    binary = np.zeros(int(fr * rec_duration))
    binary[int(fr * flash_on[0]):int(fr * flash_on[1])] = 1
    return binary

def read_csv_file_missing_data(file_dir, missing_col=3):
    fixed_rows = []
    with open(file_dir) as f:
        for line in f:
            fields = line.strip().split("\t")
            if len(fields) == 5:
                fields.insert(missing_col, '0')
            fixed_rows.append(fields)
    df = pd.DataFrame(fixed_rows)
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except Exception:
            pass
    return df

def process_file(filepath, stim_type):
    if not filepath:
        messagebox.showerror("Error", "No file selected.")
        return

    # Load file
    if stim_type == "grating":
        s_file = read_csv_file_missing_data(filepath, missing_col=3)
    else:
        s_file = pd.read_csv(filepath, sep='\t', header=None, on_bad_lines='warn')

    # Process
    if stim_type == "flash":
        binary = flash(s_file)
    elif stim_type == "moving_target":
        binary = moving_target(s_file)
    elif stim_type == "grating":
        binary = grating(s_file)
    elif stim_type == "looming":
        binary = looming(s_file)
    else:
        messagebox.showerror("Error", f"Unknown stimulus type: {stim_type}")
        return

    # Save
    save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if save_path:
        pd.Series(binary).to_csv(save_path, index=False)
        messagebox.showinfo("Success", f"Saved binary trace to:\n{save_path}")

def launch_gui():
    root = tk.Tk()
    root.title("Stimulus Log Converter - Coherent 2P Setup - 2025")

    # File chooser
    file_label = tk.Label(root, text="Stimulus Log File:")
    file_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    file_path_var = tk.StringVar()
    file_entry = tk.Entry(root, textvariable=file_path_var, width=50)
    file_entry.grid(row=0, column=1, padx=5, pady=5)

    def browse_file():
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        file_path_var.set(filename)

    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.grid(row=0, column=2, padx=5, pady=5)

    # Stimulus type dropdown
    stim_label = tk.Label(root, text="Stimulus Type:")
    stim_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

    stim_type_var = tk.StringVar(value="flash")
    stim_type_options = ["flash", "moving_target", "grating", "looming"]
    stim_dropdown = ttk.Combobox(root, textvariable=stim_type_var, values=stim_type_options, state="readonly")
    stim_dropdown.grid(row=1, column=1, padx=5, pady=5)

    # Process button
    process_button = tk.Button(root, text="Process",
                               command=lambda: process_file(file_path_var.get(), stim_type_var.get()))
    process_button.grid(row=2, column=1, pady=10)

    root.mainloop()


if __name__ == "__main__":
    launch_gui()
