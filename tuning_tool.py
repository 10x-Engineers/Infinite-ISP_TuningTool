"""
File: tuning_tool.py
Description: It is the starting point of the tool.
Author: 10xEngineers
------------------------------------------------------------
"""

import os
import sys
from src.menu.black_level_calibration_menu import BlackLevelCalibrationMenu as BlcMenu
from src.menu.color_correction_matrix_menu import ColorCorrectionMatrixMenu as CcmMenu
from src.menu.gamma_menu import GammaMenu
from src.menu.luma_noise_menu import NEMenu as neMenu
from src.menu.menu_common_func import (
    display_welcome_note,
    get_user_input,
    invalid_choice_message,
)
from src.menu.white_balance_menu import WhiteBalanceMenu as WbMenu
from src.menu.bayer_noise_menu import BNEMenu as bne
from src.utils.algo_common_utils import select_file
from src.utils.gui_common_utils import generate_separator


# -------------------------------Tuning Tool Menu----------------------------#


class TuningTool:
    """
    This is class of the tuning tool which calls differnt modules.
    """

    # Config file menu options
    # Here is applied the color formatting to the text.
    # The escape sequence "\033[36m" is used to set the
    # forground color. There is a particular color against
    # each sequence.

    load_config_menu_options = {"1": "Load a \033[36mYaml file\033[0m.", "2": "Quit\n"}

    # Main menu options
    tuning_tool_menu_options = {
        "1": "Calculate \033[35mBlack Levels\033[0m",
        "2": "Calculate \033[33mColorChecker White Balance\033[0m",
        "3": "Calculate \033[36mColor Correction Matrix\033[0m",
        "4": "Generate \033[35mGamma Curves\033[0m",
        "5": "Estimate \033[33mBayer Noise Levels\033[0m",
        "6": "Estimate \033[36mLuminance Noise Levels\033[0m",
        "7": "Quit\n",
    }

    def __init__(self):
        """
        This is the main and starting point of the tuning tool.
        """
        self.in_config_file = None
        display_welcome_note()

        # Load pipeline configuration YML
        self.load_config()

        while True:
            # Print the main menu of the Tuning Tool on the console.
            self.display_tuning_tool_menu()

            # Get user's input to continue the menu
            choice = get_user_input()

            if choice == "1":
                # Start Black Level Calulation tool
                blc_menu = BlcMenu(self.in_config_file)
                blc_menu.start_menu()

            elif choice == "2":
                # Start ColorChecker White Balance tool
                wb_menu = WbMenu(self.in_config_file)
                wb_menu.start_menu()

            elif choice == "3":
                # Start Color Correction Matrix calculation tool
                while True:
                    # Continue the CCM tool until user either exit or go to main menu
                    ccm_menu = CcmMenu(self.in_config_file)
                    ccm_again = ccm_menu.start_menu()
                    if not ccm_again:
                        break

            elif choice == "4":
                # Start gamma tool
                gamma_module = GammaMenu(self.in_config_file)
                gamma_module.start_menu()

            elif choice == "5":
                # Start Bayer Noise Levels estimation tool
                bne_module = bne()
                bne_module.start_menu()

            elif choice == "6":
                # Start Luma Noise Levels estimation tool
                ne_menu = neMenu()
                ne_menu.start_menu()

            elif choice == "7":
                # Exit the application
                sys.exit()

            else:
                invalid_choice_message()

    def load_config(self):
        """
        At the start of tuning tool. There should be a config.yml file present
        in the config directory. If this file is renamed or removed by the user,
        this function allow user to select a new YAML file.
        """
        config_file_name = "configs.yml"
        config_file_dir = "config"

        # Join file and dir and load file if file exists
        self.in_config_file = os.path.join(
            os.getcwd(), config_file_dir, config_file_name
        )

        # Exist if file exits and continue with main menu of the Tuning Tool.
        if os.path.exists(self.in_config_file):
            return

        # Display a warning message.
        print(
            "\n\033[31mError!\033[0m File config.yml does "
            'not exist in "config" directory.'
        )

        generate_separator("", "*")

        # Display a menu to select a yaml file if file does not exits.
        while True:
            # Print the menu for loading config file
            self.display_load_config_menu()

            # Get user's input
            choice = get_user_input()
            if choice == "1":
                # True if file is loaded
                file_selected = self.handle_custom_config()

                if not file_selected:
                    continue
                else:
                    break

            elif choice == "2":
                sys.exit()

            else:
                invalid_choice_message()

    def display_load_config_menu(self):
        """
        This function displays the menu that allow the user to select and load the config file.
        """
        print("Select a command:")

        for key, value in self.load_config_menu_options.items():
            print(key + ". " + value)

    def handle_custom_config(self):
        """
        Here is pop upped a file selection dialog that
        returns true if file is selected
        """
        title = "Open an image file."
        file_type = (("YAML Files", "*.yml"),)
        file_selected, file_name = select_file(title, file_type)

        if not file_selected:
            print("\033[31mError!\033[0m File is not selected.")
            generate_separator("", "*")

            return False

        # Get name of the selected config file and save it
        self.in_config_file = file_name.name

        print(
            "\033[32m" + os.path.basename(file_name.name) + "\033[0m" + " is selected."
        )

        generate_separator("", "*")

        return True

    def display_tuning_tool_menu(self):
        """
        Display the main menu of tuning tool
        """
        generate_separator("Main Menu", "-")

        print("Select a command:")

        # Print each menu option of the tuning tool.
        for key, value in self.tuning_tool_menu_options.items():
            print(key + ". " + value)


if __name__ == "__main__":
    TuningTool()
