"""
File: tuning_tool.py
Description: It is the starting point of the tool.
Author: 10xEngineers
------------------------------------------------------------
"""

import os
import shutil
from src.menu.black_level_calibration_menu import BlackLevelCalibrationMenu as BlcMenu
from src.menu.color_correction_matrix_menu import ColorCorrectionMatrixMenu as CcmMenu
from src.menu.gamma_menu import GammaMenu
from src.menu.luma_noise_menu import NEMenu as neMenu
from src.menu.config_files_menu import ConfigFilesMenu
from src.menu.menu_common_func import (
    display_welcome_note,
    end_tuning_tool,
    print_and_select_menu,
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

    # Here is applied the color formatting to the text.
    # The escape sequence "\033[36m" is used to set the
    # forground color. There is a particular color against
    # each sequence.

    # Config file menu options
    load_config_menu_options = ["Load a Yaml file", "Quit\n"]

    # Main menu options
    tuning_tool_menu_options = [
        "Calibrate Black Levels",
        "Calculate ColorChecker White Balance",
        "Calculate Color Correction Matrix",
        "Generate Gamma Curves",
        "Estimate Bayer Noise Levels",
        "Estimate Luminance Noise Levels",
        "Generate Configuration Files",
        "Quit\n",
    ]

    load_app_data_config_menu_options = ["Yes", "No\n"]

    def __init__(self):
        """
        This is the main and starting point of the tuning tool.
        """

        self.in_config_file = None
        display_welcome_note()

        # Load pipeline configuration YML
        self.load_config()

        self.start_main_menu()

    def start_main_menu(self):
        """
        This is the main and starting point of main menu.
        """

        while True:
            # Print the main menu of the Tuning Tool on the console.
            generate_separator("Main Menu", "-")

            choice = print_and_select_menu(self.tuning_tool_menu_options)

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
                ccm_menu = CcmMenu(self.in_config_file)
                ccm_menu.start_menu()

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
                # Start file generation menu
                fmenu = ConfigFilesMenu(self.in_config_file)
                fmenu.start_menu()

            elif choice == "8":
                # Exit the application
                end_tuning_tool()

    def load_config(self):
        """
        At the start of tuning tool. There should be a config.yml file present
        in the config directory. If this file is renamed or removed by the user,
        this function allow user to select a new YAML file.
        """
        config_file_name = "default_configs.yml"
        config_file_dir = "config"

        # Join file and dir and load file if file exists
        self.in_config_file = os.path.join(
            os.getcwd(), config_file_dir, config_file_name
        )

        # Exist if file exits and continue with main menu of the Tuning Tool.
        if os.path.exists(self.in_config_file):
            self.copy_config_file(self.in_config_file, True)
            return

        # Display a warning message.
        print(
            "\n\033[31mError!\033[0m The default_configs.yml file does "
            'not exist in "config" directory.\nPlease ensure that the file is present.'
        )

        generate_separator("", "*")
        end_tuning_tool()

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

    def copy_config_file(self, config, is_default_config):
        """
        This function checks that either there is already configs.yml present in the
        app_data or not. If not then copy the user selected or default configs.yml and
        save into app_data folder. If present then it overwright the exiting one.
        """
        des_file_name = "configs.yml"

        src_file = config

        des_folder_name = "config"

        des_folder = os.path.join(os.getcwd(), des_folder_name)

        if not os.path.exists(des_folder):
            os.makedirs(des_folder)

        des_file = os.path.join(des_folder, des_file_name)

        if not os.path.exists(des_file):
            shutil.copyfile(src_file, des_file)

        else:
            if not is_default_config:
                shutil.copyfile(src_file, des_file)

            else:
                choice = print_and_select_menu(
                    self.load_app_data_config_menu_options,
                    message=
                    "A configs.yml file exits in configs directory. Do you want to load it?",
                )

                if choice == "2":
                    shutil.copyfile(src_file, des_file)

        self.in_config_file = des_file


if __name__ == "__main__":
    TuningTool()
