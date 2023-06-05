"""
File: create_yaml_file.py
Description: This file will read a yaml file.
Author: 10xEngineers
------------------------------------------------------------
"""
import yaml


class CustomDumper(yaml.Dumper):
    """
    Custom Dumper
    """

    def increase_indent(self, flow=False, indentless=False):
        return super(CustomDumper, self).increase_indent(flow, False)

    def write_line_break(self, data=None):
        super().write_line_break(data)
        if len(self.indents) == 1:
            self.stream.write("\n")


def represent_list(self, data):
    """
    Represent list
    """
    return self.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)


yaml.add_representer(list, represent_list, Dumper=CustomDumper)


class ReadYMLFile:
    """
    Read YAML File
    """

    def __init__(self, config_path):
        with open(config_path, "r", encoding="utf-8") as fil:
            self.c_yaml = yaml.safe_load(fil)

    def get_bits_depth(self):
        """
        Get bit depth data
        """
        sensor_info = self.c_yaml["sensor_info"]
        bpp = sensor_info["bit_depth"]
        return bpp

    def get_platform(self):
        """
        Get platform data
        """
        # Extract workspace info
        platform = self.c_yaml["platform"]
        raw_file = platform["filename"]
        progress_bar = platform["disable_progress_bar"]
        pbar_string = platform["leave_pbar_string"]
        return (raw_file, progress_bar, pbar_string)

    def get_sensor_info(self):
        """
        Get sensor data
        """
        # Extract basic sensor info
        sensor_info = self.c_yaml["sensor_info"]
        bit_range = sensor_info["range"]
        bayer = sensor_info["bayer_pattern"]
        width = sensor_info["width"]
        height = sensor_info["height"]
        bpp = sensor_info["bitdep"]

        return (bit_range, bayer, width, height, bpp)

    def get_gamma_correction(self):
        """
        Get gamma data
        """
        # Extract gamma LUTs
        gamma_corr = self.c_yaml["gamma_correction"]
        gamma_lut8 = gamma_corr["gamma_lut_8"]
        gamma_lut10 = gamma_corr["gamma_lut_10"]
        gamma_lut12 = gamma_corr["gamma_lut_12"]
        gamma_lut14 = gamma_corr["gamma_lut_14"]

        return (gamma_lut8, gamma_lut10, gamma_lut12, gamma_lut14)

    def set_blc_data(self, r_offset=200, gr_offset=200, gb_offset=200, b_offset=200):
        """
        Save the calculated black levels
        """
        parm_blc = self.c_yaml["black_level_correction"]
        parm_blc["r_offset"] = r_offset
        parm_blc["gr_offset"] = gr_offset
        parm_blc["gb_offset"] = gb_offset
        parm_blc["b_offset"] = b_offset

        self.c_yaml["black_level_correction"] = parm_blc

    def set_wb_data(self, r_gain, b_gain):
        """
        Save the calculated white balance gains
        """
        parm_wbc = self.c_yaml["white_balance"]
        parm_wbc["r_gain"] = r_gain
        parm_wbc["b_gain"] = b_gain

        self.c_yaml["white_balance"] = parm_wbc

    def set_ccm_data(
        self,
        corrected_red=[1.660, -0.527, -0.133],
        corrected_green=[-0.408, 1.563, -0.082],
        corrected_blue=[-0.055, -1.641, 2.695],
    ):
        """
        Save the calculated color correction matrix
        """
        parm_ccm = self.c_yaml["color_correction_matrix"]
        parm_ccm["corrected_red"] = corrected_red
        parm_ccm["corrected_green"] = corrected_green
        parm_ccm["corrected_blue"] = corrected_blue

        self.c_yaml["color_correction_matrix"] = parm_ccm

    def save_file(self, out_file):
        """
        Save file
        """
        # file_name = "test_config.yml"
        with open(out_file, "w", encoding="utf-8") as fil:
            yaml.dump(
                self.c_yaml,
                fil,
                sort_keys=False,
                default_flow_style=False,
                Dumper=CustomDumper,
                width=170000,
            )
