"""
File: gamma_menu.py
Description: Executes the menu flow for the gamma module
Author: 10xEngineers
------------------------------------------------------------
"""
import os
from src.modules.Gamma.gamma_module import GammaModule as gamma_module
from src.menu.menu_common_func import (
    back_to_tuning_tool_message,
    print_and_select_menu,
    end_tuning_tool,
)
from src.utils.gui_common_utils import generate_separator, menu_title


class GammaMenu:
    """
    Gamma Menu
    """

    # Options for comparing gamma curves
    display_gamma_menu_options = [
        "Compare the Gamma Curves",
        "Return to the Main Menu",
        "Quit\n",
    ]

    # Options for selecting yml file
    select_yml_file_menu_options = [
        "Select a YAML file",
        "Return to the Main Menu",
        "Quit\n",
    ]

    def __init__(self, in_config_file):
        self.gamma_moudle = gamma_module(in_config_file)

    def start_menu(self):
        """
        Start menu for the module
        """

        # clean console
        os.system("cls")

        # Welcome note
        self.welcome_to_gamma()

        while True:
            # Display main menu
            choice = print_and_select_menu(self.display_gamma_menu_options)

            if choice == "1":
                selection_status = self.start_select_config_file_menu()
                if selection_status == "Tuning_tool":
                    back_to_tuning_tool_message()
                    break

                if not self.gamma_moudle.get_plotting_data():
                    end_tuning_tool()

                self.gamma_moudle.display_gamma_plots()

                generate_separator("", "*")

            elif choice == "2":
                back_to_tuning_tool_message()
                break

            elif choice == "3":
                end_tuning_tool()

    def welcome_to_gamma(self):
        """
        Welcome note for Gamma
        """
        menu_title("Welcome to the \033[35mGamma Tool\033[0m ")

    def start_select_config_file_menu(self):
        """
        Return if config file exits in the config folder otherwise
         allow user to select a YAML file.
        """
        config_file = self.gamma_moudle.is_config_exists()
        if config_file:
            return

        # Display file missing message.
        print("\033[31mError!\033[0m The YAML file does not exist.")
        generate_separator("", "*")

        while True:
            # Display file selection menu
            choice = print_and_select_menu(self.select_yml_file_menu_options)

            if choice == "1":
                if not self.gamma_moudle.load_ymal_file():
                    continue

                else:
                    return

            elif choice == "2":
                return "Tuning_tool"

            elif choice == "3":
                end_tuning_tool()
