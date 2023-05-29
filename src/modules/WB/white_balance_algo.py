"""
File: white_balance_algo.py
Description: Executes the algorithm for the white balance
Author: 10xEngineers
------------------------------------------------------------
"""

import numpy as np
import cv2
from src.utils.algo_common_utils import extract_patches_mat, cal_patches_avg


class WhiteBalanceAlgo:
    """
    White Balance Algorithm
    """

    def __init__(self, rgb_image, patches_points):
        """
        Here following steps are performed:
        1) Extract/ crop the patches of all the 24 patches and save into a mat array.
        2) Calculate average of each channel using saved mat array.
        3) Get the avg. of gray row only.
        """

        self.rgb_image = rgb_image
        self.patches_points = patches_points

        patches_mat = extract_patches_mat(self.rgb_image, self.patches_points)
        self.r_avg, self.g_avg, self.b_avg = cal_patches_avg(patches_mat)
        self.r_avg_gray, self.g_avg_gray, self.b_avg_gray = self.get_gray_row_avg(
            self.r_avg, self.g_avg, self.b_avg
        )

    def calculate_wb_gains(self):
        """
        Calculate the wb gains using rgb_image and given
        average r,g, and b arrays.
        """
        wb_r = np.zeros(len(self.r_avg_gray))
        wb_b = np.zeros(len(self.r_avg_gray))

        for count, _ in enumerate(self.r_avg_gray):
            if self.r_avg_gray[count] == 0:
                wb_r[count] = 1
            else:
                wb_r[count] = self.g_avg_gray[count] / self.r_avg_gray[count]

            if self.b_avg_gray[count] == 0:
                wb_b[count] = 1
            else:
                wb_b[count] = self.g_avg_gray[count] / self.b_avg_gray[count]

        wr_mean = np.mean(wb_r)
        wb_mean = np.mean(wb_b)

        # Round off value upto 4 decimal
        r_gain = float(round(wr_mean, 4))
        b_gain = float(round(wb_mean, 4))

        return r_gain, b_gain

    def apply_wb_gains(self, r_gain, b_gain):
        """
        Apply the given white balnce gains on the rgb image
        """

        # Split rgb-image into three channels and convert them into float
        # as gains are in float.
        r_channel, g_channel, b_channel = np.float32(cv2.split(self.rgb_image))

        # Apply gain to r and b channels.
        r_channel = r_channel * r_gain
        b_channel = b_channel * b_gain

        # Merged the channels to get the white balanced image.
        white_balanced_image = cv2.merge([r_channel, g_channel, b_channel])

        # Clip the values and keep between 0-255.
        white_balanced_image = np.clip(white_balanced_image, 0, 255).astype(np.uint8)

        return white_balanced_image

    def execute(self):
        """
        This function calculate the wb, apply the calcualted gains on the rgb
         image and return the white balanced image.
        """
        r_gain, b_gain = self.calculate_wb_gains()
        white_balanced_image = self.apply_wb_gains(r_gain, b_gain)
        return white_balanced_image

    def get_gray_row_avg(self, r_avg, g_avg, b_avg):
        """
        Extract the only gray row patches except first and last patch
         which are necessary for wb calculation.
        """

        r_avg_gray = np.array(r_avg[19:23])
        g_avg_gray = np.array(g_avg[19:23])
        b_avg_gray = np.array(b_avg[19:23])

        return r_avg_gray, g_avg_gray, b_avg_gray

    def get_patches_averages(self):
        """
        Get mean values from the patches
        """
        return self.r_avg, self.g_avg, self.b_avg
