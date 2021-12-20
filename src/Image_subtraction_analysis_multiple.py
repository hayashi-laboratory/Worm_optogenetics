# -*- coding: utf-8 -*-
"""

"""
import pathlib

import cv2
import datetime
import os
import os.path

import tkinter
from tkinter import filedialog
from tkinter import messagebox

import numpy as np
import pandas as pd

from numpy import ndarray
from skimage.color import rgb2gray

from skimage import io, img_as_float
from tqdm import tqdm


# parameters
threshold = 7


def ask_dir_name():
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showinfo('select directory', 'select analyzing directory')
    directory = filedialog.askdirectory()
    os.chdir(directory)


def search_image_dir_path():
    # search dirname = Pos0
    image_dir_path_list = []
    for curDir, dirs, files in os.walk("../../Optogenetics_analysis/tests/"):
        if curDir.split("\\")[-1] == "Pos0":
            image_dir_path_list.append(pathlib.Path(curDir).resolve())
        else:
            pass
    return image_dir_path_list


def get_image_path_list(path):
    os.chdir(path)
    path_list = os.listdir('.')
    path_list = [i for i in path_list if os.path.splitext(i)[1] == '.jpg' \
                 or os.path.splitext(i)[1] == '.png' \
                 or os.path.splitext(i)[1] == ".tiff" \
                 or os.path.splitext(i)[1] == ".tif"]
    return path_list


def image_subtraction_analysis(image_path_list):
    threshold_list = []
    data_list: list = []
    for n in tqdm(range(len(image_path_list) - 1)):
        img1_path = image_path_list[n]
        img2_path = image_path_list[(int(n) + 1)]
        img1: ndarray = cv2.GaussianBlur(rgb2gray(img_as_float(io.imread(img1_path))), (5, 5), 1)
        img2: ndarray = cv2.GaussianBlur(rgb2gray(img_as_float(io.imread(img2_path))), (5, 5), 1)
        subtracted_image = cv2.absdiff(img1, img2)
        subtracted_image = cv2.GaussianBlur(subtracted_image, (5, 5), 1)
        threshold = subtracted_image.mean() + 7 * subtracted_image.std()
        data_list.append(np.count_nonzero(subtracted_image > threshold))
        threshold_list.append(threshold)
    data_array = np.array([data_list, threshold_list])
    return data_array


def data_save(data_list):
    s = pd.DataFrame(data_list.T)
    s_name = os.path.basename("./")

    date = datetime.date.today()
    time = datetime.datetime.now()
    os.chdir('../')
    os.makedirs('./analyzed_data_{}'.format(date), exist_ok=True)
    os.chdir('./analyzed_data_{}'.format(date))
    s.to_csv('./locomotor_activity_th={0}.csv'.format(threshold))
    path_w = './readme.txt'
    contents = '\nanalyzed_date: {0}\nthreshold: {1}'.format(time,threshold)

    with open(path_w, mode="a") as f:
        f.write(contents)


def main():
    ask_dir_name()
    image_dir_path_list = search_image_dir_path()
    print(image_dir_path_list)
    for i in range(len(image_dir_path_list)):
        image_dir_path = image_dir_path_list[i]
        image_path_list = get_image_path_list(image_dir_path)
        data_array = image_subtraction_analysis(image_path_list)
        data_save(data_array)


if __name__ == '__main__':
    main()
