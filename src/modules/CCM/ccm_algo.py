"""
File: ccm_algo.py
Description: Executes the algorithm to calculate ColorChecker matrix
Author: 10xEngineers
------------------------------------------------------------
"""
import os
import warnings
import tkinter as tk
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import minimize
from skimage import color
from src.menu.menu_common_func import end_tuning_tool
from src.modules.WB.white_balance_algo import WhiteBalanceAlgo as WBAlgo
from src.utils.gui_common_utils import (
    generate_separator,
    determine_image_scale_factor,
    cv2_to_pil_image,
    get_tk_image,
    select_file_saving_dir,
    pop_up_msg,
)


class ColorCorrectionMatrixAlgo:
    """
    Color Correction Matrix (CCM)
    """

    def __init__(self):
        """
        At the start of the algorithm, first of all,
         reads the input reference files.
        """
        self.data = CcmAlgoStorage()
        self.load_ref_files()

    def load_ref_files(self):
        """
        Loading reference files
        """
        data = self.data

        # Load the reference file (refD65Lab.txt) that is present in
        # the "Input Files" directory of this project.
        ref_file_dir = "app_data"
        file_ref_d65_lab = "refD65Lab.txt"
        file_ref_d65_lin = "refD65Lin.txt"

        # Join file and dir and load file if file exists
        ref_d65_lab_path = os.path.join(os.getcwd(), ref_file_dir, file_ref_d65_lab)
        ref_d65_lin_path = os.path.join(os.getcwd(), ref_file_dir, file_ref_d65_lin)

        # Check and exit the project if refD65Lab file does not exit.
        if os.path.exists(ref_d65_lab_path):
            data.ref_d65_lab = self.read_input_file(ref_d65_lab_path)
        else:
            print(
                "\n\033[31mError!\033[0m File (refD65Lab.txt) does not exist in ' "
                + ref_file_dir
                + '" directory.',
            )
            end_tuning_tool()

        # Check and exit the program if refD65Lin file does not exit.
        if os.path.exists(ref_d65_lin_path):
            data.ref_d65_lin = self.read_input_file(ref_d65_lin_path)
        else:
            print(
                "\n\033[31mError!\033[0m File (refD65Lin.txt) does not exist in '"
                + ref_file_dir
                + '" directory.'
            )
            end_tuning_tool()

        self.data = data

    def get_input_image_data(self):
        """
        This function returns a mat by joining the data of the 24
         obtained from the input image and taking its transpose.
        """
        input_mat = np.column_stack((self.data.r_avg, self.data.g_avg, self.data.b_avg))
        input_mat = np.transpose(input_mat)
        return input_mat

    def cosfunction(self, x_var, data):
        """
        Define cosfunction that needs to minimize.
        """

        # Separate the parameters from the data array
        input_mat = data[0]
        ref_lab = data[1]
        amp_fact = data[2]

        # Reshape initial values (x0)
        ccm = x_var.reshape((3, 3))

        # Muliply the app_factor with input mat
        modified_input_mat = amp_fact[0][0] * input_mat

        # Get the predicted ccm
        pred_ccm = np.matmul(ccm, modified_input_mat)

        # Get the sign of the predicted ccm mat to avoid warning when applying gamma
        mat_sign = np.sign(pred_ccm)

        # Convert negative values of the predicted ccm into positive
        mat_abs = np.abs(pred_ccm)

        # Apply gamma on positive pred-ccm
        gamma_applied = np.power(mat_abs, (0.45))

        # Give back the sign of pred-ccm mat
        actual_pred_ccm = np.multiply(mat_sign, gamma_applied)

        # Convert from rgb to lab color space
        lab_ccm = color.rgb2lab(np.transpose(actual_pred_ccm))
        lab_ccm = np.transpose(lab_ccm)

        # Calculate the error
        error = self.calculate_error(ref_lab, lab_ccm)

        # Take the square and mean of the error.
        error = error * error
        mean_error = np.mean(error)

        return mean_error

    def const_row1(self, x_var):
        """
        These constrained keeps the sum equal to 1 for each row.
        """
        sum_sq = 1
        for i in range(3):
            sum_sq = sum_sq - x_var[i]
        return sum_sq

    def const_row2(self, x_var):
        """
        These constrained keeps the sum equal to 1 for each row.
        """
        sum_sq = 1
        for i in range(3):
            sum_sq = sum_sq - x_var[3 + i]
        return sum_sq

    def const_row3(self, x_var):
        """
        These constrained keeps the sum equal to 1 for each row.
        """
        sum_sq = 1
        for i in range(3):
            sum_sq = sum_sq - x_var[6 + i]
        return sum_sq

    def const_diagonal1(self, x_var):
        """
        These constrained keeps the diagonal greater than 1
        """
        return x_var[0] - 1.0

    def const_diagonal2(self, x_var):
        """
        These constrained keeps the diagonal greater than 1
        """
        return x_var[4] - 1.0

    def const_diagonal3(self, x_var):
        """
        These constrained keeps the diagonal greater than 1
        """
        return x_var[8] - 1.0

    def apply_wb_gains_on_patches(self, r_gain, b_gain):
        """
        Apply the wb gains on the input patches data.
        """
        data = self.data

        data.r_avg = [data.r_avg[i] * r_gain for i in range(len(data.r_avg))]
        data.b_avg = [data.b_avg[i] * b_gain for i in range(len(data.b_avg))]

        self.data = data

    def read_input_file(self, file_name):
        """
        This function takes the input reference files and returns the read data.
        As the files contains 24 rows and 3 columns with floating points,
        so if anything does not satisfy the format, the program will exit.
        """
        # Open the file in reading mode
        with open(file_name, "r") as fil:
            file = fil.read()

            # Split file into lines
            lines = file.split("\n")

            # Check number of lines
            if len(lines) != 24:
                print(
                    '\n\033[31mError!\033[0m Invalid file "',
                    os.path.basename(file_name),
                    '" data.',
                )
                end_tuning_tool()

            # Data storage array
            data = []

            for line in lines:
                # Split the values in each line
                values = line.split()

                # Check number of values in a line
                if len(values) != 3:
                    print(
                        '\n\033[31mError!\033[0m Invalid file "',
                        os.path.basename(file_name),
                        '" data.',
                    )
                    end_tuning_tool()
                # Convert the values to float
                try:
                    values = [float(val) for val in values]
                except:
                    print(
                        '\n\033[31mError!\033[0m Invalid file "',
                        os.path.basename(file_name),
                        '" data.',
                    )
                    end_tuning_tool()

                data.append(values)
        data = np.array(data)
        return data

    def calculate_ccm_matrix(self):
        """
        Obtained all the required data/arguments for the algorithm,
         set constraints, ran the cosfunction and displayed the results.
        """
        data = self.data

        # Collect the required data for cosfunction
        arguments = [
            self.get_input_image_data(),
            np.transpose(data.ref_d65_lab),
            self.cal_amp_fact(),
        ]

        # Apply equality constained on each row
        row1_wb = {"type": "eq", "fun": self.const_row1}
        row2_wb = {"type": "eq", "fun": self.const_row2}
        row3_wb = {"type": "eq", "fun": self.const_row3}

        # Apply inquality constained on diagonals
        diag1 = {"type": "ineq", "fun": self.const_diagonal1}
        diag2 = {"type": "ineq", "fun": self.const_diagonal2}
        diag3 = {"type": "ineq", "fun": self.const_diagonal3}

        # Combine constraints
        cons_with_wb = [row1_wb, row2_wb, row3_wb, diag1, diag2, diag3]
        cons_without_wb = [diag1, diag2, diag3]

        # Apply the minimze function according to the user's selected parameters.
        if data.maintain_wb:
            sol = minimize(
                self.cosfunction,
                data.initial_cccm,
                args=arguments,
                method="trust-constr",
                constraints=cons_with_wb,
            )
        else:
            sol = minimize(
                self.cosfunction,
                data.initial_cccm,
                args=arguments,
                method="trust-constr",
                constraints=cons_without_wb,
            )

        # Convert the resultant-ccm array into a 3x3 mat
        ccm_matrix_floating = sol.x.reshape((3, 3))

        # Convert the resultant-ccm into int values
        int_muliplier = np.power(2, 10)
        ccm_matrix_int = ccm_matrix_floating * int_muliplier
        ccm_matrix_int = np.round(ccm_matrix_int)
        data.ccm_float = ccm_matrix_floating

        # Separate ccm matrix into red_channel,green_channel and blue_channel channels
        data.ccm_r = ccm_matrix_int[0]
        data.ccm_g = ccm_matrix_int[1]
        data.ccm_b = ccm_matrix_int[2]

        # Convert np int into simple int value
        data.ccm_r = [int(x) for x in data.ccm_r]
        data.ccm_g = [int(x) for x in data.ccm_g]
        data.ccm_b = [int(x) for x in data.ccm_b]

        self.data = data
        return ccm_matrix_floating

    def display_ccm_matrix(self, ccm_matrix_floating):
        """
        Display CCM Matrix
        """
        data = self.data

        ccm_r = np.around(ccm_matrix_floating[0], decimals=4)
        ccm_g = np.around(ccm_matrix_floating[1], decimals=4)
        ccm_b = np.around(ccm_matrix_floating[2], decimals=4)

        # Display calculated ccm.
        generate_separator("Result", "*")
        print("Calculated Color Correction Matrix with following parameters:")

        if data.is_delta_e:
            print("1. Error matrix: Delta Eab")
        else:
            print("1. Error matrix: Delta Cab")

        if data.maintain_wb:
            print("2. White balance: Maintained")
        else:
            print("2. White balance: Not Maintained")

        generate_separator("Integer CCM", "-")
        print("Corrected red   = ", data.ccm_r)
        print("Corrected green = ", data.ccm_g)
        print("Corrected blue  = ", data.ccm_b)

        generate_separator("Floating-point CCM", "-")
        print("Corrected red   = ", ccm_r)
        print("Corrected green = ", ccm_g)
        print("Corrected blue  = ", ccm_b)
        self.data = data

    def find_initial_ccm(self):
        """
        Calculated the initial ccm matrix for the optimizer.
        """
        data = self.data
        mean_r_avg = np.mean(data.r_avg)
        mean_g_avg = np.mean(data.g_avg)
        mean_b_avg = np.mean(data.b_avg)

        # Zero error check for division
        if mean_r_avg == 0:
            mean_r_avg = np.mean(data.ref_d65_lin[:, 0])
        if mean_g_avg == 0:
            mean_g_avg = np.mean(data.ref_d65_lin[:, 1])
        if mean_b_avg == 0:
            mean_b_avg = np.mean(data.ref_d65_lin[:, 2])

        # Get diagonal values
        red_channel = np.mean(data.ref_d65_lin[:, 0]) / mean_r_avg
        green_channel = np.mean(data.ref_d65_lin[:, 1]) / mean_g_avg
        blue_channel = np.mean(data.ref_d65_lin[:, 2]) / mean_b_avg

        # Clear initial ccm array
        data.initial_cccm = []

        # Set values
        data.initial_cccm = [red_channel, 0, 0, 0, green_channel, 0, 0, 0, blue_channel]

        self.data = data

    def get_ccm_matrix(self):
        """
        Return the calculated ccm matrix as red_channel, green_channel and blue_channel lists
        """
        return (self.data.ccm_r, self.data.ccm_g, self.data.ccm_b)

    def cal_amp_fact(self):
        """
        Calculate the amp-factor
        """
        data = self.data

        input_black_patch_avg = np.mean(
            [data.r_avg[23], data.b_avg[23], data.g_avg[23]]
        )

        # Zero division check
        if input_black_patch_avg == 0:
            amp_fact = 1
        else:
            ref_black_patch_avg = np.mean(data.ref_d65_lin[23])
            amp_fact = ref_black_patch_avg / input_black_patch_avg

        amp_fact_mat = np.array([[amp_fact]])

        self.data = data
        return amp_fact_mat

    def set_parameters(self, points, rgb_image, algo, maintain_wb, wb_flag):
        """
        Set parameters
        """
        data = self.data

        data.sub_rect_points = points
        data.rgb_image = rgb_image
        data.is_delta_e = algo
        data.maintain_wb = maintain_wb
        data.wb_flag = wb_flag

        self.data = data

    def execute_algo(self):
        """
        Get requirements for algorithm and implement it
        """
        data = self.data
        wb_flag = data.wb_flag
        wb_algo = WBAlgo(data.rgb_image, data.sub_rect_points)
        data.r_avg, data.g_avg, data.b_avg = wb_algo.get_patches_averages()

        # Check if white balance flag is true
        if wb_flag is True:
            r_gain, b_gain = wb_algo.calculate_wb_gains()
            data.white_balanced_image = wb_algo.apply_wb_gains(r_gain, b_gain)
            self.apply_wb_gains_on_patches(r_gain, b_gain)
        else:
            data.white_balanced_image = data.rgb_image

        # Finding initial CCM guess
        self.find_initial_ccm()
        ccm_mat = self.calculate_ccm_matrix()
        self.display_ccm_matrix(ccm_mat)
        self.ccm_output_frame()

        self.data = data

    def calculate_error(self, ref_lab, lab_img):
        """
        Calcuate the error depending on user's selected type.
        """
        data = self.data

        # Define a mat to store the error crossponding to 24 patches.
        error_mat = np.ones((24, 1), dtype=np.float64)

        if not data.is_delta_e:
            for i in range(data.total_patches):
                error_mat[i, 0] = self.delta_c00(
                    [ref_lab[0, i], ref_lab[1, i], ref_lab[2, i]],
                    [lab_img[0, i], lab_img[1, i], lab_img[2, i]],
                )
        else:
            for i in range(data.total_patches):
                error_mat[i, 0] = self.delta_e00(
                    [ref_lab[0, i], ref_lab[1, i], ref_lab[2, i]],
                    [lab_img[0, i], lab_img[1, i], lab_img[2, i]],
                )
        self.data = data
        return error_mat

    def delta_e00(
        self, lab_color_vector, lab_color_array, kl_var=1, kc_var=1, kh_var=1
    ):
        """
        Calculates the Delta E (CIE2000) of two colors.
        """
        warnings.simplefilter("ignore")
        l_in_lab, a_in_lab, b_in_lab = lab_color_vector

        avg_lp = (l_in_lab + lab_color_array[0]) / 2.0

        c1_var = np.sqrt(np.sum(np.power(lab_color_vector[1:], 2)))
        c2_var = np.sqrt(np.sum(np.power(lab_color_array[1:], 2)))

        avg_c1_c2 = (c1_var + c2_var) / 2.0

        g_value = 0.5 * (
            1
            - np.sqrt(
                np.power(avg_c1_c2, 7.0)
                / (np.power(avg_c1_c2, 7.0) + np.power(25.0, 7.0))
            )
        )

        a1p = (1.0 + g_value) * a_in_lab
        a2p = (1.0 + g_value) * lab_color_array[1]

        c1p = np.sqrt(np.power(a1p, 2) + np.power(b_in_lab, 2))
        c2p = np.sqrt(np.power(a2p, 2) + np.power(lab_color_array[2], 2))

        avg_c1p_c2p = (c1p + c2p) / 2.0

        h1p = np.degrees(np.arctan2(b_in_lab, a1p))
        h1p += (h1p < 0) * 360

        h2p = np.degrees(np.arctan2(lab_color_array[2], a2p))
        h2p += (h2p < 0) * 360

        avg_hp = (((np.fabs(h1p - h2p) > 180) * 360) + h1p + h2p) / 2.0

        t_mat = (
            1
            - 0.17 * np.cos(np.radians(avg_hp - 30))
            + 0.24 * np.cos(np.radians(2 * avg_hp))
            + 0.32 * np.cos(np.radians(3 * avg_hp + 6))
            - 0.2 * np.cos(np.radians(4 * avg_hp - 63))
        )

        diff_h2p_h1p = h2p - h1p
        delta_hp = diff_h2p_h1p + (np.fabs(diff_h2p_h1p) > 180) * 360
        delta_hp -= (h2p > h1p) * 720

        delta_lp = lab_color_array[0] - l_in_lab
        delta_cp = c2p - c1p
        delta_hp = 2 * np.sqrt(c2p * c1p) * np.sin(np.radians(delta_hp) / 2.0)

        s_l = 1 + (
            (0.015 * np.power(avg_lp - 50, 2))
            / np.sqrt(20 + np.power(avg_lp - 50, 2.0))
        )
        s_c = 1 + 0.045 * avg_c1p_c2p
        s_h = 1 + 0.015 * avg_c1p_c2p * t_mat

        delta_ro = 30 * np.exp(-(np.power(((avg_hp - 275) / 25), 2.0)))
        r_c = np.sqrt(
            (np.power(avg_c1p_c2p, 7.0))
            / (np.power(avg_c1p_c2p, 7.0) + np.power(25.0, 7.0))
        )
        r_t = -2 * r_c * np.sin(2 * np.radians(delta_ro))

        return np.sqrt(
            np.power(delta_lp / (s_l * kl_var), 2)
            + np.power(delta_cp / (s_c * kc_var), 2)
            + np.power(delta_hp / (s_h * kh_var), 2)
            + r_t * (delta_cp / (s_c * kc_var)) * (delta_hp / (s_h * kh_var))
        )

    def delta_c00(
        self, lab_color_vector, lab_color_array, kl_var=1, kc_var=1, kh_var=1
    ):
        """
        Calculates the Delta E (CIE2000) of two colors.
        """
        warnings.simplefilter("ignore")
        _, a_in_lab, b_in_lab = lab_color_vector

        # avg_lp = (l_in_lab + lab_color_array[0]) / 2.0

        c1_var = np.sqrt(np.sum(np.power(lab_color_vector[1:], 2)))
        c2_var = np.sqrt(np.sum(np.power(lab_color_array[1:], 2)))

        avg_c1_c2 = (c1_var + c2_var) / 2.0

        g_value = 0.5 * (
            1
            - np.sqrt(
                np.power(avg_c1_c2, 7.0)
                / (np.power(avg_c1_c2, 7.0) + np.power(25.0, 7.0))
            )
        )

        a1p = (1.0 + g_value) * a_in_lab
        a2p = (1.0 + g_value) * lab_color_array[1]

        c1p = np.sqrt(np.power(a1p, 2) + np.power(b_in_lab, 2))
        c2p = np.sqrt(np.power(a2p, 2) + np.power(lab_color_array[2], 2))

        avg_c1p_c2p = (c1p + c2p) / 2.0

        h1p = np.degrees(np.arctan2(b_in_lab, a1p))
        h1p += (h1p < 0) * 360

        h2p = np.degrees(np.arctan2(lab_color_array[2], a2p))
        h2p += (h2p < 0) * 360

        avg_hp = (((np.fabs(h1p - h2p) > 180) * 360) + h1p + h2p) / 2.0

        t_mat = (
            1
            - 0.17 * np.cos(np.radians(avg_hp - 30))
            + 0.24 * np.cos(np.radians(2 * avg_hp))
            + 0.32 * np.cos(np.radians(3 * avg_hp + 6))
            - 0.2 * np.cos(np.radians(4 * avg_hp - 63))
        )

        diff_h2p_h1p = h2p - h1p
        delta_hp = diff_h2p_h1p + (np.fabs(diff_h2p_h1p) > 180) * 360
        delta_hp -= (h2p > h1p) * 720

        # delta_lp = lab_color_array[0] - l_in_lab
        delta_cp = c2p - c1p
        delta_hp = 2 * np.sqrt(c2p * c1p) * np.sin(np.radians(delta_hp) / 2.0)

        # s_l = 1 + (
        #     (0.015 * np.power(avg_lp - 50, 2))
        #     / np.sqrt(20 + np.power(avg_lp - 50, 2.0))
        # )
        s_c = 1 + 0.045 * avg_c1p_c2p
        s_h = 1 + 0.015 * avg_c1p_c2p * t_mat

        delta_ro = 30 * np.exp(-(np.power(((avg_hp - 275) / 25), 2.0)))
        r_c = np.sqrt(
            (np.power(avg_c1p_c2p, 7.0))
            / (np.power(avg_c1p_c2p, 7.0) + np.power(25.0, 7.0))
        )
        r_t = -2 * r_c * np.sin(2 * np.radians(delta_ro))

        return np.sqrt(
            np.power(delta_cp / (s_c * kc_var), 2)
            + np.power(delta_hp / (s_h * kh_var), 2)
            + r_t * (delta_cp / (s_c * kc_var)) * (delta_hp / (s_h * kh_var))
        )

    def apply_ccm(self):
        """
        Apply CCM Params
        """
        data = self.data

        image = data.white_balanced_image

        img1 = image.reshape(((image.shape[0] * image.shape[1], 3)))

        # keeping imatest convention of colum sum to 1 mat. O*A => A = ccm
        out = np.matmul(img1, data.ccm_float.transpose())

        # Normalize the out mat between 0 and 1
        out = out / 255

        # Apply gamma 2.2
        out = np.power(out, (0.45))

        # Clip and map image on 8 bits.
        out = np.uint8(np.clip(out, 0, 1) * 255)

        # Reshaped the image
        out = out.reshape(image.shape)

        return out

    def ccm_output_frame(self):
        """
        Design a frame and load input and output images parallel.
        """
        # Create a frame, set its title and make it not
        # resizeable on both axis
        data = self.data
        input_image = data.rgb_image
        output_image = self.apply_ccm()
        data.ccm_image = output_image

        image_height, image_width, _ = input_image.shape

        # Define frame
        root = tk.Tk()
        data.root = root

        root.title("Comparison: Image Before and After CCM Applied")
        root.resizable(False, False)

        # Determine the image scale factor with respect to user screen
        # and then double it as need to display two images parallel.
        width_offset = 50
        height_offset = 50
        image_scale_factor = determine_image_scale_factor(
            root,
            image_width,
            image_height,
            width_offset,
            height_offset,
        )

        # As need to display two images
        image_scale_factor *= 2

        # Create canvas to display input and output images separately and set their positions
        canvas1 = tk.Canvas(
            root,
            width=(image_width / image_scale_factor),
            height=(image_height / image_scale_factor),
        )

        canvas2 = tk.Canvas(
            root,
            width=(image_width / image_scale_factor),
            height=(image_height / image_scale_factor),
        )

        canvas1.grid(row=0, column=0, pady=10)
        canvas2.grid(row=0, column=1, pady=10)

        # Convert the image mats into PIL images
        input_pil_image = cv2_to_pil_image(input_image)
        output_pil_image = cv2_to_pil_image(output_image)

        # Resize the pil images to fit on the image canvas
        input_pil_image = input_pil_image.resize(
            (
                int(image_width / image_scale_factor),
                int(image_height / image_scale_factor),
            )
        )

        output_pil_image = output_pil_image.resize(
            (
                int(image_width / image_scale_factor),
                int(image_height / image_scale_factor),
            )
        )

        # Convert the pil images into imagetk to display on canvas
        input_display_image = get_tk_image(input_pil_image)
        output_display_image = get_tk_image(output_pil_image)

        # Load image on the canvas
        canvas1.create_image(0, 0, image=input_display_image, anchor=tk.NW)
        canvas2.create_image(0, 0, image=output_display_image, anchor=tk.NW)

        # Set labels for input and output images on frame below the image canvas
        label_in_image = tk.Label(root, text="Before CCM")
        label_out_image = tk.Label(root, text="After CCM")

        label_in_image.grid(row=1, column=0, padx=10)
        label_out_image.grid(row=1, column=1, padx=10)

        # Make a button to save the images
        btn_save = tk.Button(
            master=root, text="Save Images", command=self.on_save_btn_clicked
        )

        btn_save.grid(row=2, columnspan=2, padx=10, pady=10)

        self.data = data

        # Start the gui
        root.mainloop()

    def on_save_btn_clicked(self):
        """
        Save the input image and output (white balanced) images
        """
        file_path = select_file_saving_dir()
        if file_path:
            data = self.data

            # Define images name
            in_file = "Input_Image_without_CCM.png"
            out_file = "Output_Image_with_CCM.png"

            # Get full path of images
            in_file_path = os.path.join(file_path, in_file)
            out_file_path = os.path.join(file_path, out_file)

            # Save images on the selected path
            plt.imsave(in_file_path, data.rgb_image)
            plt.imsave(out_file_path, data.ccm_image)

            # Get the directory name from the file name and display at console.
            generate_separator("", "*")
            print("\nFile saved at:", file_path)
            data.root.destroy()
        else:
            pop_up_msg("\nFiles not saved.")
            print("\n\033[31mWarning!\033[0m File destination path is not selected.")


class CcmAlgoStorage:
    """
    This class contains all the data variables
     that are used in CCM algo.
    """

    def __init__(self):
        self.rgb_image = None
        self.white_balanced_image = None
        self.ccm_image = None

        self.root = None

        self.sub_rect_points = []
        self.r_avg = []
        self.g_avg = []
        self.b_avg = []
        self.ref_d65_lab = None
        self.ref_d65_lin = None
        self.total_patches = 24

        self.ccm_r = []
        self.ccm_g = []
        self.ccm_b = []

        self.ccm_float = []

        self.initial_cccm = []
        self.maintain_wb = False
        self.wb_flag = False
        self.is_delta_e = True
