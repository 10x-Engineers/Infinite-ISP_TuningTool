"""
File: blc_module.py
Description: Executes the modular flow for black level calculations
Author: 10xEngineers
------------------------------------------------------------
"""
import os
import numpy as np
from src.utils.algo_common_utils import select_image_and_get_para
from src.utils.gui_common_utils import (
    get_config_out_file,
    generate_separator,
)
from src.utils.read_yaml_file import ReadYMLFile


class BlackLevelCalibrationModule:
    """
    Black Level Calibration Module
    """

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.raw_image_para = None
        self.__r = 0
        self.__gr = 0
        self.__gb = 0
        self.__b = 0

    def is_image_and_para_loaded(self):
        """
        To check if the image is loaded, if true store respective parameters.
        """
        file_type = (("RAW Files", "*.raw"),)
        is_selected, self.raw_image_para = select_image_and_get_para(file_type)

        return is_selected

    def execute(self):
        """
        image_loaded, raw_image = get_raw_image(
        self.raw_image_para.file_name,
        self.raw_image_para.width, self.raw_image_para.height)

        if not image_loaded:
            return False
        """

        self.calculate_blc(self.raw_image_para.raw_image)

        self.display_black_levels()
        return True

    def calculate_blc(self, raw_image):
        """
        There are 3 steps involved in the function.
        1) Separate the four channels.
        2) Calcualte averages of each channel.
        3) Map the averages on the bayer pattern.
        """
        channel_1 = raw_image[0::2, 0::2]
        channel_2 = raw_image[0::2, 1::2]
        channel_3 = raw_image[1::2, 0::2]
        channel_4 = raw_image[1::2, 1::2]

        avg_ch1 = int(np.mean(channel_1))
        avg_ch2 = int(np.mean(channel_2))
        avg_ch3 = int(np.mean(channel_3))
        avg_ch4 = int(np.mean(channel_4))

        bayer_mapping = {
            "RGGB": [avg_ch1, avg_ch2, avg_ch3, avg_ch4],
            "GRBG": [avg_ch2, avg_ch1, avg_ch4, avg_ch3],
            "GBRG": [avg_ch3, avg_ch4, avg_ch1, avg_ch2],
            "BGGR": [avg_ch4, avg_ch3, avg_ch2, avg_ch1],
        }

        self.__r, self.__gr, self.__gb, self.__b = bayer_mapping[
            self.raw_image_para.bayer_pattern
        ]

    def display_black_levels(self):
        """
        Display black levels
        """
        generate_separator("Calibrated black levels", "-")
        print("R Channel  = ", self.__r)
        print("Gr Channel = ", self.__gr)
        print("Gb Channel = ", self.__gb)
        print("B Channel  = ", self.__b, "\n")

    def save_config_file_with_calculated_black_level(self):
        """
        Save Black levels in Config File.
        """
        out_file_path = get_config_out_file(self.in_config_file)

        if not out_file_path:
            return

        # Read the existing file, set the calculated black levels and save the output file.
        yaml_file = ReadYMLFile(self.in_config_file)
        yaml_file.set_blc_data(self.__r, self.__gr, self.__gb, self.__b)
        yaml_file.save_file(out_file_path)

        # Get the directory name using the file name.
        print("File saved at:", os.path.dirname(out_file_path))
        generate_separator("", "*")
