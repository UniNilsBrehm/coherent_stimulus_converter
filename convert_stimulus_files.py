#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comment
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython import embed


def moving_target(s_file):
    # There are two moving target presentations

    dot_pos = s_file[0]  # in degrees (horizontal)
    time_sec = s_file[3]  # in secs from recording start

    # Compute difference in time to get the interval between the two repetitions
    time_diff = np.diff(time_sec)
    idx_interval = np.where(time_diff > 10)[0][0]

    # Find onsets and offsets
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
    rec_duration = 90  # in secs
    grating_status = s_file[0] # 1: start moving, -1: stopp moving
    time_sec = s_file[3]  # in secs from recording start

    starts = grating_status == 1
    stops = grating_status == -1

    start_times = time_sec[starts].to_numpy()
    stop_times = time_sec[stops].to_numpy()

    fr = 60
    binary = np.zeros(int(fr * rec_duration))
    binary[int(fr * start_times[0]):int(fr * stop_times[0])] = 1
    binary[int(fr * start_times[1]):int(fr * stop_times[1])] = 1

    # time_axis = np.linspace(0, 90, int(fr * 90))
    # plt.plot(time_axis, binary)
    # plt.show()

    return binary

def looming(s_file):
    rec_duration = 90  # in secs
    disc_size = s_file[0] # in degrees
    time_sec = s_file[3]  # in secs from recording start

    fr = np.ceil(1 / np.diff(time_sec).mean())  # 60 Hz

    binary = np.zeros(int(fr * rec_duration))
    binary[0:int(np.ceil(time_sec.max() * fr))] = disc_size

    # time_axis = np.linspace(0, 90, int(fr * 90))
    # plt.plot(time_axis, binary)
    # plt.show()

    return binary

def flash(s_file):
    rec_duration = 90  # in secs
    flash_status = s_file[0]
    time_sec = s_file[1]  # in secs from recording start

    idx = flash_status == 1
    flash_on = time_sec[idx].to_numpy()

    fr = 60

    binary = np.zeros(int(fr * rec_duration))
    binary[int(fr * flash_on[0]):int(fr * flash_on[1])] = 1

    time_axis = np.linspace(0, 90, int(fr * 90))
    plt.plot(time_axis, binary)
    plt.show()

    return binary

def read_csv_file_missing_data(file_dir, missing_col=3):
    fixed_rows = []

    with open(file_dir) as f:
        for line in f:
            fields = line.strip().split("\t")
            if len(fields) == 5:
                # column 3 is missing, insert '0' at position 2 (0-based index)
                fields.insert(missing_col, '0')
            fixed_rows.append(fields)

    # convert to DataFrame
    df = pd.DataFrame(fixed_rows)

    # assign column names if you wish
    # df.columns = [f"col{i + 1}" for i in range(df.shape[1])]

    # convert numbers
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except Exception:
            pass  # keep column as is if it cannot be converted

    return df

def main():
    file_dir = 'C:/UniFreiburg/Code/visual_stimulus_converter/stimulus_files/sw_15_flash.txt'
    s_file = pd.read_csv(file_dir, sep='\t', header=None, on_bad_lines='warn')

    binary = flash(s_file)
    binary.to_csv(save_dir)

    # For gratings
    # s_file = read_csv_file_missing_data(file_dir, missing_col=3)


if __name__ == "__main__":
    main()
