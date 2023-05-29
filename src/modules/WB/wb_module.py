"""
File: wb_module.py
Description: Executes the module flow with the algorithm for the white balance
Author: 10xEngineers
------------------------------------------------------------
"""

import os
import tkinter as tk
from matplotlib import pyplot as plt
from src.modules.WB.white_balance_algo import WhiteBalanceAlgo
from src.utils.algo_common_utils import select_image_and_get_para, generate_separator
from src.utils.area_selection_frame import SelectAreaFrame as select_area_frame
from src.utils.read_yaml_file import ReadYMLFile
from src.utils.gui_common_utils import (
    determine_image_scale_factor,
    cv2_to_pil_image,
    select_file_saving_dir,
    get_tk_image,
    pop_up_msg,
    get_config_out_file,
)


class WhiteBalanceModule:
    """
    White Balance Module
    """

    def __init__(self, in_config_file):
        self.in_config_file = in_config_file
        self.raw_image_para = None
        self.root_apply_wb_frame = None
        self.r_gain = 0
        self.b_gain = 0
        self.white_balanced_image = None
        self.image_scale_factor = 2
        self.wb_algo = None
        self.selection_frame = None

    def display_gains(self):
        """
        Display the calculated gains
        """
        generate_separator("Calculated Gains", "-")
        print("R gain = ", self.r_gain)
        print("B gain = ", self.b_gain)

    def is_image_and_para_loaded(self):
        """
        To check if the image is loaded, if true store respective parameters.
        """
        file_type = (
            ("RAW Files (*.raw)", "*.raw"),
            (
                "PNG, JPEG, JPG Files (*.png, *.jpeg, *.jpg)",
                ("*.png", "*.jpeg", "*.jpg"),
            ),
            ("All Files (*.*)", ("*.raw", "*.png", "*.jpeg", "*.jpg")),
        )

        is_selected, self.raw_image_para = select_image_and_get_para(file_type)

        return is_selected

    def color_checker_selection_frame(self):
        """
        Open the color checker patches selection frame and return true
        if patches are drawn and saved using continue button
        otherwise return false
        """
        self.selection_frame = select_area_frame(self.raw_image_para.rgb_image)

        if self.selection_frame.data.is_data_saved:
            return True
        return False

    def implement_wb_algo(self):
        """
        Implement the white balance algorithm, for which get
        sub-rect points, rgb-image and execute the algo.
        """
        sub_rect_points = self.selection_frame.get_sub_rect_points()
        self.wb_algo = WhiteBalanceAlgo(self.raw_image_para.rgb_image, sub_rect_points)
        self.r_gain, self.b_gain = self.wb_algo.calculate_wb_gains()
        self.display_gains()

    def apply_cal_wb_gain(self):
        """
        Apply the calculated white balnce gains on the input image
        """
        self.white_balanced_image = self.wb_algo.apply_wb_gains(
            self.r_gain, self.b_gain
        )

    def in_out_images_display(self):
        """
        Design a frame and load input and output images parallel.
        """
        # Create a frame, set its title and make it not
        # resizeable on both axis
        root = tk.Tk()
        self.root_apply_wb_frame = root

        root.title("Comparison: Image Before and After White Balance")
        root.resizable(False, False)

        # Determine the image scale factor with respect to user screen
        # and then double it as need to display two images parallel.
        width_offset = 50
        height_offset = 50
        self.image_scale_factor = determine_image_scale_factor(
            root,
            self.raw_image_para.width,
            self.raw_image_para.height,
            width_offset,
            height_offset,
        )
        self.image_scale_factor *= 2

        # Create canvas to display input and output images separately and set their positions
        canvas1 = tk.Canvas(
            root,
            width=(self.raw_image_para.width / self.image_scale_factor),
            height=(self.raw_image_para.height / self.image_scale_factor),
        )
        canvas2 = tk.Canvas(
            root,
            width=(self.raw_image_para.width / self.image_scale_factor),
            height=(self.raw_image_para.height / self.image_scale_factor),
        )

        canvas1.grid(row=0, column=0, pady=10)
        canvas2.grid(row=0, column=1, pady=10)

        # Convert the image mats into PIL images
        input_pil_image = cv2_to_pil_image(self.raw_image_para.rgb_image)
        output_pil_image = cv2_to_pil_image(self.white_balanced_image)

        # Resize the pil images to fit on the image canvas
        input_pil_image = input_pil_image.resize(
            (
                int(self.raw_image_para.width / self.image_scale_factor),
                int(self.raw_image_para.height / self.image_scale_factor),
            )
        )

        output_pil_image = output_pil_image.resize(
            (
                int(self.raw_image_para.width / self.image_scale_factor),
                int(self.raw_image_para.height / self.image_scale_factor),
            )
        )

        # Convert the pil images into imagetk to display on canvas
        input_display_image = get_tk_image(input_pil_image)
        output_display_image = get_tk_image(output_pil_image)

        # Load image on the canvas
        canvas1.create_image(0, 0, image=input_display_image, anchor=tk.NW)
        canvas2.create_image(0, 0, image=output_display_image, anchor=tk.NW)

        # Set labels for input and output images on frame below the image canvas
        label_in_image = tk.Label(root, text="Before White Balance")
        label_out_image = tk.Label(root, text="After White Balance")

        label_in_image.grid(row=1, column=0, padx=10)
        label_out_image.grid(row=1, column=1, padx=10)

        # Make a button to save the images
        btn_save = tk.Button(
            master=root, text="Save Images", command=self.on_save_btn_clicked
        )
        btn_save.grid(row=2, columnspan=2, padx=10, pady=10)

        # Start the gui
        root.mainloop()

    def on_save_btn_clicked(self):
        """
        Save the input image and output (white balanced) images
        """
        file_path = select_file_saving_dir()
        if file_path:
            # Define images name
            in_file = "Input_Image.png"
            out_file = "Output_Image.png"

            # Get full path of images
            in_file_path = os.path.join(file_path, in_file)
            out_file_path = os.path.join(file_path, out_file)

            # Save images on the selected path
            plt.imsave(in_file_path, self.raw_image_para.rgb_image)
            plt.imsave(out_file_path, self.white_balanced_image)

            # Get the directory name from the file name and display at console.
            print("File saved at:", file_path)
            self.root_apply_wb_frame.destroy()
        else:
            pop_up_msg("Files not saved.")
            print("\033[31mWarning!\033[0m File destination path is not selected.")

    def save_wb_config_file(self):
        """
        Save the configuration file with calculated wb data.
        """
        out_file_path = get_config_out_file(self.in_config_file)

        if not out_file_path:
            return

        # Read the existing file, set the calculated black
        # levels and save the output file.
        yaml_file = ReadYMLFile(self.in_config_file)
        yaml_file.set_wb_data(r_gain=self.r_gain, b_gain=self.b_gain)
        yaml_file.save_file(out_file_path)

        # Get the directory name using the file name.
        print("File saved at:", os.path.dirname(out_file_path))
        generate_separator("", "*")
