"""
File: white_balance_menu.py
Description: Executes the menu flow for the white balance module
Author: 10xEngineers
------------------------------------------------------------
"""
import sys
import os
from src.modules.WB.wb_module import WhiteBalanceModule as WBModule
from src.menu.menu_common_func import (
    get_user_input,
    area_selection_error,
    invalid_choice_message,
    back_to_tuning_tool_message,
    display_main_menu,
)
from src.utils.gui_common_utils import generate_separator, menu_title


class WhiteBalanceMenu:
    """
    White Balance Menu
    """

    # Options for applying wb
    apply_save_wb_menu_options = {
        "1": "Apply White Balance on the Input Image",
        "2": "Save config.yml with the Calculated WB Gains",
        "3": "Restart the ColorChecker White Balance Tool",
        "4": "Return to the Main Menu",
        "5": "Quit\n",
    }

    # Options for open area selection frame
    selection_frame_menu_options = {
        "1": "Open \033[35mColorChecker Selection Frame\033[0m",
        # "2": "Reload \033[32mRaw Image\033[0m",
        "2": "Return to the Main Menu.",
        "3": "Quit\n",
    }

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
        # Display main menu
        display_main_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                # Get raw image and its parameters.
                image_loaded = self.wb_module.is_image_and_para_loaded()
                if not image_loaded:
                    display_main_menu()
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
                if apply_menu_status == "Restart_wb":
                    # Restart color checker white balance tool.
                    os.system("cls")
                    self.welcome_to_wb()
                    display_main_menu()
                    continue
            if choice == "2":
                back_to_tuning_tool_message()
                break
            if choice == "3":
                sys.exit()
            invalid_choice_message()
            display_main_menu()

    def welcome_to_wb(self):
        """
        Welcome note at the start of ccm
        """
        os.system("cls")
        menu_title("Welcome to the \033[33mColorChecker White Balance Tool \033[0m ")
        print("Raw file name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: ColorChecker_2592x1536_12bits_RGGB.raw\n")

    def display_selection_frame_menu(self):
        """
        Display selection frame menu
        """
        print("Select a command:")

        # Display selection frame menu options
        for key, value in self.selection_frame_menu_options.items():
            print(key + ". " + value)

    def display_apply_save_wb_menu(self):
        """
        Display apply and save wb menu
        """
        print("Select a command:")

        # Display selection frame menu options
        for key, value in self.apply_save_wb_menu_options.items():
            print(key + ". " + value)

    def start_frame_selection_menu(self):
        """
        Menu to open area selection frame
        """
        # Display selection frame menu
        self.display_selection_frame_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                is_selection_done = self.wb_module.color_checker_selection_frame()
                if not is_selection_done:
                    area_selection_error()
                    self.display_selection_frame_menu()
                    continue
                return
            if choice == "2":
                return "1"
            if choice == "3":
                sys.exit()
            invalid_choice_message()
            self.display_selection_frame_menu()

    def start_apply_save_wb_menu(self):
        """
        Menu to apply wb on the input image
        """
        self.display_apply_save_wb_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                self.wb_module.apply_cal_wb_gain()
                self.wb_module.in_out_images_display()
                generate_separator("", "*")
                return "Apply_wb_done"
            if choice == "2":
                self.wb_module.save_wb_config_file()
                return "Save_conf_done"
            if choice == "3":
                return "Restart_wb"
            if choice == "4":
                return "Tuning_tool"
            if choice == "5":
                sys.exit()
            invalid_choice_message()
            self.display_apply_save_wb_menu()
