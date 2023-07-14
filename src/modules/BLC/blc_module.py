"""
File: blc_module.py
Description: Executes the modular flow for black level calculations
Author: 10xEngineers
------------------------------------------------------------
"""
import os
from src.utils.algo_common_utils import select_image_and_get_para
from src.utils.gui_common_utils import (
    generate_separator,
)
from src.modules.BLC.blc_algo import BlackLevelsAlgo
from src.utils.read_yaml_file import ReadWriteYMLFile


class BlackLevelCalibrationModule:
    """
    Black Level Calibration Module
    """

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file

        self.raw_image_para = None
        self.bayer = None
        self.bit_dep = None
        self.is_linear = False

        self.__r = 0
        self.__gr = 0
        self.__gb = 0
        self.__b = 0

        self.blc_algo = None

    def is_image_and_para_loaded(self):
        """
        To check if the image is loaded, if true store respective parameters.
        """
        file_type = (("RAW Files", "*.raw"),)
        is_selected, self.raw_image_para = select_image_and_get_para(file_type)
        self.blc_algo = BlackLevelsAlgo(self.raw_image_para)
        return is_selected

    def set_blc_para(self, is_linear):
        """
        Set flag status to true if the calculated
        black levels need to be applied
        """
        self.is_linear = is_linear

    def execute(self):
        """
        This function will calculate and return black
        levels.
        """
        self.__r, self.__gr, self.__gb, self.__b = self.blc_algo.calculate_blc()
        generate_separator("Calibrated black levels", "-")
        self.blc_algo.display_black_levels((self.__r, self.__gr, self.__gb, self.__b))

        return (self.__r, self.__gr, self.__gb, self.__b)

    def save_config_file_with_calculated_black_level(self):
        """
        Save Black levels in Config File.
        """

        if not os.path.exists(self.in_config_file):
            # Display a warning message.
            print(
                "\n\033[31mError!\033[0m File configs.yml does "
                'not exist in "app_data" directory.'
            )

            generate_separator("", "*")
            return

        # Read the existing file, set the calculated black levels and save the output file.
        yaml_file = ReadWriteYMLFile(self.in_config_file)
        yaml_file.set_blc_data(self.__r, self.__gr, self.__gb, self.__b)
        yaml_file.save_file(self.in_config_file)

        # Get the directory name using the file name.
        print("File saved at:", os.path.dirname(self.in_config_file))
        generate_separator("", "*")

    def apply_blc_levels(self, blc_levels):
        """
        Applying black levels to the raw image
        """
        status, apply_flag = self.blc_algo.apply_blclevels(
            blc_levels, self.in_config_file, self.is_linear
        )
        generate_separator("", "*")
        return status, apply_flag
