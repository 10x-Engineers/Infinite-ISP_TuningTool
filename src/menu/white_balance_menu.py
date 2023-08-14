"""
File: white_balance_menu.py
Description: Executes the menu flow for the white balance module
Author: 10xEngineers
------------------------------------------------------------
"""
import os
from src.modules.WB.wb_module import WhiteBalanceModule as WBModule
from src.menu.menu_common_func import (
    area_selection_error,
    back_to_tuning_tool_message,
    print_and_select_menu,
    get_main_menu_options,
    end_tuning_tool,
)
from src.utils.gui_common_utils import generate_separator, menu_title


class WhiteBalanceMenu:
    """
    White Balance Menu
    """

    # Options for applying wb
    apply_save_wb_menu_options = [
        "Apply White Balance on the Input Image",
        "Save config.yml with the Calculated WB Gains",
        "Restart the White Balance Tool",
        "Return to the Main Menu",
        "Quit\n",
    ]

    # Options for open area selection frame
    selection_frame_menu_options = [
        "Open ColorChecker Selection Frame",
        "Return to the Main Menu.",
        "Quit\n",
    ]

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file

        # Define object of white balance module
        self.wb_module = WBModule(in_config_file)

    def start_menu(self):
        """
        Start menu for module
        """

        # clean console
        os.system("cls")

        # Welcome note
        self.welcome_to_wb()

        while True:
            # Display main menu
            choice = print_and_select_menu(get_main_menu_options())

            if choice == "1":
                # Get raw image and its parameters.
                image_loaded = self.wb_module.is_image_and_para_loaded()
                if not image_loaded:
                    continue

                # Allow user to select color checker patches. If patches
                # are not selected or saved then display another menu for
                # area selection agian.
                is_selection_done = self.wb_module.color_checker_selection_frame()
                if not is_selection_done:
                    area_selection_error()
                    selection_status = self.start_frame_selection_menu()

                    if selection_status == "1":
                        back_to_tuning_tool_message()
                        break

                # Calculate wb.
                self.wb_module.implement_wb_algo()
                generate_separator("", "*")

                apply_menu_status = ""
                while True:
                    # Menu to apply calculated white balance on the input image.
                    apply_menu_status = self.start_apply_save_wb_menu()
                    if (apply_menu_status == "Apply_wb_done") or (
                        apply_menu_status == "Save_conf_done"
                    ):
                        continue

                    else:
                        break

                if apply_menu_status == "Tuning_tool":
                    # Go back to tuning tool.
                    back_to_tuning_tool_message()
                    break

                elif apply_menu_status == "Restart_wb":
                    # Restart color checker white balance tool.
                    os.system("cls")
                    self.welcome_to_wb()
                    continue

            elif choice == "2":
                back_to_tuning_tool_message()
                break

            elif choice == "3":
                end_tuning_tool()

    def welcome_to_wb(self):
        """
        Welcome note at the start of ccm
        """
        os.system("cls")
        menu_title("Welcome to the \033[33mWhite Balance Tool \033[0m ")
        print("Raw file name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: ColorChecker_2592x1536_12bits_RGGB.raw\n")

    def start_frame_selection_menu(self):
        """
        Menu to open area selection frame
        """

        while True:
            choice = print_and_select_menu(self.selection_frame_menu_options)

            if choice == "1":
                is_selection_done = self.wb_module.color_checker_selection_frame()
                if not is_selection_done:
                    area_selection_error()
                    continue
                return

            elif choice == "2":
                return "1"

            elif choice == "3":
                end_tuning_tool()

    def start_apply_save_wb_menu(self):
        """
        Menu to apply wb on the input image
        """

        while True:
            choice = print_and_select_menu(self.apply_save_wb_menu_options)

            if choice == "1":
                self.wb_module.apply_cal_wb_gain()
                self.wb_module.in_out_images_display()
                generate_separator("", "*")

                return "Apply_wb_done"

            elif choice == "2":
                self.wb_module.save_wb_config_file()
                return "Save_conf_done"

            elif choice == "3":
                return "Restart_wb"

            elif choice == "4":
                return "Tuning_tool"

            elif choice == "5":
                end_tuning_tool()
