"""
File: ccm_module.py
Description: Executes the CCM module flow with the algorithm
Author: 10xEngineers
------------------------------------------------------------
"""
import os
from src.utils.algo_common_utils import select_image_and_get_para
from src.utils.gui_common_utils import get_config_out_file, generate_separator
from src.utils.area_selection_frame import SelectAreaFrame as select_area_frame
from src.utils.read_yaml_file import ReadYMLFile
from src.modules.CCM.ccm_algo import ColorCorrectionMatrixAlgo as CcmAlgo


class ColorCorrectionMatrixModule:
    """
    CCM Module
    """

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.raw_image_para = None
        self.maintain_wb = True
        self.selection_frame = None
        self.is_delta_e = True
        self.ccm_algo = None

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

        return is_selected

    def color_checker_selection_frame(self):
        """
        Open the color checker patches selection frame and return
        true if patches are drawn and saved using continue button
        otherwise return false
        """
        self.selection_frame = select_area_frame(self.raw_image_para.rgb_image)

        if self.selection_frame.data.is_data_saved:
            return True
        return False

    def set_algo_type(self, algo_type):
        """
        Set the algorithm type, existing algorithms are
        1) DeltaCab 2) DeltaEab
        """
        self.is_delta_e = algo_type

    def enable_wb(self, status):
        """
        Set status of wb
        """
        self.maintain_wb = status

    def start_algo(self):
        """
        Start the ccm algorithm for which first get and set the
        required parameters and then implement algo.
        """
        self.ccm_algo = CcmAlgo()
        self.ccm_algo.set_parameters(
            self.selection_frame.get_sub_rect_points(),
            self.raw_image_para.rgb_image,
            self.is_delta_e,
            self.maintain_wb,
        )
        generate_separator("Algorithm is running", "-")
        self.ccm_algo.execute_algo()
        generate_separator("Process completed", "-")

    def save_ccm_config_file(self):
        """
        Save the configuration file with calculated ccm data.
        """
        out_file_path = get_config_out_file(self.in_config_file)

        if not out_file_path:
            return

        ccm_data = self.ccm_algo.get_ccm_matrix()
        yaml_file = ReadYMLFile(self.in_config_file)
        yaml_file.set_ccm_data(
            corrected_red=ccm_data[0],
            corrected_green=ccm_data[1],
            corrected_blue=ccm_data[2],
        )
        yaml_file.save_file(out_file_path)

        # Get the directory name using the file name.
        print("File saved at:", os.path.dirname(out_file_path))
        generate_separator("", "*")
