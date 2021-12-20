import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter
from tkinter import messagebox
from tkinter import filedialog

stimuli_list = [1346, 1884, 2259, 2727, 3122]
threshold = 50
Shortest_M_bout_duration = 5
Activity_dur = 120  # (sec)
Baseline_start = 600  # (images)


def select_file():
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo('select file', 'select file')
    path = filedialog.askopenfilename()
    dir_path = os.path.dirname(path)
    os.chdir(dir_path)
    os.makedirs("./dfs", exist_ok=True)
    os.makedirs("./figs", exist_ok=True)
    return path


def duration_analysis(data, stimulated_frame):
    extracted_data = data[stimulated_frame:].iloc[:, 1].values
    if extracted_data[0] != 1:
        motion_duration = 0
    else:
        motion_duration = np.argmin(extracted_data) / 2
    return motion_duration


def analysis(path, stimuli_list):
    data = pd.read_csv(path)
    timeaxis = data.iloc[:, 0] * 0.5

    # make activity graphs
    plt.plot(data.iloc[:, 1], color="black")
    plt.ylim(0, 1000)
    plt.savefig("./figs/activity_plot.png")

    # make M Q graph
    motion_data = data.iloc[:, 1].values
    MorQ = np.where(motion_data > threshold, 1, 0)
    plt.plot(MorQ, color="black")
    plt.savefig("./figs/MorQ.png")

    # calc motion and make graphs
    tempstart = 0
    motion = np.zeros(len(timeaxis))
    for i in np.where(motion_data > threshold)[0]:
        timeduration = float(timeaxis[i] - timeaxis[tempstart])
        if timeduration <= Shortest_M_bout_duration:
            motion[tempstart:i] = 1
        else:
            pass
        tempstart = i

    plt.plot(motion, color="black")
    plt.savefig("./figs/motion_bout_fig.png")
    timeaxis_array = timeaxis.values
    motion_bout_df = pd.DataFrame(np.vstack([timeaxis_array, motion]).T, columns=["time", "motion_bout"])
    motion_bout_df.to_csv("./dfs/motion_bout_df.csv", index=False)

    motion_duration_list = []
    for i in range(len(stimuli_list)):
        motion_duration_list.append(duration_analysis(motion_bout_df, stimuli_list[i]))
    motion_duration_df = pd.DataFrame(np.vstack((stimuli_list, motion_duration_list)).T,
                                      columns=["stimuli timing", "motion_duration (sec)"])
    motion_duration_df.to_csv("./dfs/motion_duration_df.csv", index=False)
    return motion_bout_df


def activity_analysis(path, stimuli_list):
    data = pd.read_csv(path)
    timeaxis = data.iloc[:, 0] * 0.5
    data["time"] = timeaxis
    for i in range(len(stimuli_list)):
        start = stimuli_list[i] - 2 * Shortest_M_bout_duration
        end = stimuli_list[i] + Activity_dur * 2
        extracted_df = data.iloc[start:end, 1]
        extracted_df.to_csv("./dfs/Stimuli_{}.csv".format(i), index=False)


def maxisland_start_len_mask(a, fillna_index=-1, fillna_len=0):
    # a is a boolean array
    a = np.array(a)
    a = a.reshape(len(a), 1)

    pad = np.zeros(a.shape[1], dtype=bool)
    mask = np.vstack((pad, a, pad))

    mask_step = mask[1:] != mask[:-1]
    idx = np.flatnonzero(mask_step.T)
    island_starts = idx[::2]
    island_lens = idx[1::2] - idx[::2]
    n_islands_percol = mask_step.sum(0) // 2

    bins = np.repeat(np.arange(a.shape[1]), n_islands_percol)
    scale = island_lens.max() + 1

    scaled_idx = np.argsort(scale * bins + island_lens)
    grp_shift_idx = np.r_[0, n_islands_percol.cumsum()]
    max_island_starts = island_starts[scaled_idx[grp_shift_idx[1:] - 1]]

    max_island_percol_start = max_island_starts % (a.shape[0] + 1)

    valid = n_islands_percol != 0
    cut_idx = grp_shift_idx[:-1][valid]
    max_island_percol_len = np.maximum.reduceat(island_lens, cut_idx)

    out_len = np.full(a.shape[1], fillna_len, dtype=int)
    out_len[valid] = max_island_percol_len
    out_index = np.where(valid, max_island_percol_start, fillna_index)
    return island_starts, island_lens


def Change_data_to_boolian_df(data_array, time_axis):
    data_df = pd.DataFrame(np.stack([time_axis, data_array], axis=1), columns=["time", "locomotor_activity"])
    data_df["loc_bool"] = np.where(data_df["locomotor_activity"].values < threshold, 0, 1)
    data_df["loc_bool_not"] = np.where(data_df["locomotor_activity"].values < threshold, 1, 0)
    return data_df


def State_analysis_preprocessing(M_starts, M_durations, Q_starts, Q_durations):
    # if the motion bouts started before quiescent bouts, delete the first q bout
    if M_starts[0] > Q_starts[0]:
        Q_durations = Q_durations[1:]
    if len(M_durations) > len(Q_durations):
        M_durations = M_durations[:-1]
    Bouts_df = pd.DataFrame(np.stack([M_durations, Q_durations], axis=1),
                            columns=["Motion_bout", "Quiescent_bout"])
    return Bouts_df


def state_analysis(path, stimuli_list):
    """
    :param path: csv file path
    :param stimuli_list: blue light stim list

    This function conduct the state analysis for the optogenetics experiment
    """
    data = pd.read_csv(path)
    data["time"] = data.iloc[:, 0] * 0.5
    # extract the before stim data
    if stimuli_list[0] < Baseline_start:
        pass
    else:
        # before stimulation analysis
        before_stim_data = data[Baseline_start:stimuli_list[0]]
        before_stim_df = Change_data_to_boolian_df(before_stim_data["0"].values, before_stim_data["time"].values)
        Before_M_starts, Before_M_durations = maxisland_start_len_mask(before_stim_df["loc_bool"])
        Before_Q_starts, Before_Q_durations = maxisland_start_len_mask(before_stim_df["loc_bool_not"])
        Before_bouts_df = State_analysis_preprocessing(Before_M_starts,
                                                       Before_M_durations,
                                                       Before_Q_starts,
                                                       Before_Q_durations)
        Before_bouts_df.to_csv("./dfs/Before_bouts_df.csv", index=False)

        # after stimulation analysis
        after_stim_data_list = [data[stimuli_list[i]:stimuli_list[i + 1] - 1] for i in range(len(stimuli_list)-1)]
        for i in range(len(after_stim_data_list)):
            temp_stim_data = after_stim_data_list[i]
            temp_stim_df = Change_data_to_boolian_df(temp_stim_data["0"].values, temp_stim_data["time"].values)
            M_starts, M_durations = maxisland_start_len_mask(temp_stim_df["loc_bool"])
            Q_starts, Q_durations = maxisland_start_len_mask(temp_stim_df["loc_bool_not"])
            Bouts_df = State_analysis_preprocessing(M_starts,
                                                    M_durations,
                                                    Q_starts,
                                                    Q_durations)
            Bouts_df.to_csv("./dfs/Stim{}_bouts_df.csv".format(i), index=False)


def main():
    path = select_file()
    motion_bout_df = analysis(path, stimuli_list)
    activity_analysis(path, stimuli_list)
    state_analysis(path, stimuli_list)


if __name__ == '__main__':
    main()
