"""
File: noise_reduction_2d.py
Description: Executes the algorithm to estimate luma noise levels
Author: 10xEngineers
------------------------------------------------------------
"""
import tkinter as tk
import csv
from PIL import Image, ImageTk
import numpy as np
from src.utils.gui_common_utils import (
    file_saving_path,
    pop_up_msg,
    generate_separator,
    determine_image_scale_factor,
)


class NEAlgo:
    """
    Bayer Noise Estimation Algorithm
    """

    def __init__(self, img, patches_info):
        self.rgb_cv_image = img
        self.sub_rect_points = patches_info

    def rgb_to_yuv(self, img):
        """
        RGB-to-YUV Colorspace conversion (Analog)
        """
        # for BT.601/407 analog
        rgb2yuv_mat = np.array(
            [
                [0.299, 0.587, 0.114],
                [-0.1687, -0.3313, 0.5],
                [0.5, -0.4187, -0.0813],
            ]
        )

        # normalize image to 0-1
        img = np.float32(img) / (2**8 - 1)

        # make nx3 2d matrix of image
        mat_2d = img.reshape((img.shape[0] * img.shape[1], 3))

        # convert to 3xn for matrix multiplication
        mat2d_t = mat_2d.transpose()

        # convert to YUV
        yuv_2d = np.matmul(rgb2yuv_mat, mat2d_t)

        # reshape the image back
        yuv2d_t = yuv_2d.transpose()

        img = yuv2d_t.reshape(img.shape).astype(np.float32)
        return img

    def apply_algo(self):
        """
        Apply algorithm to the luminance channel
        to estimate noise levels using last 6
        gray patches
        """
        rgb_wb = self.rgb_cv_image
        yuv_image = self.rgb_to_yuv(rgb_wb)
        lum_y = yuv_image[:, :, 0]
        std = np.zeros(
            [
                6,
            ]
        )
        ind = 0
        for _, patch_cord in enumerate(self.sub_rect_points[-6:]):
            start_point = patch_cord[0]
            end_point = patch_cord[1]

            cropped_image = lum_y[
                start_point[1] : end_point[1], start_point[0] : end_point[0]
            ]
            std[ind] = np.std(cropped_image)
            ind += 1

        self.display_patches(rgb_wb, std)

    def display_patches(self, rgb_wb, std):
        """
        Display standard deviations along with the last 6 patches
        """
        root = tk.Tk()
        root.title("Luma Noise Levels")
        root.resizable(False, False)

        # Create a table using a grid layout
        patches = tk.Frame(root)
        patches.grid(row=0, column=0, padx=10, pady=10)

        for count_i, patch_coord in enumerate(self.sub_rect_points[-6:]):
            patch = rgb_wb[
                patch_coord[0][1] : patch_coord[1][1],
                patch_coord[0][0] : patch_coord[1][0],
            ]

            # Convert the OpenCV image to PIL format
            pil_image = Image.fromarray(patch)

            image_scale_factor = determine_image_scale_factor(
                root, patch.shape[1] * 6, patch.shape[0] * 6, 50, 50
            )
            # Create a canvas for displaying the image
            canvas = tk.Canvas(
                patches,
                width=patch.shape[1] / image_scale_factor,
                height=patch.shape[0] / image_scale_factor,
            )
            canvas.grid(row=0, column=count_i, padx=10, pady=10)

            # Resize the image to fit the canvas
            pil_image = pil_image.resize(
                (
                    (
                        int(patch.shape[1] / image_scale_factor),
                        int(patch.shape[0] / image_scale_factor),
                    )
                ),
                Image.ANTIALIAS,
            )

            # Create a Tkinter-compatible image
            tk_image = ImageTk.PhotoImage(pil_image)

            # Display the image on the canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            canvas.image = tk_image

            stddev_text = f"Patch {count_i + 1} \nstd: {std[count_i]:.4f}"
            stddev_label = tk.Label(patches, text=stddev_text, font=("Arial", 12))
            stddev_label.grid(row=1, column=count_i, padx=10, pady=10)

        # Displaying mean
        stddev_label = tk.Label(
            root, text=f"Mean std: {np.mean(std):.4f}", font=("Arial", 12)
        )
        stddev_label.grid(row=1, column=0, padx=10, pady=10)

        # Add "Save" button
        save_button = tk.Button(
            root,
            text="Save",
            font=("Arial", 12),
            command=lambda: self.save_to_csv(std, root),
        )
        save_button.grid(row=2, column=0, padx=10, pady=10)

        root.mainloop()

    def save_to_csv(self, std, root):
        """
        Save Data to CSV File
        """
        # Ask the user to select a file path to save the CSV file
        file_path = file_saving_path(
            ".csv",
            [
                ("CSV Files", "*.csv"),
            ],
            "luma_standard_deviations.csv",
        )
        # Check if the user selected a file path
        if file_path:
            # Create a list of dictionaries to hold patch information
            patch_data = []
            for count_i, stddev in enumerate(std):
                patch_data.append({"Patch": count_i + 1, "StdDev": stddev})

            # Calculate the mean of all standard deviations
            mean_stddev = np.mean(std)
            patch_data.append({})
            patch_data.append({"Patch": "Mean std", "StdDev": mean_stddev})

            # Write the patch data to a CSV file
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                fieldnames = ["Patch", "StdDev"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(patch_data)

            print(f"CSV file saved to:\n {file_path}")
            root.destroy()
        else:
            pop_up_msg("File not saved.")
            print("\033[31mWarning!\033[0m File destination path is not selected.")
        generate_separator("", "*")
