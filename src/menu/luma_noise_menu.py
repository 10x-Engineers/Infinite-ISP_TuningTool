"""
File: luma_noise_menu.py
Description: Executes the menu flow for the luminance noise estimation module
Author: 10xEngineers
------------------------------------------------------------
"""
import sys
import os
from src.modules.NR.noise_reduction_2d_module import NEModule as NE
from src.menu.menu_common_func import (
    get_user_input,
    area_selection_error,
    invalid_choice_message,
    back_to_tuning_tool_message,
    display_main_menu,
)
from src.utils.gui_common_utils import generate_separator, menu_title


class NEMenu:
    """
    Noise Estimation Tool
    """

    # Define object of noise estimation module
    ne_module = NE()

    # Options for open area selection frame
    selection_frame_menu_options = {
        "1": "Open \033[36mColorcChecker Selection Frame.\033[0m",
        "2": "Return to the Main Menu.",
        "3": "Quit\n",
    }
    # This is the main function to start the menu.

    def ask_user_for_wb(self, path):
        """
        Ask user to apply white balance
        """
        _, file_extension = os.path.splitext(path)
        ext = file_extension.lower()
        while True:
            if ext in [".png", ".jpg", ".jpeg"]:
                generate_separator("", "-")
                print("Do you want to apply white balance?\n\nSelect a command:")
                print("1. Yes")
                print("2. No\n")
                choice = get_user_input()
                if choice == "1":
                    return "1"
                if choice == "2":
                    return "2"
                invalid_choice_message()
                continue
            if ext == ".raw":
                return "1"

    def start_menu(self):
        """
        Start menu for the module.
        """
        os.system("cls")

        # Welcome note
        self.welcome_to_ne()

        # Display main menu
        display_main_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                # Get raw image and its parameters.
                is_loaded, img_para = self.ne_module.is_image_and_para_loaded()
                if not is_loaded:
                    display_main_menu()
                    continue

                # Allow user to select color checker patches. If patches are not
                # selected or saved then display another menu for area selection again.
                is_selection_done = self.ne_module.color_checker_selection_frame()
                if not is_selection_done:
                    area_selection_error()
                    selection_status = self.start_frame_selection_menu()

                    if selection_status == "1":
                        back_to_tuning_tool_message()
                        break

                # Calculate Noise Estimation.
                ask_user = self.ask_user_for_wb(img_para.file_name)
                self.ne_module.implement_ne_algo(ask_user)

                apply_menu_status = self.restart_ne_menu()

                if apply_menu_status == "Tuning_tool":
                    # Go back to tuning tool.
                    back_to_tuning_tool_message()
                    break
                if apply_menu_status == "Restart_NE":
                    # Restart noise estimation tool.
                    self.welcome_to_ne()
                    display_main_menu()
                    continue
            elif choice == "2":
                back_to_tuning_tool_message()
                break
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                display_main_menu()

    def welcome_to_ne(self):
        """
        Welcome note for the module
        """
        os.system("cls")
        menu_title("Welcome to the \033[36mLuminance Noise Estimation Tool\033[0m")
        print("Raw file name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: ColorChecker_2592x1536_12bits_RGGB.raw\n")

    # Display selection frame menu
    def display_selection_frame_menu(self):
        """
        Display Selection Frame Menu
        """
        print("Select a command:")

        # Display selection frame menu options
        for key, value in self.selection_frame_menu_options.items():
            print(key + ". " + value)

    apply_save_ne_menu_options = {
        "1": "Restart the Noise Estimation Tool",
        "2": "Return to the Main Menu",
        "3": "Quit\n",
    }

    # Display apply and save bne menu
    def display_restart_ne_menu(self):
        """
        Display menu options after BNE done
        """
        print("\nSelect a command:")

        # Display selection frame menu options
        for key, value in self.apply_save_ne_menu_options.items():
            print(key + ". " + value)

    # Menu to open area selection frame
    def start_frame_selection_menu(self):
        """
        Display selection frame menu
        """
        self.display_selection_frame_menu()
        while True:
            choice = get_user_input()
            if choice == "1":
                is_selection_done = self.ne_module.color_checker_selection_frame()
                if not is_selection_done:
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

    def restart_ne_menu(self):
        """
        Menu apply to restart the module
        """
        self.display_restart_ne_menu()
        while True:
            choice = get_user_input()
            if choice == "1":
                self.welcome_to_ne()
                display_main_menu()
                return "Restart_ne"
            elif choice == "2":
                return "Tuning_tool"
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                self.display_restart_ne_menu()
