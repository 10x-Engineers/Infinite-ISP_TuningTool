"""
File: black_level_calibration_menu.py
Description: Executes the menu flow for the BLC module
Author: 10xEngineers
------------------------------------------------------------
"""
import os

from src.menu.menu_common_func import (
    back_to_tuning_tool_message,
    end_tuning_tool,
    print_and_select_menu,
    get_main_menu_options,
    get_yes_no_options,
)
from src.utils.read_yaml_file import ReadWriteYMLFile
from src.modules.BLC.blc_module import BlackLevelCalibrationModule as BLCModule
from src.utils.gui_common_utils import generate_separator, menu_title


class BlackLevelCalibrationMenu:
    """
    Black Level Calibration Menu
    """

    start_options = [
        "Calculate Black Levels",
        "Apply Black Levels",
        "Return to the Main Menu",
        "Quit\n",
    ]

    config_file_menu_options = [
        "Save config.yml with Calculated Black Levels",
        "Apply Calculated Black Levels",
        "Restart the Black Level Calculation Tool",
        "Return to the Main Menu",
        "Quit\n",
    ]

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.blc_module = BLCModule(self.in_config_file)

    def start_menu(self):
        """
        Start menu for the module to work
        """
        os.system("cls")

        # Welcome note
        self.welcome_to_blc()
        break_flag = False
        restart_flag = False
        while True:
            # Start menu to apply or calculate BLC
            opt = print_and_select_menu(self.start_options)
            if opt == "1":
                while True:
                    # Loading raw black image for calibration
                    choice = print_and_select_menu(get_main_menu_options())
                    if choice == "1":
                        image_loaded = self.blc_module.is_image_and_para_loaded()
                        if not image_loaded:
                            continue

                        # Start executing the BLC algorithm
                        generate_separator("Calculation Started", "*")
                        black_levels = self.blc_module.execute()
                        generate_separator("Calculation Ended", "*")

                        # Menu to display after calibration
                        break_flag, restart_flag = self.start_config_menu(black_levels)
                        break

                    elif choice == "2":
                        break_flag = True
                        back_to_tuning_tool_message()
                        break

                    elif choice == "3":
                        end_tuning_tool()

                    if break_flag is True or restart_flag is True:
                        break

            elif opt == "2":
                # Get blc levels from config
                yaml_file = ReadWriteYMLFile(self.in_config_file)
                blc_levels = yaml_file.get_blc_data()

                # Applying BLC on raw image
                status, apply_flag = self.start_blc_apply_menu(blc_levels)

                if apply_flag:
                    generate_separator("Black levels from configs.yml are applied", "-")
                    generate_separator("", "*")
                    break_flag, restart_flag = self.apply_restart_menu()
                    break_flag = status
                    break

                if apply_flag is False and status is True:
                    break

            elif opt == "3":
                back_to_tuning_tool_message()
                break

            elif opt == "4":
                end_tuning_tool()

            if break_flag is True or restart_flag is True:
                break

    def start_blc_apply_menu(self, black_levels):
        """
        Menu flow for applying BLC on image
        """
        # Parameters to be updated after loading raw file
        is_linear = False
        while True:
            # Menu option to load an image
            choice = print_and_select_menu(get_main_menu_options())
            if choice == "1":
                # Loading raw image for BLC application
                image_loaded = self.blc_module.is_image_and_para_loaded()
                if not image_loaded:
                    continue

                lin_choice = print_and_select_menu(
                    get_yes_no_options(), message="Do you want to apply linearization?"
                )

                if lin_choice == "1":
                    is_linear = True
                elif lin_choice == "2":
                    is_linear = False

                # Applying BLC on the raw image after setting respective parameters
                self.blc_module.set_blc_para(is_linear)
                status, apply_flag = self.blc_module.apply_blc_levels(black_levels)
                return status, apply_flag

            elif choice == "2":
                back_to_tuning_tool_message()
                return True, False

            elif choice == "3":
                end_tuning_tool()
                return True, False

    def apply_restart_menu(self):
        """
        Start config menu
        """
        restart_flag = False
        break_flag = False
        while True:
            choice = print_and_select_menu(self.config_file_menu_options[2:5])
            if choice == "1":
                self.start_menu()
                restart_flag = True
                return break_flag, restart_flag

            elif choice == "2":
                back_to_tuning_tool_message()
                break_flag = True
                return break_flag, restart_flag

            elif choice == "3":
                end_tuning_tool()
            generate_separator("", "*")

    def start_config_menu(self, black_levels):
        """
        Start config menu
        """
        restart_flag = False
        break_flag = False
        while True:
            choice = print_and_select_menu(self.config_file_menu_options)

            if choice == "1":
                # Saving BLC to the configs.yml file
                self.blc_module.save_config_file_with_calculated_black_level()
                self.start_config_menu(black_levels)
                break_flag = True
                return break_flag, restart_flag

            elif choice == "2":
                # Applying calculated BLC on raw image
                generate_separator("", "*")
                status, apply_flag = self.start_blc_apply_menu(black_levels)
                if apply_flag is True:
                    generate_separator("Calculated black levels are applied", "-")
                    generate_separator("", "*")
                    continue

                if apply_flag is False and status is False:
                    continue

                return break_flag, restart_flag

            elif choice == "3":
                self.start_menu()
                restart_flag = True
                return break_flag, restart_flag

            elif choice == "4":
                back_to_tuning_tool_message()
                break_flag = True
                return break_flag, restart_flag

            elif choice == "5":
                end_tuning_tool()

    def welcome_to_blc(self):
        """
        Display welcome note for module
        """
        menu_title("Welcome to the \033[35mBlack Levels Calibration Tool\033[0m  ")
