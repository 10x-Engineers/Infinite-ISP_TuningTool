"""
File: noise_reduction_2d_module.py
Description: Executes the module flow with the algorithm for the luma noise estimation
Author: 10xEngineers
------------------------------------------------------------
"""
from src.modules.NR.noise_reduction_2d_algo import NEAlgo
from src.modules.WB.white_balance_algo import WhiteBalanceAlgo as wb
from src.utils.algo_common_utils import select_image_and_get_para, generate_separator
from src.utils.area_selection_frame import SelectAreaFrame as select_area_frame


class NEModule:
    """
    Luminance Noise Estimation Module
    """

    def __init__(self):
        self.raw_image_para = None
        self.selection_frame = None

    def is_image_and_para_loaded(self):
        """
        To check if the image is loaded, if true store respective parameters.
        """
        file_type = (
            ("RAW Files (*.raw)", "*.raw"),
            (
                "PNG, JPEG, JPG Files (*.png, *.jpeg, *.jpg)",
                ("*.png", "*.jpeg", "*.jpg"),
            ),
            ("All Files (*.*)", ("*.raw", "*.png", "*.jpeg", "*.jpg")),
        )
        is_selected, self.raw_image_para = select_image_and_get_para(file_type)

        return is_selected, self.raw_image_para

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

    def implement_ne_algo(self, status):
        """
        Extract patches and apply algorithm on the image
        to estimate luma noise levels.
        """
        sub_rect_points = self.selection_frame.get_sub_rect_points()

        if status == "1":
            wb_obj = wb(self.raw_image_para.rgb_image, sub_rect_points)
            self.raw_image_para.rgb_image = wb_obj.execute()
        noise_est = NEAlgo(self.raw_image_para.rgb_image, sub_rect_points)
        noise_est.apply_algo()
        generate_separator("Noise Levels Estimated Successfully!", "-")
        generate_separator("", "*")
