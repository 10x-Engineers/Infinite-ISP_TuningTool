"""
File: gui_common_utils.py
Description: This file contains common functions used for GUI.
Author: 10xEngineers
------------------------------------------------------------
"""
import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from PIL import Image, ImageTk


def generate_separator(string, symb):
    """
    This function will generate a separating line with string placed
    in center of the user defined character (symb)
    """
    # Declaring total length of the separator line
    total_length = 73
    string_length = len(string)

    # Calculating padding length by subtracting string
    # length from the total length
    padding_length = (total_length - string_length) // 2

    padding = symb * padding_length

    # Generating final string with padded characters
    padded_string = f"{padding}{string}{padding}"

    if len(padded_string) < total_length:
        padded_string += symb

    print("\n", padded_string, "\n")


def menu_title(string):
    """
    This function will generate a menu title
    for each module
    """
    # Declaring total length of the string for each
    # line in the menu title. The menu title has total of
    # three separate lines. Each will be generated separately
    # and in last it will be combined to print the title
    total_length = 70

    # Subtracting 9 from length of the input string to exclude
    # the color arguments that comes up with the string
    string_length = len(string) - 9
    padding_length = (total_length - string_length) // 2

    # Defining symbols for each line dash for top and bottom
    # lines and space for the center one.
    symb1 = "━"
    symb2 = " "
    padding = symb2 * (padding_length)

    # Combining the strings to get the final menu title
    padded_string1 = f"{symb1 * (total_length-2)}"
    padded_string2 = f"{padding}{string}{padding}"
    padded_string3 = f"{symb1 * (total_length-2)}"

    while len(padded_string2) < (total_length):
        padded_string2 += symb2

    print("\n┏━", padded_string1, "━┓")
    print("┃", padded_string2, "┃")
    print("┗━", padded_string3, "━┛")


def pop_up_msg(msg):
    """
    It will generate a pop up window message
    """
    root = tk.Tk()

    # Hide the main window
    root.withdraw()

    # Display a message box
    messagebox.showinfo("Warning", msg)

    # Destroy the main window (optional)
    root.destroy()


def cv2_to_pil_image(cv_image):
    """
    Convert the openCV image into PIL(Python imaging library) image.
    """
    pil_image = Image.fromarray(cv_image)
    return pil_image


def get_screen_resolution(root):
    """
    Extract the user's screen resolution (width and height).
    """
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    return (screen_width, screen_height)


def determine_image_scale_factor(root, image_width, image_height, offset_x, offset_y):
    """
    Determine the factor to resize the image.
    """
    available_size = cal_available_screen_size(root, offset_x, offset_y)

    # Find out scale factor if either image width or image
    # height is greater than avaialbe size otherwise set it to 1
    if (image_width > available_size[0]) or (image_height > available_size[1]):
        factor1 = image_width / available_size[0]
        factor2 = image_height / available_size[1]
        if factor1 > factor2:
            return factor1
        return factor2
    return 1


def get_tk_image(image):
    """
    Convert the pil image into imagetk to display on the canvas.
    """
    display_image = ImageTk.PhotoImage(image=image)
    return display_image


def cal_available_screen_size(root, offset_x, offset_y):
    """
    cal the available screen resolution.
    """
    # Get user's screen size
    screen_size = get_screen_resolution(root)

    # Offsets that need to subtract from the screen size
    width_offset = offset_x
    height_offset = offset_y

    # Find out required size for image
    available_w = screen_size[0] - width_offset
    avaialble_h = screen_size[1] - height_offset

    return (available_w, avaialble_h)


def get_config_out_file(in_file_path):
    """
    Generate path for saving config file
    """
    if not os.path.exists(in_file_path):
        file_name = os.path.basename(in_file_path)
        print("\n\033[31mError!\033[0m File", file_name, " does not exists.")
        return None

    def_ext = ".yml"
    file_types = [
        ("YAML Files", "*.yml"),
    ]

    initial_file = "configs.yml"

    out_file_path = file_saving_path(def_ext, file_types, initial_file)

    if not out_file_path:
        print("\033[31mWarning!\033[0m File destination path is not selected.")
        generate_separator("", "*")
        return None

    # Return if selected output config and input config paths is same.
    if os.path.dirname(out_file_path.replace("/", "\\")) == os.path.dirname(
        in_file_path.replace("/", "\\")
    ):
        return None

    return out_file_path


def select_file_saving_dir():
    """
    Allow user to select the directory for saving file.
    """
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    root.focus()
    file_path = fd.askdirectory()
    root.destroy()
    return file_path


def file_saving_path(def_ext, file_types, initial_file_name):
    """
    Generate path for saving a file
    """
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    root.focus()
    file_path = fd.asksaveasfilename(
        defaultextension=def_ext,
        filetypes=file_types,
        initialfile=initial_file_name,
        title="Please select file storage path.",
    )
    root.destroy()
    return file_path
