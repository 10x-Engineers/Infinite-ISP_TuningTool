"""
File: config_files_menu.py
Description: Executes the menu flow when user chooses to generate files
Author: 10xEngineers
------------------------------------------------------------
"""
import os
import shutil
from src.menu.menu_common_func import (
    generate_separator,
    back_to_tuning_tool_message,
    print_and_select_menu,
    end_tuning_tool,
)
from src.utils.gui_common_utils import (
    menu_title,
    get_config_out_file,
    select_file_saving_dir,
)
from src.utils.create_h_file.generate_h_file import GenerateHFile
from src.utils.read_yaml_file import ReadWriteYMLFile


class ConfigFilesMenu:
    """
    Generating Files Menu Flow
    """

    # Save RTL compatible config file options
    h_file_options = [
        "v1.0",
        "Back to the Configuration Files Menu",
        "Return to the Main Menu",
        "Quit\n",
    ]

    config_file_main_menu = [
        "Update Sensor Info",
        "Generate configs.yml",
        "Generate isp_init.h",
        "Return to the Main Menu",
        "Quit\n",
    ]

    bayer_options = [
        "rggb",
        "bggr",
        "grbg",
        "gbrg\n",
    ]

    bitdepth_options = [
        "8",
        "10",
        "12",
        "14\n",
    ]

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.yaml_file = ReadWriteYMLFile(in_config_file)

    def start_menu(self):
        """
        Start Menu for Generating Files
        """
        # clean console
        os.system("cls")

        # Welcome note
        self.welcome_note()

        # Displaying sensor info
        generate_separator("Sensor Info", "-")
        self.display_sensor_info()

        while True:
            choice = print_and_select_menu(self.config_file_main_menu)
            if choice == "1":
                self.update_sensor_info()

            elif choice == "2":
                # Save the configs.yml file
                self.save_config_file()

            elif choice == "3":
                # Exit the application
                break_flag = self.save_h_file()
                if break_flag is True:
                    break

            elif choice == "4":
                back_to_tuning_tool_message()
                break

            elif choice == "5":
                # Exit the application
                end_tuning_tool()

    def update_sensor_info(self):
        """
        To update the sensor info in the configs.yml file,
        4 values are required from the user.
        1) Bayer pattern 2) Bit depth 3) Width 4) Height
        """

        # Setting variables for bayer and bitdepth
        bitdepth = None
        bayer_pattern = None

        # Ask user choices for bayer pattern
        bayer_choice = print_and_select_menu(
            self.bayer_options, message="Select the Bayer Pattern:"
        )

        if bayer_choice == "1":
            bayer_pattern = "rggb"

        elif bayer_choice == "2":
            bayer_pattern = "bggr"

        elif bayer_choice == "3":
            bayer_pattern = "grbg"

        elif bayer_choice == "4":
            bayer_pattern = "gbrg"

        # Ask user choices for bits depth
        bit_choice = print_and_select_menu(
            self.bitdepth_options, message="Select the Bit Depth:"
        )

        if bit_choice == "1":
            bitdepth = 8

        elif bit_choice == "2":
            bitdepth = 10

        elif bit_choice == "3":
            bitdepth = 12

        elif bit_choice == "4":
            bitdepth = 14

        # Taking user input for width in the range
        # 1 - 30730 (32k).
        while True:
            width = input("\nEnter width:")

            # Error handling for valid input
            try:
                # Attempt to convert the input to an integer
                width = int(width)

                if width > 0 and width < 30721:
                    break  # Exit the loop if the input is valid

                else:
                    print("\033[31mInvalid Input!\033[0m Valid range (1-30720).")

            except ValueError:
                self.display_error_msg()

        # Taking user input for height in the
        # range 1 - 17281 (32k).
        while True:
            height = input("\nEnter height:")

            # Error handling for valid input
            try:
                # Attempt to convert the input to an integer
                height = int(height)

                if height > 0 and height < 17281:
                    break  # Exit the loop if the input is valid

                else:
                    print("\033[31mInvalid Input!\033[0m Valid range (1-17280).")

            except ValueError:
                self.display_error_msg()

        # Updating sensor info in the config file
        self.yaml_file.set_sensor_info(bitdepth, bayer_pattern, width, height)
        generate_separator("Updated Sensor Info!", "-")

        # Saving data in config file
        self.yaml_file.save_file(self.in_config_file)

        # Displaying sensor info for the user
        self.display_sensor_info()

    def display_sensor_info(self):
        """
        Display sensor info
        """
        # Extracting data from the config file
        bpp, bayer, width, height = self.yaml_file.get_sensor_info()

        # Displaying sensor info data on console
        print("Bit Depth:", bpp)
        print("Bayer Pattern:", bayer)
        print("Width:", width)
        print("Height:", height)
        generate_separator("", "-")

    def welcome_note(self):
        """
        Welcome note to display
        """
        menu_title("\033[35mGenerate Configuration Files \033[0m ")

    def save_config_file(self):
        """
        Save the updated configs.yml file on the user selected path
        """

        out_file_path = get_config_out_file(self.in_config_file)

        if not out_file_path:
            return

        print("File is saved at: ", self.in_config_file)
        generate_separator("", "*")

        shutil.copyfile(self.in_config_file, out_file_path)

    def save_h_file(self):
        """
        Save the RTL compatible config file.
        Get the user desired version and select the configs.yml crossponding to that version,
        and save the .h file.
        """
        # Setting variable
        curr_config_file = None
        while True:
            selected_version = self.start_create_h_file_menu()

            if selected_version == "v1.0":
                curr_config_file = self.in_config_file

            elif selected_version == "Back":
                return False

            elif selected_version == "Tuning_tool":
                back_to_tuning_tool_message()
                return True

            # Get a directory to save the .h file
            h_file_dir = select_file_saving_dir()
            if not h_file_dir:
                print(
                    "\033[31mWarning!\033[0m File destination path is not selected.\n"
                )
                continue

            # Combine file name and selected directory
            h_file_name = "isp_init.h"
            h_file_full_name = os.path.join(h_file_dir, h_file_name)

            # Create object to generate .h file
            h_file_obj = GenerateHFile(curr_config_file, selected_version)
            h_file_obj.write_to_h_file(h_file_full_name)

            print(f"The {h_file_name} is saved successfully at: \n", h_file_full_name)
            generate_separator("", "*")
            return False

    def start_create_h_file_menu(self):
        """
        Start create RTL compatible config file (.h) menu
        """

        while True:
            choice = print_and_select_menu(self.h_file_options)

            if choice == "1":
                return "v1.0"

            elif choice == "2":
                return "Back"

            elif choice == "3":
                return "Tuning_tool"

            elif choice == "4":
                end_tuning_tool()

    def display_error_msg(self):
        """
        Display error message for invalid input
        """
        print("\033[31mInvalid Input!\033[0m Please enter again.\n")
