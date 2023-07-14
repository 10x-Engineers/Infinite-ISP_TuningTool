"""
File: generate_h_file.py
Description: This file will create .h file.
Author: 10xEngineers
------------------------------------------------------------
"""
from src.utils.read_yaml_file import ReadWriteYMLFile
from src.utils.create_h_file.create_h_data import CreateHFileData


class GenerateHFile:
    """
    Generate H File
    """

    def __init__(self, in_config_file, version):
        self.version = version
        self.in_config_file = in_config_file
        self.h_file = CreateHFileData(in_config_file)
        self.update_h_file_data()

    def update_h_file_data(self):
        """
        Read data from the config file and update the h_file data.
        """
        read_file = ReadWriteYMLFile(self.in_config_file)

        # Update the dpc data
        self.h_file.update_dpc(read_file.get_dpc_data())

        # Update the blc data
        self.h_file.update_blc(read_file.get_blc_data(), read_file.get_blc_sat_data())

        # Update oecf data
        self.h_file.update_oecf(read_file.get_oecf_data())

        # Update dgain data
        self.h_file.update_dgain(read_file.get_dgain_data())

        # Update bnr data
        self.h_file.update_bnr(read_file.get_bnr_data(), read_file.get_bits_depth())
        # Update awb data
        self.h_file.update_awb(read_file.get_awb_data())

        # Update wb data
        self.h_file.update_wb(read_file.get_wb_data())

        # Update ccm data
        self.h_file.update_ccm(read_file.get_ccm_data())

        # Update gamma data
        self.h_file.update_gamma(read_file.get_gamma_correction())

        # Update ae data
        self.h_file.update_ae(read_file.get_ae_data())

        # Update csc data
        self.h_file.update_csc(read_file.get_csc_data())

        # Update 2dnr data
        self.h_file.update_2dnr(read_file.get_2dnr_data())

        # Get ISP modules states
        isp_modules_state = self.get_isp_modules_states(read_file)
        self.h_file.update_isp_modules_state(isp_modules_state)

        # Get VIP modules states
        vip_modules_state = self.get_vip_modules_states(read_file)
        self.h_file.update_vip_modules_state(vip_modules_state)

        # Update rgbc data
        self.h_file.update_rgbc(read_file.get_csc_data())

        # Update yuv_conv data
        self.h_file.update_yuv_conv(read_file.get_yuv_conv_data())

        # Get data for IRC module
        irc_data = self.get_irc_module_data(read_file)
        self.h_file.update_irc(irc_data)

    def get_irc_module_data(self, read_file):
        """
        Get the irc data using by adding folowing offset and border
        for each module.
        DPC = 2, BNR= 6, CFA= 2, 2DNR= 4
        """

        offset = 0

        dpc_en = read_file.get_module_state("dead_pixel_correction")
        bnr_en = read_file.get_module_state("bayer_noise_reduction")
        nr2d_en = read_file.get_module_state("2d_noise_reduction")

        # CFA is enabled by-default
        cfa_en = 1

        if cfa_en:
            offset = offset + 2

        if dpc_en:
            offset = offset + 2

        if bnr_en:
            offset = offset + 6

        if nr2d_en:
            offset = offset + 4

        width_idx, height_idx = read_file.get_irc_data()

        height_idx = height_idx + offset

        return (width_idx, height_idx)

    def get_isp_modules_states(self, read_file):
        """
        This function returns enable / disable state of isp modules.
        """

        modules_name = [
            "crop",
            "dead_pixel_correction",
            "black_level_correction",
            "oecf",
            "bayer_noise_reduction",
            "white_balance",
            "color_correction_matrix",
            "gamma_correction",
            "2d_noise_reduction",
            "auto_white_balance",
            "auto_exposure",
        ]
        module_state = []
        for module in modules_name:
            state = read_file.get_module_state(module)
            module_state.append(self.set_01_state(state))

        # Get and append is_linear state of the BLC
        state = read_file.get_blc_linear_state()
        module_state.append(self.set_01_state(state))

        return module_state

    def get_vip_modules_states(self, read_file):
        """
        This function returns enable / disable state of vip modules.
        """
        modules_name = [
            "rgb_conversion",
            "invalid_region_crop",
            "scale",
            "yuv_conversion_format",
        ]
        module_state = []
        for module in modules_name:
            state = read_file.get_module_state(module)
            module_state.append(self.set_01_state(state))

        return module_state

    def set_01_state(self, state):
        """
        This function is used to replace the True with 1
        and False with 0.
        """

        if state:
            return 1
        else:
            return 0

    def write_to_h_file(self, h_file):
        """
        Writing h_data to .h file
        """

        with open(h_file, "w") as h_file:
            # Write the header of the .h file
            h_file.write("#ifndef __ISP_INIT_H__\n#define __ISP_INIT_H__\n")

            # Write commend of the ISP enable / disable variables
            h_file.write("\n// ISP Block Enable/Disable\n")

            # Write ISP enable / disable variables
            for key, value in self.h_file.isp_en_disable_data.items():
                line = "#define {: <20}{: <20}\n".format(key, value)
                h_file.write(line)

            # Write commend of the VIP enable / disable variables
            h_file.write("\n// VIP Block Enable/Disable\n")

            # Write VIP enable / disable variables
            for key, value in self.h_file.vip_en_disable_data.items():
                line = "#define {: <20}{: <20}\n".format(key, value)
                h_file.write(line)

            for key1, _ in self.h_file.h_data.items():
                h_file.write(f"\n// {key1} \n")

                for key, value in self.h_file.h_data[key1].items():
                    if key == "comment":
                        h_file.write(f"{value}\n")

                    elif key1 == "CCM":
                        h_file.write(f"const signed int {key} = {value};\n")

                    else:
                        h_file.write(f"const unsigned int {key} = {value};\n")

            h_file.write("\n#endif\n")
