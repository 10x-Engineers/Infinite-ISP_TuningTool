"""
File: bnr_module.py
Description: Executes the module flow with the algorithm for the bayer noise estimation
Author: 10xEngineers
------------------------------------------------------------
"""
from src.modules.BNR.bnr_algo import BneAlgo as bne_algo
from src.utils.algo_common_utils import select_image_and_get_para, generate_separator
from src.utils.area_selection_frame import SelectAreaFrame as select_area_frame


class BneModule:
    """
    Bayer Noise Estimation Module
    """

    def __init__(self):
        self.raw_image_para = None
        self.selection_frame = None

    def is_image_and_para_loaded(self):
        """
        To check if the raw image is loaded, if true store respective parameters.
        """
        file_type = (("RAW Files", "*.raw"),)

        is_selected, self.raw_image_para = select_image_and_get_para(file_type)

        return is_selected

    def color_checker_selection_frame(self):
        """
        Open the color checker patches selection frame and return true
        if patches are drawn and saved using continue button otherwise
        return false
        """
        self.selection_frame = select_area_frame(self.raw_image_para.rgb_image)

        if self.selection_frame.data.is_data_saved is False:
            return False
        return True

    def implement_bne_algo(self):
        """
        Extract patches and apply algorithm on the image
        to estimate bayer noise levels.
        """
        # Extracting coordinates for the patches to be used
        # for extracting patches from each channel
        sub_rect_points = self.selection_frame.get_sub_rect_points()

        # Applying Noise Estimation Algorithm
        noise_est = bne_algo(self.raw_image_para, sub_rect_points)
        noise_est.apply_algo()
        generate_separator("Noise Levels Estimated Successfully!", "-")
        generate_separator("", "*")
        return True
