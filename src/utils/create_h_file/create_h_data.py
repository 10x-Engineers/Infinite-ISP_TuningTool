"""
File: create_h_data.py
Description: This file will create list of parameters that are used to generate h file.
Author: 10xEngineers
---------------------------------------------------------------------------------------
"""
import warnings
import yaml
import numpy as np


class CreateHFileData:
    """
    This class will create data to generate .h file.
    """

    def __init__(self, config_path):
        with open(config_path, "r", encoding="utf-8") as fil:
            self.c_yaml = yaml.safe_load(fil)

        # Defined the ISP enable / disable parameters. The one which are independent
        # from the configs file are hardcoded.

        self.isp_en_disable_data = {
            "CROP_EN": None,
            "DPC_EN": None,
            "BLC_EN": None,
            "BLC_LINEAR_EN": None,
            "OECF_EN": None,
            "DGAIN_EN": 1,
            "BNR_EN": None,
            "WB_EN": None,
            "CFA_EN": 1,
            "CCM_EN": None,
            "GAMMA_EN": None,
            "CSC_EN": 1,
            "NR2D_EN": None,
            "AWB_EN": None,
            "AE_EN": None,
        }

        self.vip_en_disable_data = {
            "RGBC_EN": None,
            "IRC_EN": None,
            "SCALE_EN": None,
            "OSD_EN": 1,
            "YUV_CONV_FMT_EN": None,
        }

        self.h_data = {
            "DPC": {"dp_threshold": None},
            "CROP": {"comment": "// No register setting required. Crop "
                                "parameters were fixed at 2048x1536 in the design."},
            "BLC": {
                "r_offset": None,
                "gr_offset": None,
                "gb_offset": None,
                "b_offset": None,
                "linear_r": None,
                "linear_gr": None,
                "linear_gb": None,
                "linear_b": None,
            },
            "OECF": {"oecf_table[]": None},
            "DGAIN": {
                "gain_array[]": None,
                "current_gain": None,
                "DGAIN_isManual": None,
            },
            "BNR": {
                "bnr_sk_r[]": None,
                "bnr_sk_g[]": None,
                "bnr_sk_b[]": None,
                "bnr_cc_xr[]": None,
                "bnr_cc_yr[]": None,
                "bnr_cc_xg[]": None,
                "bnr_cc_yg[]": None,
                "bnr_cc_xb[]": None,
                "bnr_cc_yb[]": None,
            },
            "WB": {"r_gain": None, "b_gain": None},
            "CFA": {"comment": "// No parameters required."},
            "CCM": {
                "corrected_red[]": None,
                "corrected_green[]": None,
                "corrected_blue[]": None,
            },
            "GAMMA": {
                "gamma_lut_8[]": None,
                "gamma_lut_10[]": None,
                "gamma_lut_12[]": None,
                "gamma_lut_14[]": None,
            },
            "CSC": {"csc_conv_standard": None},
            "2DNR": {"nr2d_diff[]": None, "nr2d_weight[]": None},
            "AWB": {"underexposed_percentage": None, "overexposed_percentage": None},
            "AE": {
                "center_illuminance": None,
                "histogram_skewnes": None,
            },
            "VIP": {},
            "RGBC": {"rgbc_conv_standard": None},
            "IRC": {
                "height_start_idx": None,
                "width_start_idx": None,
            },
            "SCALE":{
                "comment": "// No register setting required. All "
                           "parameters were fixed at 1920x1080 in the design.",
            },
            "YUV444TO422": {"comment": "// 444 --> 0, 422 --> 1",
                "yuv_444_to_422": None},
        }

    def update_dpc(self, dpc):
        """
        Update the dpc data
        """
        self.h_data["DPC"]["dp_threshold"] = dpc

    def update_blc(self, black_levels, sat_levels):
        """
        Update the blc data
        """

        self.h_data["BLC"]["r_offset"] = black_levels[0]
        self.h_data["BLC"]["gr_offset"] = black_levels[1]
        self.h_data["BLC"]["gb_offset"] = black_levels[2]
        self.h_data["BLC"]["b_offset"] = black_levels[3]
        self.h_data["BLC"]["linear_r"] = self.sat_to_hex(sat_levels[0], black_levels[0])
        self.h_data["BLC"]["linear_gr"] = self.sat_to_hex(sat_levels[1], black_levels[1])
        self.h_data["BLC"]["linear_gb"] = self.sat_to_hex(sat_levels[2], black_levels[2])
        self.h_data["BLC"]["linear_b"] = self.sat_to_hex(sat_levels[3], black_levels[3])

    def sat_to_hex(self, sat, blc):
        """
        Convert saturation value to hexadecimal
        """
        # Converting number into hexadecimal
        number = (hex(int(sat * np.power(2, 14) / (sat - blc)))).upper()
        # Selecting 16 most significant digits
        return number[:16]

    def update_oecf(self, oecf):
        """
        Update the oecf data
        """
        self.h_data["OECF"]["oecf_table[]"] = (
            str(oecf).replace("[", "{").replace("]", "}")
        )

    def update_dgain(self, dgain):
        """
        Update the DG data, hardcoded the DGAIN_isManual equal to 0
        """
        gain_array = str(dgain[2]).replace("[", "{").replace("]", "}")
        self.h_data["DGAIN"]["gain_array[]"] = gain_array
        self.h_data["DGAIN"]["current_gain"] = dgain[0]
        if dgain[3]:
            self.h_data["DGAIN"]["DGAIN_isManual"] = 0
        else:
            self.h_data["DGAIN"]["DGAIN_isManual"] = 1

    def update_bnr(self, bnr, bpp):
        """
        Get BNR parameters from config and process them to
        generate LUT
        """
        # Getting filter size for processing
        spatial_kern = int((bnr[0] + 1) / 2)

        # Getting spatial kernel using gauss function
        s_kern_r = self.gauss_kern_raw(spatial_kern, bnr[1], 2)
        self.h_data["BNR"]["bnr_sk_r[]"] = self.rtl_array(s_kern_r)

        s_kern_g = self.gauss_kern_raw(spatial_kern, bnr[3], 1)
        self.h_data["BNR"]["bnr_sk_g[]"] = self.rtl_array(s_kern_g)

        s_kern_b = self.gauss_kern_raw(spatial_kern, bnr[5], 2)
        self.h_data["BNR"]["bnr_sk_b[]"] = self.rtl_array(s_kern_b)

        # Creating range curves
        curve_r = self.x_bf_make_color_curve(
            9, 2 * bnr[2] * (2**bpp - 1), bnr[2] * (2**bpp - 1), 255
        )  # 255 is the scaling factor
        self.h_data["BNR"]["bnr_cc_xr[]"] = self.rtl_array(curve_r[:, 0])
        self.h_data["BNR"]["bnr_cc_yr[]"] = self.rtl_array(curve_r[:, 1])

        curve_g = self.x_bf_make_color_curve(
            9, 2 * bnr[4] * (2**bpp - 1), bnr[4] * (2**bpp - 1), 255
        )  # 255 is the scaling factor
        self.h_data["BNR"]["bnr_cc_xg[]"] = self.rtl_array(curve_g[:, 0])
        self.h_data["BNR"]["bnr_cc_yg[]"] = self.rtl_array(curve_g[:, 1])

        curve_b = self.x_bf_make_color_curve(
            9, 2 * bnr[6] * (2**bpp - 1), bnr[6] * (2**bpp - 1), 255
        )  # 255 is the scaling factor
        self.h_data["BNR"]["bnr_cc_xb[]"] = self.rtl_array(curve_b[:, 0])
        self.h_data["BNR"]["bnr_cc_yb[]"] = self.rtl_array(curve_b[:, 1])

    def update_awb(self, awb):
        """
        Update AWB data
        """
        self.h_data["AWB"]["underexposed_percentage"] = awb[0]
        self.h_data["AWB"]["overexposed_percentage"] = awb[1]

    def update_ccm(self, ccm):
        """
        Update CCM data
        """
        c_r = str(ccm[0]).replace("[", "{").replace("]", "}")
        c_g = str(ccm[1]).replace("[", "{").replace("]", "}")
        c_b = str(ccm[2]).replace("[", "{").replace("]", "}")

        self.h_data["CCM"]["corrected_red[]"] = c_r
        self.h_data["CCM"]["corrected_green[]"] = c_g
        self.h_data["CCM"]["corrected_blue[]"] = c_b

    def update_gamma(self, gamma):
        """
        Update gamma data
        """
        gamma8 = str(gamma[0]).replace("[", "{").replace("]", "}")
        gamma10 = str(gamma[1]).replace("[", "{").replace("]", "}")
        gamma12 = str(gamma[2]).replace("[", "{").replace("]", "}")
        gamma14 = str(gamma[3]).replace("[", "{").replace("]", "}")

        self.h_data["GAMMA"]["gamma_lut_8[]"] = gamma8
        self.h_data["GAMMA"]["gamma_lut_10[]"] = gamma10
        self.h_data["GAMMA"]["gamma_lut_12[]"] = gamma12
        self.h_data["GAMMA"]["gamma_lut_14[]"] = gamma14

    def update_wb(self, wbgain):
        """
        Update wb data
        """
        self.h_data["WB"]["r_gain"] = int(np.floor(wbgain[0] * 256))
        self.h_data["WB"]["b_gain"] = int(np.floor(wbgain[1] * 256))

    def update_2dnr(self, dnr):
        """
        Update 2dnr data
        """
        # Creating LUT
        curve_2d = self.make_weighted_curve(32, dnr[1])

        # Generating exact format needed in .h file that is to add commas
        # between each entry of the row and replacing [] with {}
        self.h_data["2DNR"]["nr2d_diff[]"] = self.rtl_array(curve_2d[:, 0])
        self.h_data["2DNR"]["nr2d_weight[]"] = self.rtl_array(curve_2d[:, 1])

    def update_csc(self, csc):
        """
        Update csc data
        """
        self.h_data["CSC"]["csc_conv_standard"] = csc

    def update_ae(self, ae_par):
        """
        Update ae data
        """
        self.h_data["AE"]["center_illuminance"] = ae_par[0]
        self.h_data["AE"]["histogram_skewnes"] = int(np.floor(ae_par[1] * 256))

    def update_isp_modules_state(self, modules_state):
        """
        This function is used to update the isp_modules
        enable or disable state given in modules_states.
        Status of these moduels is present in given order:
        ["crop","dead_pixel_correction", "black_level_correction", "oecf",
        "bayer_noise_reduction", "white_balance", "color_correction_matrix",
        "gamma_correction", "2d_noise_reduction", "auto_white_balance", "auto_exposure",
        "blc_is_linear"]

        """
        self.isp_en_disable_data["CROP_EN"] = modules_state[0]
        self.isp_en_disable_data["DPC_EN"] = modules_state[1]
        self.isp_en_disable_data["BLC_EN"] = modules_state[2]
        self.isp_en_disable_data["OECF_EN"] = modules_state[3]
        self.isp_en_disable_data["BNR_EN"] = modules_state[4]
        self.isp_en_disable_data["WB_EN"] = modules_state[5]
        self.isp_en_disable_data["CCM_EN"] = modules_state[6]
        self.isp_en_disable_data["GAMMA_EN"] = modules_state[7]
        self.isp_en_disable_data["NR2D_EN"] = modules_state[8]
        self.isp_en_disable_data["AWB_EN"] = modules_state[9]
        self.isp_en_disable_data["AE_EN"] = modules_state[10]
        self.isp_en_disable_data["BLC_LINEAR_EN"] = modules_state[11]

    def update_vip_modules_state(self, modules_state):
        """
        This function is used to update the vip_modules
        enable or disable state given in modules_states.
        Status of these moduels is present in given order:
        ["rgb_conversion", "invalid_region_crop", "scale",
        "yuv_conversion_format"]

        """
        self.vip_en_disable_data["RGBC_EN"] = modules_state[0]
        self.vip_en_disable_data["IRC_EN"] = modules_state[1]
        self.vip_en_disable_data["SCALE_EN"] = modules_state[2]
        self.vip_en_disable_data["YUV_CONV_FMT_EN"] = modules_state[3]

    def update_rgbc(self, rgbc):
        """
        Update rgbc data
        """
        self.h_data["RGBC"]["rgbc_conv_standard"] = rgbc

    def update_yuv_conv(self, yuv_conv):
        """
        Update the yuv conv. data
        """
        # 444 --> 0, 422 --> 1
        if yuv_conv == "444":
            self.h_data["YUV444TO422"]["yuv_444_to_422"] = 1
        else:
            self.h_data["YUV444TO422"]["yuv_444_to_422"] = 0

    def update_irc(self, irc_data):
        """
        Updated the irc module
        """
        self.h_data["IRC"]["height_start_idx"] = irc_data[1]
        self.h_data["IRC"]["width_start_idx"] = irc_data[0]

    def rtl_array(self, array):
        """
        This function converts python arrays to
        RTL compatible arrays
        """
        # Generating exact format needed in .h file that is to add commas
        # between each entry of the row and replacing [] with {}
        final_array = np.array2string(array.flatten(), separator=",")[1:-1]
        final_array = final_array.replace("\n", "")
        final_string = "{" + final_array + "}"
        return final_string

    def x_bf_make_color_curve(self, n_ind, max_diff, sigma_color, factor):
        """
        Generating Look-up-table based on color difference
        """
        # Create an empty 2D array to store the curve values
        curve = np.zeros((n_ind, 2), np.int16)

        # Iterate over the indices
        for i in range(n_ind):
            # Calculate the color difference based on the index
            diff = max_diff * (i + 1) // (n_ind + 1)

            # Assign the color difference value to the first column
            # of the curve array
            curve[i, 0] = diff

            # Calculate the corresponding value based on the color
            # difference using a formula
            curve[i, 1] = np.int16(
                factor * np.exp(-(diff**2) / (2 * sigma_color**2)) + 0.5
            )
        return curve

    def gauss_kern_raw(self, kern, std_dev, stride):
        """
        Creating spatial kernel
        """
        if kern % 2 == 0:
            warnings.warn("kernel size (kern) cannot be even, setting it as odd value")
            kern = kern + 1

        if kern <= 0:
            warnings.warn("kernel size (kern) cannot be <= zero, setting it as 3")
            kern = 3

        out_kern = np.zeros((kern, kern), dtype=np.float32)

        for i in range(0, kern):
            for j in range(0, kern):
                # stride is used to adjust the gaussian weights for neighbourhood
                # pixel that are 'stride' spaces apart in a bayer image
                out_kern[i, j] = np.exp(
                    -1
                    * (
                        (stride * (i - ((kern - 1) / 2))) ** 2
                        + (stride * (j - ((kern - 1) / 2))) ** 2
                    )
                    / (2 * (std_dev**2))
                )
        out_kern = np.uint8(255 * out_kern + 0.5)
        return out_kern

    def make_weighted_curve(self, n_ind, h_par):
        """
        Creating weighting LUT
        """
        curve = np.zeros((n_ind, 2), np.int32)
        diff = np.linspace(0, 255, n_ind)
        # Considering maximum weight to be 31 (5 bit)
        wts = (np.exp(-(diff**2) / h_par**2) * 31).astype(np.int32)
        curve[:, 0] = diff
        curve[:, 1] = wts
        return curve
