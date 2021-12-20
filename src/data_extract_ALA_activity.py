"""
Run and select wATR or woATR
This script extract all sleep and motion bouts before and after each stimulation

wATR, woATRのディレクトリ直下で実行
stimのデータを抽出してまとめる
"""

import os
import re
import numpy as np
import pandas
import tkinter
from tkinter import filedialog
from tkinter import messagebox

import pandas as pd


def ask_dir_name():
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo('select directory', 'select analyzing directory')
    directory = filedialog.askdirectory()
    os.chdir(directory)


def search_subdivided_dir_path():
    """
    extract the Stimuli_**.csv paths from selected directory
    :return
    stimuli_data_list: list, path of csv files, full path
    date_list: list, analysis date list, for making directories
    """
    date_list = []
    stimuli_data_list = []
    bouts_data_list = []
    for curDir, dirs, files in os.walk("./"):
        for file in files:
            if len(curDir.split("\\")) != 1:
                pre_date_list = [i for i in curDir.split("\\") if re.match("analyzed_data_\d+-\d+-\d+", i)]
                if pre_date_list:
                    date = pre_date_list[0].split("_")[-1]
                    if date in date_list:
                        pass
                    else:
                        date_list.append(date)
                else:
                    pass
            if os.path.basename(file).split("_")[0] == "Stimuli":
                stimuli_data_list.append(os.path.join(curDir, file))
            elif len(os.path.basename(file).split("_"))>1:
                if os.path.basename(file).split("_")[1] == "bouts":
                    bouts_data_list.append(os.path.join(curDir, file))
            else:
                pass
    return stimuli_data_list, bouts_data_list


def data_extraction_and_summarize(stimuli_data_list):
    data_dict = {}
    for path in stimuli_data_list:
        # get date
        current_data_analyzed_date_list = [i for i in path.split("\\") if re.match("analyzed_data_\d+-\d+-\d+", i)]
        if current_data_analyzed_date_list:
            current_data_analyzed_date = current_data_analyzed_date_list[0].split("_")[-1]
        else:
            pass
        # get experiment name
        current_data_experiment_name_list = [i for i in path.split("\\") if re.findall("\w+_remEx\w+\+|\-+\w+", i)]
        if current_data_experiment_name_list:
            current_data_experiment_name = current_data_experiment_name_list[0].split("/")[-1]
        else:
            pass
        # get worm number
        current_worm_number_list = [i for i in path.split("\\") if re.findall("_\d", i)]
        if current_worm_number_list:
            current_worm_number = "worm" + current_worm_number_list[0]
        else:
            pass
        # get stimuli number
        current_stimuli_number = path.split("\\")[-1].split("_")[-1].split(".")[0]

        # make destination directory
        os.makedirs("./extracted_data", exist_ok=True)

        # get data
        current_data_array = pd.read_csv(path).values
        current_data_name = current_data_experiment_name + current_worm_number + "Stimuli_" + current_stimuli_number

        # add data
        if current_data_analyzed_date in data_dict:
            if len(data_dict[current_data_analyzed_date]) != len(current_data_array):
                pass
            else:
                saved_df = data_dict[current_data_analyzed_date]
                saved_df[current_data_name] = current_data_array
        else:
            data_dict[current_data_analyzed_date] = pd.DataFrame(current_data_array.T[0],
                                                                 columns=[current_data_name])

    for key in data_dict:
        data = data_dict[key]
        data.to_csv("./extracted_data/{}.csv".format(key))


def bouts_extraction_and_summarize(bouts_data_list):
    data_dict = {}
    for path in bouts_data_list:
        # get date
        current_data_analyzed_date_list = [i for i in path.split("\\") if re.match("analyzed_data_\d+-\d+-\d+", i)]
        if current_data_analyzed_date_list:
            current_data_analyzed_date = current_data_analyzed_date_list[0].split("_")[-1]
        else:
            pass
        # get experiment name
        current_data_experiment_name_list = [i for i in path.split("\\") if re.findall("\w+_remEx\w+\+|\-+\w+", i)]
        if current_data_experiment_name_list:
            current_data_experiment_name = current_data_experiment_name_list[0].split("/")[-1]
        else:
            pass
        # get worm number
        current_worm_number_list = [i for i in path.split("\\") if re.findall("_\d", i)]
        if current_worm_number_list:
            current_worm_number = "worm" + current_worm_number_list[0]
        else:
            pass
        # get stimuli number
        current_stimuli_number = path.split("\\")[-1].split("_")[0]
        # make destination directory
        os.makedirs("./extracted_data", exist_ok=True)

        # get data
        current_df = pd.read_csv(path)
        current_data_name = current_data_experiment_name + current_worm_number + current_stimuli_number

        # add data
        if current_data_analyzed_date in data_dict:
            current_df=current_df.rename(columns={"Motion_bout":"{}_motion_bout".format(current_stimuli_number),
                                                  "Quiescent_bout":"{}_quiescent_bout".format(current_stimuli_number)})
            saved_df = data_dict[current_data_analyzed_date]
            data_dict[current_data_analyzed_date] = pd.concat([saved_df, current_df],axis=1)
        else:
            current_df = current_df.rename(columns={"Motion_bout": "{}_motion_bout".format(current_stimuli_number),
                                                    "Quiescent_bout": "{}_quiescent_bout".format(
                                                        current_stimuli_number)})
            data_dict[current_data_analyzed_date] = current_df

    for key in data_dict:
        data = data_dict[key]
        data.to_csv("./extracted_data/{}_bouts.csv".format(key))


def main():
    ask_dir_name()
    stimuli_data_list, bouts_data_list = search_subdivided_dir_path()
    data_extraction_and_summarize(stimuli_data_list)
    bouts_extraction_and_summarize(bouts_data_list)

if __name__ == '__main__':
    main()
