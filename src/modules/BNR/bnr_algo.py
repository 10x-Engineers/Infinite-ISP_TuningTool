"""
File: bnr_module.py
Description: Executes the algorithm to estimate bayer noise levels
Author: 10xEngineers
------------------------------------------------------------
"""
import tkinter
from tkinter import Entry, Tk, END
import csv
import numpy as np
from src.utils.gui_common_utils import file_saving_path, pop_up_msg, generate_separator


class BneAlgo:
    """
    Bayer Noise Estimation Algorithm
    """

    def __init__(self, raw_img_para, patches_info):
        self.raw_image_para = raw_img_para
        self.sub_rect_points = patches_info

    def generate_rgb_mask(self):
        """
        Generate R,G & B masks to generate raw R,B & G channels
        """
        # Loading raw image
        raw_data = self.raw_image_para.raw_image
        pattern = self.raw_image_para.bayer_pattern

        # dict will be creating 3 channel boolean type array of given shape with the name
        # tag like 'r_channel': [False False ....] , 'g_channel': [False False ....] ,
        # 'b_channel': [False False ....]
        channels = dict(
            (channel, np.zeros(raw_data.shape, dtype=bool)) for channel in "RGB"
        )

        # Following comment will create boolean masks for each channel r_channel,
        # g_channel and b_channel
        for channel, (y_channel, x_channel) in zip(
            pattern, [(0, 0), (0, 1), (1, 0), (1, 1)]
        ):
            channels[channel][y_channel::2, x_channel::2] = True

        # tuple will return 3 channel boolean pattern for r_channel,
        # g_channel and b_channel with True at corresponding value
        # For example in rggb pattern, the r_channel mask would then be
        # [ [ True, False, True, False], [ False, False, False, False]]
        raw_rgb = np.zeros([self.raw_image_para.height, self.raw_image_para.width, 3])
        mask_r, mask_g, mask_b = tuple(channels[c] for c in "RGB")

        # Adding 0.0001 just to keep data zeros different from masking zeros
        raw_data = np.float32(raw_data) + 0.0001

        # Generating R, G & B channels from raw image
        r_channel = raw_data * mask_r
        g_channel = raw_data * mask_g
        b_channel = raw_data * mask_b
        raw_rgb[:, :, 0] = r_channel
        raw_rgb[:, :, 1] = g_channel
        raw_rgb[:, :, 2] = b_channel
        return raw_rgb

    def apply_algo(self):
        """
        Apply Algorithm to the R,B & G raw channels
        """
        # Generating R, G, & B raw channels
        raw_rgb = self.generate_rgb_mask()

        # Normalization between 0-1
        raw_rgb = raw_rgb / (2**self.raw_image_para.bit_depth - 1)

        # Creating matrix to store standard deviations
        std_mat = np.zeros([6, 3])
        ind = 0

        # Extracting last six patches from each channel
        for i in range(18, 24, 1):
            point_at_time = self.sub_rect_points[i]
            start_point = point_at_time[0]
            end_point = point_at_time[1]

            # Extracting patches from each R, G & B bayer channels.
            crop_ch1_raw = raw_rgb[
                start_point[1] : end_point[1], start_point[0] : end_point[0], 0
            ]
            crop_ch2_raw = raw_rgb[
                start_point[1] : end_point[1], start_point[0] : end_point[0], 1
            ]
            crop_ch3_raw = raw_rgb[
                start_point[1] : end_point[1], start_point[0] : end_point[0], 2
            ]

            # Calculating std for each channel patch excluding masking zeros.
            std_mat[ind, 0] = np.std(crop_ch1_raw[crop_ch1_raw != 0])
            std_mat[ind, 1] = np.std(crop_ch2_raw[crop_ch2_raw != 0])
            std_mat[ind, 2] = np.std(crop_ch3_raw[crop_ch3_raw != 0])
            ind += 1

        self.display_matrix(std_mat)

    def display_matrix(self, matrix):
        """
        Display standard deviations to the GUI
        """
        root = Tk()
        table = tkinter.Frame(root)
        root.resizable(False, False)
        table.grid(row=0, column=0, padx=10, pady=10)

        root.title("Bayer Noise Levels")

        # Creating table to display
        # Create column headers
        table_to_dis = [("Patch", "R", "G", "B")]
        patch_nmb = 1

        # Adding data to the table
        for row in matrix:
            table_to_dis.append(([patch_nmb] + [f"{num:.4f}" for num in row]))
            patch_nmb += 1

        means = matrix.mean(axis=0)
        table_to_dis.append(
            ("Mean Std", f"{means[0]:.4f}", f"{means[1]:.4f}", f"{means[2]:.4f}")
        )

        # Font size to be used
        font_size = 12
        for i, row in enumerate(table_to_dis):
            for j, value in enumerate(row):
                if i == 0 and j == 0:
                    tab = Entry(
                        table,
                        fg="black",
                        font=("Arial", font_size, "bold"),
                        justify="center",
                    )
                    tab.grid(row=i, column=j)
                    tab.insert(END, value)
                    tab.configure(state="readonly")
                else:
                    tab = Entry(
                        table, fg="black", font=("Arial", font_size), justify="center"
                    )
                    tab.grid(row=i, column=j)
                    tab.insert(END, value)
                    tab.configure(state="readonly")

        # Add "Save" button
        save_button = tkinter.Button(
            root,
            text="Save",
            font=("Arial", font_size),
            command=lambda: self.save_to_csv(matrix, root),
        )
        save_button.grid(row=1, column=0, padx=10, pady=10)

        root.mainloop()

    def save_to_csv(self, matrix, root):
        """
        Save Data to CSV File
        """
        # Ask the user to select a file path to save the CSV file
        file_path = file_saving_path(
            ".csv",
            [
                ("CSV Files", "*.csv"),
            ],
            "bayer_standard_deviation.csv",
        )
        # Check if the user selected a file path

        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                means = matrix.mean(axis=0)
                writer.writerow(["Patch", "R", "G", "B"])
                for row in matrix:
                    writer.writerow([""] + [f"{num:.4f}" for num in row])
                writer.writerow([])
                writer.writerow(
                    [
                        "Mean std",
                        f"{means[0]:.4f}",
                        f"{means[1]:.4f}",
                        f"{means[2]:.4f}",
                    ]
                )

            print(f"CSV file saved to:\n {file_path}")
            root.destroy()
        else:
            pop_up_msg("File not saved.")
            print("\033[31mWarning!\033[0m File destination path is not selected.")
        generate_separator("", "*")
