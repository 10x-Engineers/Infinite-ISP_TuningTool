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


class ReadWriteYMLFile:
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

    def get_sensor_info(self):
        """
        Get sensor info data
        """
        sensor_info = self.c_yaml["sensor_info"]
        bpp = sensor_info["bit_depth"]
        bayer = sensor_info["bayer_pattern"]
        width = sensor_info["width"]
        height = sensor_info["height"]
        return (bpp, bayer, width, height)

    def get_dpc_data(self):
        """
        Get dpc data
        """
        parm_dpc = self.c_yaml["dead_pixel_correction"]
        dpc = parm_dpc["dp_threshold"]
        return dpc

    def get_blc_data(self):
        """
        Get blc data
        """
        parm_blc = self.c_yaml["black_level_correction"]
        r_offset = parm_blc["r_offset"]
        gr_offset = parm_blc["gr_offset"]
        gb_offset = parm_blc["gb_offset"]
        b_offset = parm_blc["b_offset"]

        return (r_offset, gr_offset, gb_offset, b_offset)

    def get_blc_sat_data(self):
        """
        Get blc data saturation
        """
        parm_blc = self.c_yaml["black_level_correction"]
        r_sat = parm_blc["r_sat"]
        gr_sat = parm_blc["gr_sat"]
        gb_sat = parm_blc["gb_sat"]
        b_sat = parm_blc["b_sat"]
        is_linear = parm_blc["is_linear"]

        return (r_sat, gr_sat, gb_sat, b_sat, is_linear)

    def get_oecf_data(self):
        """
        Get the OECF LUT
        """
        return self.c_yaml["oecf"]["r_lut"]

    def get_dgain_data(self):
        """
        Get digital gain data
        """
        digi_gain = self.c_yaml["digital_gain"]
        curr_gain = digi_gain["current_gain"]
        ae_feedback = digi_gain["ae_feedback"]
        gain_array = digi_gain["gain_array"]
        is_auto = digi_gain["is_auto"]

        return (curr_gain, ae_feedback, gain_array, is_auto)

    def get_awb_data(self):
        """
        Get AWB data
        """

        awb_data = self.c_yaml["auto_white_balance"]
        under_exp = awb_data["underexposed_percentage"]
        over_exp = awb_data["overexposed_percentage"]

        return (under_exp, over_exp)

    def get_wb_data(self):
        """
        Get WB gains
        """
        wb_gians = self.c_yaml["white_balance"]
        r_gain = wb_gians["r_gain"]
        b_gain = wb_gians["b_gain"]

        return (r_gain, b_gain)

    def get_ccm_data(self):
        """
        Get CCM matrix
        """
        ccm_mat = self.c_yaml["color_correction_matrix"]
        red = ccm_mat["corrected_red"]
        green = ccm_mat["corrected_green"]
        blue = ccm_mat["corrected_blue"]

        return (red, green, blue)

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

    def get_bnr_data(self):
        """
        Get bnr data
        """
        bnr = self.c_yaml["bayer_noise_reduction"]
        return (
            bnr["filter_window"],
            bnr["r_std_dev_s"],
            bnr["r_std_dev_r"],
            bnr["g_std_dev_s"],
            bnr["g_std_dev_r"],
            bnr["b_std_dev_s"],
            bnr["b_std_dev_r"],
        )

    def get_ae_data(self):
        """
        Get AE data
        """
        ae_data = self.c_yaml["auto_exposure"]
        center_illu = ae_data["center_illuminance"]
        hist_skew = ae_data["histogram_skewness"]

        return (center_illu, hist_skew)

    def get_csc_data(self):
        """
        Get CSC data
        """
        return self.c_yaml["color_space_conversion"]["conv_standard"]

    def get_2dnr_data(self):
        """
        Get 2DNR data
        """
        nr_data = self.c_yaml["2d_noise_reduction"]
        window_size = nr_data["window_size"]
        wts = nr_data["wts"]

        return (window_size, wts)

    def get_module_state(self, module):
        """
        Return the enable/disable state of the given module.
        """
        return self.c_yaml[module]["is_enable"]

    def get_yuv_conv_data(self):
        """
        Get YUV conv. data
        """
        return self.c_yaml["yuv_conversion_format"]["conv_type"]

    def get_blc_linear_state(self):
        """
        Return the state of is_linear in blc module.
        """

        return self.c_yaml["black_level_correction"]["is_linear"]

    def get_irc_data(self):
        """
        Return the height and width index
        """

        return (
            self.c_yaml["invalid_region_crop"]["width_start_idx"],
            self.c_yaml["invalid_region_crop"]["height_start_idx"],
        )

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

        # self.c_yaml["white_balance"] = parm_wbc

    def set_sensor_info(self, bpp, bayer, width, height):
        """
        Set the sensor info of user choice
        """
        sensor_info = self.c_yaml["sensor_info"]
        sensor_info["bit_depth"] = bpp
        sensor_info["bayer_pattern"] = bayer
        sensor_info["width"] = width
        sensor_info["height"] = height

        self.c_yaml["sensor_info"] = sensor_info

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
