"""
File: black_level_calibration_menu.py
Description: Executes the menu flow for the BLC module
Author: 10xEngineers
------------------------------------------------------------
"""
import os
import sys

from src.menu.menu_common_func import (
    get_user_input,
    back_to_tuning_tool_message,
    invalid_choice_message,
    display_main_menu,
)
from src.modules.BLC.blc_module import BlackLevelCalibrationModule as BLCModule
from src.utils.gui_common_utils import generate_separator, menu_title


class BlackLevelCalibrationMenu:
    """
    Black Level Calibration Menu
    """

    config_file_menu_options = {
        "1": "Save config.yml with Calculated Black Levels",
        "2": "Restart the Black Level Calculation Tool",
        "3": "Return to the Main Menu",
        "4": "Quit\n",
    }

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.blc_module = BLCModule(self.in_config_file)

    def display_config_menu(self):
        """
        Display config menu
        """
        print("Select a command:")

        # Display BLC menu commands
        for key, value in self.config_file_menu_options.items():
            print(key + ". " + value)

    def start_config_menu(self, black_levels):
        """
        Start config menu
        """
        self.display_config_menu()
        while True:
            choice = get_user_input()
            if choice == "1":
                self.blc_module.save_config_file_with_calculated_black_level()
                self.start_config_menu(black_levels)
                break
            elif choice == "2":
                self.start_menu()
                break
            elif choice == "3":
                back_to_tuning_tool_message()
                break
            elif choice == "4":
                sys.exit()
            else:
                invalid_choice_message()
                self.display_config_menu()

    def welcome_to_blc(self):
        """
        Display welcome note for module
        """
        # Display BLC title
        menu_title("Welcome to the \033[35mBlack Levels Calculation Tool\033[0m  ")
        print("File name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: BlackImage_2592x1536_12bits_RGGB.raw\n")

    def start_menu(self):
        """
        Start menu for the module
        """
        os.system("cls")
        # Welcome note
        self.welcome_to_blc()
        # Display blc menu
        display_main_menu()

        # Start getting user input
        black_levels = []
        while True:
            choice = get_user_input()
            if choice == "1":
                image_loaded = self.blc_module.is_image_and_para_loaded()
                if not image_loaded:
                    display_main_menu()
                else:
                    generate_separator("Calculation Started", "*")
                    black_levels = self.blc_module.execute()
                    generate_separator("Calculation Ended", "*")
                    if not black_levels:
                        generate_separator("Calculation Ended", "*")
                        display_main_menu()
                        continue
                    self.start_config_menu(black_levels)
                    break
            elif choice == "2":
                back_to_tuning_tool_message()
                break
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                display_main_menu()
