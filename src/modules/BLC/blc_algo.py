"""
File: blc_algo.py
Description: Calculates and apply black levels
Author: 10xEngineers
------------------------------------------------------------
"""
import os
import numpy as np
from fxpmath import Fxp
from src.utils.gui_common_utils import (
    file_saving_path,
    generate_separator,
    pop_up_msg,
)
from src.utils.read_yaml_file import ReadWriteYMLFile


class BlackLevelsAlgo:
    """
    Black Levels Calibration & Application
    """

    def __init__(self, raw_image_para):
        self.raw_image_para = raw_image_para

    def calculate_blc(self):
        """
        There are 3 steps involved in the function.
        1) Separate the four channels.
        2) Calcualte averages of each channel.
        3) Map the averages on the bayer pattern.
        """
        raw_image = self.raw_image_para.raw_image
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

        offset_r, offset_gr, offset_gb, offset_b = bayer_mapping[
            self.raw_image_para.bayer_pattern
        ]

        return (offset_r, offset_gr, offset_gb, offset_b)

    def get_approximate(self, decimal, register_bits, frac_precision_bits):
        """
        Returns Fixed Float Approximation of a decimal
        -- Fxp function from fxpmath library of python is used that takes following inputs:
        decimal : number to be converted to fixed point number
        signed_value : falg to indicate if we need signed fixed point number
        register_bits : bit depth of fixed point number
        frac_precision_bits : bit depth of fractional part of a fixed point number
        """
        fixed_float = Fxp(decimal, False, register_bits, frac_precision_bits)
        return fixed_float(), fixed_float.bin()

    def display_black_levels(self, blc):
        """
        Display black levels
        """
        print("R Channel  = ", blc[0])
        print("Gr Channel = ", blc[1])
        print("Gb Channel = ", blc[2])
        print("B Channel  = ", blc[3], "\n")

    def display_sat_levels(self, sat_levels):
        """
        Display saturation levels
        """
        generate_separator("Applied Saturation Levels", "-")
        print("R Channel  = ", sat_levels[0])
        print("Gr Channel = ", sat_levels[1])
        print("Gb Channel = ", sat_levels[2])
        print("B Channel  = ", sat_levels[3], "\n")

    def apply_blclevels(self, blc_levels, in_config_file, is_linear):
        """
        Applying black levels to the raw image
        """
        bayer_saturation = None
        sat_levels = None
        bayer = self.raw_image_para.bayer_pattern
        bpp = self.raw_image_para.bit_depth
        raw = np.float32(self.raw_image_para.raw_image)

        # Reading black levels
        r_offset = blc_levels[0]
        gr_offset = blc_levels[1]
        gb_offset = blc_levels[2]
        b_offset = blc_levels[3]

        # Get sat values from config if the linearization is true
        if is_linear is True:
            # Reading saturation levels from config
            yaml_file = ReadWriteYMLFile(in_config_file)
            sat_levels = yaml_file.get_blc_sat_data()

            r_sat = sat_levels[0]
            gr_sat = sat_levels[1]
            gb_sat = sat_levels[2]
            b_sat = sat_levels[3]

            ## Get Approximates for Linearization - U16.14 precision
            # print("Approximated Linearization Factor")
            r_linfact, _ = self.get_approximate(
                ((2**bpp) - 1) / (r_sat - r_offset), 16, 14
            )
            gr_linfact, _ = self.get_approximate(
                ((2**bpp) - 1) / (gr_sat - gr_offset), 16, 14
            )
            gb_linfact, _ = self.get_approximate(
                ((2**bpp) - 1) / (gb_sat - gb_offset), 16, 14
            )
            b_linfact, _ = self.get_approximate(
                ((2**bpp) - 1) / (b_sat - b_offset), 16, 14
            )

            bayer_saturation = {
                "rggb": [r_linfact, gr_linfact, gb_linfact, b_linfact],
                "grbg": [gr_linfact, r_linfact, b_linfact, gb_linfact],
                "gbrg": [gb_linfact, b_linfact, r_linfact, gr_linfact],
                "bggr": [b_linfact, gb_linfact, gr_linfact, r_linfact],
            }

        bayer_offsets = {
            "rggb": [r_offset, gr_offset, gb_offset, b_offset],
            "grbg": [gr_offset, r_offset, b_offset, gb_offset],
            "gbrg": [gb_offset, b_offset, r_offset, gr_offset],
            "bggr": [b_offset, gb_offset, gr_offset, r_offset],
        }

        offset_1, offset_2, offset_3, offset_4 = bayer_offsets[bayer.lower()]

        generate_separator("Applied Black Levels", "-")
        self.display_black_levels((r_offset, gr_offset, gb_offset, b_offset))

        raw[0::2, 0::2] = raw[0::2, 0::2] - offset_1
        raw[0::2, 1::2] = raw[0::2, 1::2] - offset_2
        raw[1::2, 0::2] = raw[1::2, 0::2] - offset_3
        raw[1::2, 1::2] = raw[1::2, 1::2] - offset_4

        if is_linear is True:
            self.display_sat_levels(sat_levels)
            sat_1, sat_2, sat_3, sat_4 = bayer_saturation[bayer.lower()]
            raw[0::2, 0::2] = raw[0::2, 0::2] * sat_1
            raw[0::2, 1::2] = raw[0::2, 1::2] * sat_2
            raw[1::2, 0::2] = raw[1::2, 0::2] * sat_3
            raw[1::2, 1::2] = raw[1::2, 1::2] * sat_4

        raw = np.where(raw >= 0, np.floor(raw + 0.5), np.ceil(raw - 0.5))

        raw = np.uint16(np.clip(raw, 0, (2**bpp) - 1))

        # Saving raw file
        def_ext = ".raw"
        file_types = [
            ("Raw Files", "*.raw"),
        ]
        name_fil = "BLC-" + os.path.basename(self.raw_image_para.file_name)
        path = file_saving_path(def_ext, file_types, name_fil)
        if path:
            raw.tofile(path)
            print(f"Raw file saved to:\n {path}")
            return True, True
        else:
            pop_up_msg("File not saved.")
            print("\033[31mWarning!\033[0m File destination path is not selected.")
            return False, False
