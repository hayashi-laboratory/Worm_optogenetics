import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter
from tkinter import messagebox
from tkinter import filedialog

stimuli_list = [251, 572, 1079]
Baseline_duration = 10 # (sec)
Activity_dur = 90  # (sec)


def select_file():
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo('select file', 'select file')
    path = filedialog.askopenfilename()
    dir_path = os.path.dirname(path)
    os.chdir(dir_path)
    os.makedirs("./dfs", exist_ok=True)
    return path


def activity_analysis(path, stimuli_list):
    data = pd.read_csv(path)
    timeaxis = data.iloc[:, 0] * 0.5
    data["time"] = timeaxis
    for i in range(len(stimuli_list)):
        start = stimuli_list[i] - Baseline_duration * 2
        end = stimuli_list[i] + Activity_dur * 2
        extracted_df = data.iloc[start:end, 1]
        extracted_df.to_csv("./dfs/Stimuli_{}.csv".format(i), index=False)


def main():
    path = select_file()
    activity_analysis(path, stimuli_list)


if __name__ == '__main__':
    main()
