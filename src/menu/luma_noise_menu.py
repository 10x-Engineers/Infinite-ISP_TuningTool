"""
File: luma_noise_menu.py
Description: Executes the menu flow for the luminance noise estimation module
Author: 10xEngineers
------------------------------------------------------------
"""
import os
from src.modules.NR.noise_reduction_2d_module import NEModule as NE
from src.menu.menu_common_func import (
    area_selection_error,
    back_to_tuning_tool_message,
    print_and_select_menu,
    get_main_menu_options,
    get_yes_no_options,
    end_tuning_tool,
)
from src.utils.gui_common_utils import generate_separator, menu_title


class NEMenu:
    """
    Noise Estimation Tool
    """

    # Define object of noise estimation module
    ne_module = NE()

    # Options for open area selection frame
    selection_frame_menu_options = [
        "Open ColorcChecker Selection Frame",
        "Return to the Main Menu",
        "Quit\n",
    ]

    apply_save_ne_menu_options = [
        "Restart the Noise Estimation Tool",
        "Return to the Main Menu",
        "Quit\n",
    ]

    def start_menu(self):
        """
        Start menu for the module.
        """
        os.system("cls")

        # Welcome note
        self.welcome_to_ne()

        while True:
            # Display main menu
            choice = print_and_select_menu(get_main_menu_options())

            if choice == "1":
                # Get raw image and its parameters.
                is_loaded = self.ne_module.is_image_and_para_loaded()
                if not is_loaded:
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

                # Ask user to apply white balance.
                ask_user = self.ask_user_for_wb()

                self.ne_module.implement_ne_algo(ask_user)

                apply_menu_status = self.restart_ne_menu()

                if apply_menu_status == "Tuning_tool":
                    # Go back to tuning tool.
                    back_to_tuning_tool_message()
                    break

                if apply_menu_status == "Restart_NE":
                    # Restart noise estimation tool.
                    self.welcome_to_ne()
                    continue

            elif choice == "2":
                back_to_tuning_tool_message()
                break

            elif choice == "3":
                end_tuning_tool()

    def welcome_to_ne(self):
        """
        Welcome note for the module
        """
        os.system("cls")
        menu_title("Welcome to the \033[36mLuminance Noise Estimation Tool\033[0m")
        print("Raw file name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: ColorChecker_2592x1536_12bits_RGGB.raw\n")

    def start_frame_selection_menu(self):
        """
        Display selection frame menu
        """

        while True:
            choice = print_and_select_menu(self.selection_frame_menu_options)

            if choice == "1":
                is_selection_done = self.ne_module.color_checker_selection_frame()
                if not is_selection_done:
                    area_selection_error()
                    continue

                break

            elif choice == "2":
                return "1"

            elif choice == "3":
                end_tuning_tool()

    def restart_ne_menu(self):
        """
        Menu apply to restart the module
        """

        while True:
            choice = print_and_select_menu(self.apply_save_ne_menu_options)

            if choice == "1":
                self.welcome_to_ne()
                return "Restart_ne"

            elif choice == "2":
                return "Tuning_tool"

            elif choice == "3":
                end_tuning_tool()

    def ask_user_for_wb(self):
        """
        Ask user to apply white balance
        """
        # Creating separator on the console
        generate_separator("", "-")

        # Giving options to user for applying white balance on image
        choice = print_and_select_menu(get_yes_no_options(), "Apply White Balance?")
        if choice == "1":
            return "1"

        if choice == "2":
            return "2"
