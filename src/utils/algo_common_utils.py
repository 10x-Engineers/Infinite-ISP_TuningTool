"""
File: algo_common_utils.py
Description: This file contains common functions used in algorithms.
Author: 10xEngineers
------------------------------------------------------------
"""
import re
import tkinter as tk
from tkinter import filedialog as fd
from pathlib import Path
import os
import numpy as np
import cv2
from src.utils.gui_common_utils import generate_separator


class RawImageParameters:
    """
    This class stores the detail of the selected
    file and also save the raw and rgb images.
    """

    def __init__(self, file_name):
        self.file_name = file_name
        self.width = 1920
        self.height = 1080
        self.bit_depth = 10
        self.bayer_pattern = "RGGB"
        self.rgb_image = None
        self.raw_image = None

    def store_parameters(self, parameters):
        """
        Store parameters for a raw image
        """
        self.width = parameters[1]
        self.height = parameters[2]
        self.bit_depth = parameters[3]
        self.bayer_pattern = parameters[4]


def select_file(title, filetypes):
    """
    Function to select image file
    """
    root = tk.Tk()
    # Open dialog box in the foreground
    root.attributes("-topmost", True)
    root.withdraw()
    root.focus()
    default_folder = "data_set"
    default_path = os.path.join(os.getcwd(), default_folder)
    file_name = fd.askopenfile(
        title=title, initialdir=default_path, filetypes=filetypes
    )
    root.destroy()
    if file_name:
        return True, file_name
    else:
        return False, file_name


def get_rgb_image(raw_data, bayer):
    """
    Read the raw file
    """
    raw_image = cv2.normalize(
        raw_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8UC3
    )

    bayer_mapping = {
        "RGGB": cv2.COLOR_BAYER_RG2RGB,
        "GRBG": cv2.COLOR_BAYER_GR2RGB,
        "GBRG": cv2.COLOR_BAYER_GB2RGB,
        "BGGR": cv2.COLOR_BAYER_BG2RGB,
    }

    # Demosaic the raw image using the OpenCV library
    image_demosaic = cv2.cvtColor(raw_image, bayer_mapping[bayer])
    image_demosaic = cv2.cvtColor(image_demosaic, cv2.COLOR_BGR2RGB)

    return image_demosaic


def parse_file_name(file_name):
    """
    Parse the file name
    """
    # Expected pattern for file name
    pattern = r"(.+)_(\d+)x(\d+)_(\d+)(?:bit|bits)_(RGGB|GRBG|GBRG|BGGR)"

    # Check pattern in the string
    match_parttern = re.match(pattern, file_name)
    if match_parttern:
        name, width, height, bits, bayer = match_parttern.groups()

        # Convert width, height, and bits to integers
        width = int(width)
        height = int(height)
        bits = int(bits)

        return [name, width, height, bits, bayer]
    return []


def display_raw_parameters(parameters):
    """
    Display selected raw image parameters.
    """
    generate_separator("Selected raw image info", "-")
    print("Width  = ", parameters[1])
    print("Height = ", parameters[2])
    print("Bits   = ", parameters[3])
    print("Bayer  = ", parameters[4])

    # Display empty line
    print()


def extract_patches_mat(image, patches_points):
    """
    Crop the image into pataches with given points
    and return a mat array of 24 patches.
    """
    # Define an array to save mat of each mat
    patches_mat = []

    # Iterate through whole points and get mat
    total_patches = len(patches_points)

    for i in range(total_patches):
        start_point = patches_points[i][0]
        end_point = patches_points[i][1]
        patch = image[start_point[1] : end_point[1], start_point[0] : end_point[0]]

        patches_mat.append(patch)

    return patches_mat


def cal_patches_avg(patches_mat):
    """
    Calculate the average of patches mat and return average
    arrays for each channel r,g, and b after normalizing it.
    """
    r_avg = []
    g_avg = []
    b_avg = []

    for _, rgb_mat in enumerate(patches_mat):
        r_channel, g_channel, b_channel = cv2.split(rgb_mat)

        r_avg.append((cv2.mean(r_channel)[0]) / 255.0)
        g_avg.append((cv2.mean(g_channel)[0]) / 255.0)
        b_avg.append((cv2.mean(b_channel)[0]) / 255.0)

    return r_avg, g_avg, b_avg


def select_image_and_get_para(file_types):
    """
    Following steps are performed in this function, if need a raw file.
    1) Allowed user to select a image.
    2) Parsed the file name.
    3) Saved the extracted parameters.
    4) Displayed the parameters.

    For a rgb file, step 1 and step 3 are performed.
    """

    # Step 1
    title = "Open an image file."
    filetypes = file_types
    image_selected, file_selected = select_file(title, filetypes)

    if not image_selected:
        print("\033[31mError!\033[0m File is not selected.")
        generate_separator("", "*")
        return False, None

    file_name = file_selected.name
    path_object = Path(file_name)

    # Initialize the container to store image detail init.
    raw_image_para = RawImageParameters(file_selected.name)

    if path_object.suffix == ".raw":
        # Step 2
        parameters = parse_file_name(file_selected.name)
        if not parameters:
            print("\033[31mError!\033[0m Invalid file name format.\n")
            generate_separator("", "*")
            return False, None

        # Step 3
        raw_image_para.store_parameters(parameters)
        valid_image, raw_img = get_raw_image(
            raw_image_para.file_name,
            raw_image_para.width,
            raw_image_para.height,
            raw_image_para.bit_depth,
        )

        if not valid_image:
            return False, None

        # Convert the selected raw file into rgb_image.
        raw_image_para.raw_image = raw_img
        raw_image_para.rgb_image = get_rgb_image(raw_img, raw_image_para.bayer_pattern)

        # Step 4
        display_raw_parameters(parameters)

    else:
        rgb_image = cv2.imread(file_name)
        rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
        raw_image_para.rgb_image = rgb_image

    return True, raw_image_para


def get_raw_image(file_name, width, height, bits):
    """
    This function load the given file_name and return the raw image.
    """
    if bits == 8:
        data_type = np.uint8
    else:
        data_type = np.uint16

    # Get actual file size
    path_object = Path(file_name)
    file_size = path_object.stat().st_size

    # Calculate expected size and compare with actual size
    expected_size = height * width * np.dtype(data_type).itemsize
    if file_size != expected_size:
        print("\033[31mError!\033[0m File size does not match expected size.")
        generate_separator("", "*")
        return False, None

    raw_image = np.fromfile(file_name, dtype=data_type).reshape((height, width))
    return True, raw_image
