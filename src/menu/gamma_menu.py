"""
File: gamma_menu.py
Description: Executes the menu flow for the gamma module
Author: 10xEngineers
------------------------------------------------------------
"""
import sys
import os
from src.modules.Gamma.gamma_module import GammaModule as gamma_module
from src.menu.menu_common_func import (
    get_user_input,
    invalid_choice_message,
    back_to_tuning_tool_message,
)
from src.utils.gui_common_utils import generate_separator, menu_title


class GammaMenu:
    """
    Gamma Menu
    """

    # Options for opening image
    display_gamma_menu_options = {
        "1": "Compare the Gamma Curves",
        "2": "Return to the Main Menu",
        "3": "Quit\n",
    }

    # Options for opening image
    select_yml_file_menu_options = {
        "1": "Select a YAML file",
        "2": "Return to the Main Menu",
        "3": "Quit\n",
    }

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

        # Display main menu
        self.display_main_menu()

        while True:
            choice = get_user_input()

            if choice == "1":
                selection_status = self.start_select_config_file_menu()
                if selection_status == "Tuning_tool":
                    back_to_tuning_tool_message()
                    break
                if not self.gamma_moudle.get_plotting_data():
                    sys.exit()

                self.gamma_moudle.display_gamma_plots()
                # Again display main menu to restart
                generate_separator("", "*")
                self.display_main_menu()
            elif choice == "2":
                back_to_tuning_tool_message()
                break
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                self.display_main_menu()

    def welcome_to_gamma(self):
        """
        Welcome note for Gamma
        """
        menu_title("Welcome to the \033[35mGamma Tool\033[0m ")

    def display_main_menu(self):
        """
        Display main menu
        """
        print("Select a command:")

        # Display main menu options
        for key, value in self.display_gamma_menu_options.items():
            print(key + ". " + value)

    def display_select_yaml_file_menu(self):
        """
        Display select YAML file menu
        """
        print("Select a command:")

        # Display main menu options
        for key, value in self.select_yml_file_menu_options.items():
            print(key + ". " + value)

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

        # Display file selection menu
        self.display_select_yaml_file_menu()

        while True:
            choice = get_user_input()

            if choice == "1":
                if not self.gamma_moudle.load_ymal_file():
                    self.display_select_yaml_file_menu()
                    continue
                else:
                    return
            elif choice == "2":
                return "Tuning_tool"
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                self.display_select_yaml_file_menu()
                continue
