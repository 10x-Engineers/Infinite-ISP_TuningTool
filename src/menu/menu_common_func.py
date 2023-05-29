"""
File: menu_common_func.py
Description: This file contains common functions used for menu flow of modules
Author: 10xEngineers
------------------------------------------------------------
"""
import os
from src.utils.gui_common_utils import generate_separator, menu_title

main_menu_options = {
    "1": "Load an \033[32mImage\033[0m",
    "2": "Return to the Main Menu",
    "3": "Quit\n",
}


def display_main_menu():
    """
    Display maine menu
    """
    print("Select a command:")

    # Display main menu commands
    for key, value in main_menu_options.items():
        print(key + ". " + value)


def get_user_input():
    """
    Get user input to select a menu option
    """
    choice = input("Enter a number to choose an option: ")
    return choice


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


def invalid_choice_message():
    """
    Message to display on entering wrong choice
    """
    print("\033[31mInvalid choice.\033[0m")
    generate_separator("", "*")


def area_selection_error():
    """
    Error message if patches are not selected on
    selection frame.
    """
    print("\033[31mError!\033[0m Patches are not selected or saved.")
    generate_separator("", "*")
