"""
File: bayer_noise_menu.py
Description: Executes the menu flow for the bayer noise estimation module
Author: 10xEngineers
------------------------------------------------------------
"""
import sys
import os
from src.modules.BNR.bnr_module import BneModule as BNE
from src.menu.menu_common_func import get_user_input, area_selection_error,\
    invalid_choice_message, back_to_tuning_tool_message, display_main_menu
from src.utils.gui_common_utils import menu_title

class BNEMenu:
    """
    Noise Estimation Tool
    """
    # Define object of noise estimation module
    bne_module = BNE()

    # Options for opening image
    open_image_menu_options = {
        "1": "Load \033[32mRaw Image\033[0m",
        "2": "Return to the Main Menu",
        "3": "Quit\n",
    }

    # Options for open area selection frame
    selection_frame_menu_options = {
        "1": "Open \033[35mColorChecker Selection Frame\033[0m",
        "2": "Return to the Main Menu",
        "3": "Quit\n",
    }

    def start_menu(self):
        """
        Start menu for the module.
        """
        # clean console
        os.system("cls")

        # Welcome note
        self.welcome_to_bne()

        # Display main menu
        display_main_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                # Get raw image and its parameters.
                is_loaded = self.bne_module.is_image_and_para_loaded()
                if not is_loaded:
                    display_main_menu()
                    continue

                # Allow user to select color checker patches. If patches are not
                # selected or saved then display another menu for area selection again.
                is_selection_done = self.bne_module.color_checker_selection_frame()
                if not is_selection_done:
                    area_selection_error()

                    selection_status = self.start_frame_selection_menu()

                    if selection_status == "1":
                        back_to_tuning_tool_message()
                        break

                # Calculate Noise Estimation.
                self.bne_module.implement_bne_algo()

                apply_menu_status = self.restart_bne_menu()

                if apply_menu_status == "Tuning_tool":
                    # Go back to tuning tool.
                    back_to_tuning_tool_message()
                    break
                elif apply_menu_status == "Restart_NE":
                    # Restart noise estimation tool.
                    self.welcome_to_bne()
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

    def welcome_to_bne(self):
        """
        Welcome note for the module
        """
        os.system("cls")
        menu_title("Welcome to the \033[33mBayer Noise Estimation Tool\033[0m")
        print("File name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: ColorChecker_2592x1536_12bits_RGGB.raw\n")

    def display_selection_frame_menu(self):
        """
        Display menu to select area frame
        """
        print("Select a command:")

        # Display selection frame menu options
        for key, value in self.selection_frame_menu_options.items():
            print(key + ". " + value)

    restart_bne_menu_options = {
        "1": "Restart the Bayer Noise Estimation Tool",
        "2": "Return to the Main Menu",
        "3": "Quit\n",
    }

    def display_restart_bne_menu(self):
        """
        Display menu options after BNE done
        """
        print("Select a command:")

        # Display selection frame menu options
        for key, value in self.restart_bne_menu_options.items():
            print(key + ". " + value)

    def start_frame_selection_menu(self):
        """ 
        Display selection frame menu
        """
        self.display_selection_frame_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                is_selection_done = self.bne_module.color_checker_selection_frame()
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

    def restart_bne_menu(self):
        """
        Menu apply to restart the module
        """
        self.display_restart_bne_menu()

        while True:
            choice = get_user_input()
            if choice == "1":
                self.welcome_to_bne()
                display_main_menu()
                return "Restart_ne"
            elif choice == "2":
                return "Tuning_tool"
            elif choice == "3":
                sys.exit()
            else:
                invalid_choice_message()
                self.display_restart_bne_menu()
