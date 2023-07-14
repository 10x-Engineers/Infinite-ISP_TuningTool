"""
File: color_correction_matrix_menu.py
Description: Executes the menu flow for the color correction matrix module
Author: 10xEngineers
------------------------------------------------------------
"""
import os
from src.modules.CCM.ccm_module import ColorCorrectionMatrixModule as CcmModule
from src.menu.menu_common_func import (
    area_selection_error,
    back_to_tuning_tool_message,
    print_and_select_menu,
    get_main_menu_options,
    get_yes_no_options,
    end_tuning_tool,
    generate_separator,
)
from src.utils.gui_common_utils import menu_title


class ColorCorrectionMatrixMenu:
    """
    Color Correction Matrix Menu
    """

    restart_main_menu_options = [
        "Use the Loaded Image",
        "Load an Image",
        "Return to the Main Menu",
        "Quit\n",
    ]

    restart_colorchecker_menu_options = [
        "Use the Selected Patches",
        "Open ColorChecker Selection Frame",
    ]

    # Option for open area selection frame
    selection_frame_menu_options = [
        "Open ColorChecker Selection Frame",
        "Return to the Main Menu",
        "Quit\n",
    ]

    # Option for auto gain selection
    auto_gain_menu_option = [
        "Enable Auto Gain",
        "Disable Auto Gain",
    ]

    # Option for errorr matrix type
    error_matrix_menu_option = [
        chr(0x394) + "C" + " 00",
        chr(0x394) + "E" + " 00",
    ]

    # Menu options for config file
    config_menu_option = [
        "Save config.yml with Calculated Color Correction Matrix",
        "Restart the Color Correction Matrix Tool",
        "Return to the Main Menu",
        "Quit\n",
    ]

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.ccm_module = CcmModule(in_config_file)
        self.restart_ccm = False

    def start_menu(self):
        """
        Display start menu
        """

        # clean console
        os.system("cls")

        # Welcome note
        self.welcome_to_ccm()

        while True:
            # Display main menu
            if self.restart_ccm:
                choice = print_and_select_menu(self.restart_main_menu_options)
                choice = self.update_choice(choice)

            else:
                choice = print_and_select_menu(get_main_menu_options())
                self.restart_ccm = False

            if choice == "0" or choice == "1":
                if choice == "1":
                    # Return true if image and its parameters are loaded.
                    self.restart_ccm = False
                    image_loaded = self.ccm_module.is_image_and_para_loaded()
                    if not image_loaded:
                        continue

                # restart_colorchecker_menu_options
                restart_color_checker = ""
                if choice == "0":
                    restart_color_checker = print_and_select_menu(
                        self.restart_colorchecker_menu_options
                    )
                # Allow user to select color checker patches. If patches are
                # not selected or saved then display another menu for
                # area selection agian.
                if choice == "1" or restart_color_checker == "2":
                    patches_selected = self.ccm_module.color_checker_selection_frame()
                    if not patches_selected:
                        area_selection_error()
                        selection_status = self.start_frame_selection_menu()

                        if selection_status == "1":
                            back_to_tuning_tool_message()
                            break

                # Get required parameters compulsory to run algo
                print("\033[32mParameters required for ccm algorithm:\033[0m")

                # Ask user to apply white balance.
                self.ask_user_for_wb()

                # Get error matrix type
                self.start_algo_selection_menu()

                # Get input on to maintain wb
                self.start_wb_selection_menu()

                # Start ccm algorithm
                self.ccm_module.start_algo()

                # Start config file menu
                res = self.start_config_file_menu()

                if res == "1":
                    break

                if res == "2":
                    self.restart_ccm = True
                    self.welcome_to_ccm()
                    continue  # to start ccm again

            elif choice == "2":
                back_to_tuning_tool_message()
                break

            elif choice == "3":
                end_tuning_tool()

    def welcome_to_ccm(self):
        """
        Welcome note for CCM
        """

        os.system("cls")
        menu_title("Welcome to the \033[36mColor Correction Matrix Tool\033[0m ")
        print("Raw file name format: Name_WxH_Nbits_Bayer.raw")
        print("For example: ColorChecker_2592x1536_12bits_RGGB.raw\n")

    def start_config_file_menu(self):
        """
        Menu to save config file or chose other options
        """

        while True:
            # Add additional space
            print()

            choice = print_and_select_menu(self.config_menu_option)

            if choice == "1":
                self.ccm_module.save_ccm_config_file()
                continue

            elif choice == "2":
                return "2"

            elif choice == "3":
                back_to_tuning_tool_message()
                return "1"

            elif choice == "4":
                end_tuning_tool()

    def start_wb_selection_menu(self):
        """
        Menu to ask your either need to maintaing wb or not.
        """

        # Add additional space
        print()

        choice = print_and_select_menu(get_yes_no_options(), "Maintain White Balance? ")

        if choice == "1":
            self.ccm_module.enable_wb(True)
            print("White balance is maintained.")

        elif choice == "2":
            self.ccm_module.enable_wb(False)
            print("White balance is not maintained.")

    def start_algo_selection_menu(self):
        """
        Menu for auto gain selection
        """
        choice = print_and_select_menu(
            self.error_matrix_menu_option, message="Error Matrix?"
        )

        if choice == "1":
            self.ccm_module.set_algo_type(False)
            print(chr(0x394) + "C" + " 00 is selected.")

        elif choice == "2":
            self.ccm_module.set_algo_type(True)
            print(chr(0x394) + "E" + " 00 is selected.")

    def start_frame_selection_menu(self):
        """
        Menu to open area selection frame
        """

        while True:
            # Display selection frame menu
            choice = print_and_select_menu(self.selection_frame_menu_options)

            if choice == "1":
                output = self.ccm_module.color_checker_selection_frame()
                if not output:
                    area_selection_error()
                    continue

                break

            elif choice == "2":
                return "1"

            elif choice == "3":
                end_tuning_tool()

    def description(self):
        """
        Description of ccm tool.
        """
        print("Please select the ColorChecker image")

    def ask_user_for_wb(self):
        """
        Ask user to apply white balance
        """
        # Creating separator on the console
        generate_separator("", "-")

        # Giving options to user for applying white balance on image
        choice = print_and_select_menu(get_yes_no_options(), "Apply White Balance?")

        if choice == "1":
            self.ccm_module.set_wb_flag(True)

        elif choice == "2":
            self.ccm_module.set_wb_flag(False)

    def update_choice(self, choice):
        """
        This function is used to give the one option above the
        selected one.
        """
        choice_int = int(choice)
        choice_int = choice_int - 1
        return str(choice_int)
