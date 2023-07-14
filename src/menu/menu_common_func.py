"""
File: menu_common_func.py
Description: This file contains common functions used for menu flow of modules
Author: 10xEngineers
------------------------------------------------------------
"""
import os
import sys
import questionary
from prompt_toolkit.styles import Style
from src.utils.gui_common_utils import generate_separator, menu_title

main_menu_options = [
    "Load an Image",
    "Return to the Main Menu",
    "Quit\n",
]

yes_no_options = [
    "Yes",
    "No\n",
]


def print_and_select_menu(menu_options, message="Select an option:"):
    """
    This function display the given menu options on the screen and
    allow user to select one using arrow keys.
    In the end, it returns the index of the selected option as a string
    considering index starting from 1 instead of 0.
    """
    style = Style.from_dict(
        {
            "message": "fg:green",
            "questionmark": "fg:ansired",
            "pointer": "fg:ansigreen bold",
            "selected": "fg:green",
        }
    )

    choice = questionary.select(
        message=message,
        style=style,
        choices=menu_options,
        qmark="\u2605",
        show_selected=True,
        use_arrow_keys=True,
        default=None,
    ).ask()
    print()
    index = menu_options.index(choice)

    index = str(index + 1)

    return index


def get_main_menu_options():
    """
    This function returns the main menu options
    """
    return main_menu_options


def get_yes_no_options():
    """
    This function returns the yes/no options
    """
    return yes_no_options


def display_welcome_note():
    """
    Welcome note for tuning tool
    """
    os.system("cls")
    menu_title("Welcome to the \033[32mTuning Tool\033[0m")


def back_to_tuning_tool_message():
    """
    Returning to main menu of tuning tool message
    """
    # Clear the console
    os.system("cls")

    # Print the Tuning tool welcome message
    display_welcome_note()


def area_selection_error():
    """
    Error message if patches are not selected on
    selection frame.
    """
    print("\033[31mError!\033[0m Patches are not selected or saved.")
    generate_separator("", "*")


def remove_config_file():
    """
    Remove the configs.yml file that is present in the app_data folder.
    """
    des_file_name = "configs.yml"

    des_folder_name = "app_data"

    des_file_path = os.path.join(os.getcwd(), des_folder_name, des_file_name)

    if not os.path.exists(des_file_path):
        return

    os.remove(des_file_path)


def end_tuning_tool():
    """
    This function is called when user quit the tool.
    """
    # remove_config_file()

    sys.exit()
