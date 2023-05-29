"""
File: color_correction_matrix_menu.py
Description: Executes the menu flow for the color correction matrix module
Author: 10xEngineers
------------------------------------------------------------
"""
import sys
import os
from src.modules.CCM.ccm_module import ColorCorrectionMatrixModule as CcmModule
from src.menu.menu_common_func import (
    get_user_input,
    area_selection_error,
    invalid_choice_message,
    back_to_tuning_tool_message,
    display_main_menu,
)
from src.utils.gui_common_utils import menu_title


class ColorCorrectionMatrixMenu:
    """
    Color Correction Matrix Menu
    """

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.ccm_module = CcmModule(in_config_file)

    def start_menu(self):
        """
        Display start menu
        """
        # clean console
        os.system("cls")

        # Welcome note
        self.welcome_to_ccm()

        # Display main menu
        display_main_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                # Return true if image and its parameters are loaded.
                image_loaded = self.ccm_module.is_image_and_para_loaded()
                if not image_loaded:
                    display_main_menu()
                    continue

                # Allow user to select color checker patches. If patches are
                # not selected or saved then display another menu for
                # area selection agian.
                patches_selected = self.ccm_module.color_checker_selection_frame()
                if not patches_selected:
                    area_selection_error()
                    selection_status = self.start_frame_selection_menu()

                    if selection_status == "1":
                        back_to_tuning_tool_message()
                        break

                # Get required parameters compulsory to run algo
                print("\033[32mParameters required for ccm algorithm:\033[0m")

                # Get autogain status
                # self.menu_auto_gain_selection()

                # Get error matrix type
                self.start_algo_selection_menu()

                # Get input on to maintain wb
                self.start_wb_selection_menu()

                # Start ccm algorithm
                self.ccm_module.start_algo()

                # Start config file menu
                res = self.start_config_file_menu()

                if res == "1":
                    break
                if res == "2":
                    return True  # to start ccm again
            elif choice == "2":
                back_to_tuning_tool_message()
                break
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                display_main_menu()

    # Option for open area selection frame
    selection_frame_menu_options = {
        "1": "Open \033[35mColorChecker Selection Frame\033[0m",
        "2": "Return to the Main Menu",
        "3": "Quit\n",
    }

    # Option for auto gain selection
    auto_gain_menu_option = {
        "1": "Enable Auto Gain",
        "2": "Disable Auto Gain",
    }

    # Option for errorr matrix type
    error_matrix_menu_option = {
        "1": chr(0x394) + "C" + " 00",
        "2": chr(0x394) + "E" + " 00",
    }

    # Option to allow user to maintain wb if needed
    wb_menu_option = {
        "1": "Yes",
        "2": "No",
    }

    # Menu options for config file
    config_menu_option = {
        "1": "Save config.yml with Calculated Color Correction Matrix",
        "2": "Restart the Color Correction Matrix Tool",
        "3": "Return to the Main Menu",
        "4": "Quit\n",
    }

    def welcome_to_ccm(self):
        """
        Welcome note for CCM
        """
        os.system("cls")
        menu_title("Welcome to the \033[36mColor Correction Matrix Tool\033[0m ")
        print("Raw file name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: ColorChecker_2592x1536_12bits_RGGB.raw\n")

    def display_config_file_menu(self):
        """
        Display config file menu
        """
        print("Select a command:")

        for key, value in self.config_menu_option.items():
            print(key + ". " + value)

    def display_selection_frame_menu(self):
        """
        Display selection area frame menu
        """
        print("Select a command:")

        # Display selection frame menu options
        for key, value in self.selection_frame_menu_options.items():
            print(key + ". " + value)

    def display_algo_selection_menu(self):
        """
        Algorithm selection menu
        """
        print("Select Error Matrix:")

        for key, value in self.error_matrix_menu_option.items():
            print(key + ". " + value)

    def display_wb_menu(self):
        """
        Dsiplay wb choice menu
        """
        print("Do you want to maintain white balance?:")

        for key, value in self.wb_menu_option.items():
            print(key + ". " + value)

    def start_config_file_menu(self):
        """
        Menu to save config file or chose other options
        """
        print()
        self.display_config_file_menu()
        while True:
            # Add additional space
            print()

            choice = get_user_input()
            if choice == "1":
                self.ccm_module.save_ccm_config_file()
                self.display_config_file_menu()
                continue
            elif choice == "2":
                return "2"
            elif choice == "3":
                back_to_tuning_tool_message()
                return "1"
            elif choice == "4":
                sys.exit()
            else:
                invalid_choice_message()
                self.display_config_file_menu()
                continue

    def start_wb_selection_menu(self):
        """
        Menu to ask your either need to maintaing wb or not.
        """
        print()
        self.display_wb_menu()
        while True:
            # Add additional space
            print()

            choice = get_user_input()
            if choice == "1":
                self.ccm_module.enable_wb(True)
                print("White balance is maintained.")
                break
            elif choice == "2":
                self.ccm_module.enable_wb(False)
                print("White balance is not maintained.")
                break
            else:
                invalid_choice_message()
                self.display_wb_menu()
                continue

    def start_algo_selection_menu(self):
        """
        Menu for auto gain selection
        """
        print()
        self.display_algo_selection_menu()
        while True:
            # Add additional space
            print()

            choice = get_user_input()
            if choice == "1":
                self.ccm_module.set_algo_type(False)
                print(chr(0x394) + "C" + " 00 is selected.")
                break
            elif choice == "2":
                self.ccm_module.set_algo_type(True)
                print(chr(0x394) + "E" + " 00 is selected.")
                break
            else:
                invalid_choice_message()
                self.display_algo_selection_menu()
                continue

    def start_frame_selection_menu(self):
        """
        Menu to open area selection frame
        """
        # Display selection frame menu
        self.display_selection_frame_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                output = self.ccm_module.color_checker_selection_frame()
                if not output:
                    area_selection_error()
                    self.display_selection_frame_menu()
                    continue
                break
            elif choice == "2":
                return "1"
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                self.display_selection_frame_menu()

    def description(self):
        """
        Description of ccm tool.
        """
        print("Please select the ColorChecker image")
