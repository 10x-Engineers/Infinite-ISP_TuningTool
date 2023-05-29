"""
File: gamma_module.py
Description: Executes the gamma curves plotting module
Author: 10xEngineers
------------------------------------------------------------
"""
import math
import os
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.utils.gui_common_utils import (
    cal_available_screen_size,
    file_saving_path,
    pop_up_msg,
    generate_separator,
)
from src.utils.read_yaml_file import ReadYMLFile
from src.utils.algo_common_utils import select_file


class GammaModule:
    """
    Gamma Module
    """

    def __init__(self, in_config_file):
        self.gamma_lut = None
        self.bpp = None

        # Path to configuration file
        self.config_path = in_config_file

    def is_config_exists(self):
        """
        Check that either config.yml exits in the config folder or not
        """
        if os.path.exists(self.config_path):
            return True
        else:
            return False

    def display_gamma_plots(self):
        """
        Create tinker window for plots
        """
        root = tk.Tk()
        # Calculate available screen size
        width_offset = 200
        height_offset = 150
        graph_size = cal_available_screen_size(root, width_offset, height_offset)
        # Create plot
        gamma_graph = plt.Figure(
            figsize=(graph_size[0] // 100, graph_size[1] // 100), dpi=100
        )
        root.title("Gamma Curves")
        # Open dialog box in the foreground
        root.attributes("-topmost", True)

        # Generate the plot
        self.create_graph(gamma_graph)

        # Add plot to Tkinter window
        canvas = FigureCanvasTkAgg(gamma_graph, master=root)

        canvas.draw()
        canvas.get_tk_widget().pack()

        # Make a button to save the images
        btn_save = tk.Button(
            root,
            text="Save Graphs",
            command=lambda: self.on_save_btn_clicked(gamma_graph, root),
        )
        btn_save.pack(padx=10, pady=10)
        # Run Tkinter mainloop
        root.mainloop()

    def create_graph(self, gamma_graph):
        """
        Create gamma graphs
        """
        # Calculate total values
        total_values = len(self.gamma_lut)

        # Generated gamma 2.2
        gamma_lut_2_2 = []
        for x_iter in range(total_values):
            value = (total_values - 1) * math.pow(
                (x_iter / (total_values - 1)), 1 / 2.2
            )
            gamma_lut_2_2.append(value)

        # Generate intensity levels for x_iter axis
        gamma_x = np.arange(total_values)

        # Here set 10 markers on the curve between and including start and end values.
        total_markers = 10

        # Calculate the values on which need to set markers then
        mark_values = np.linspace(0, (total_values - 1), num=total_markers, dtype=int)

        # Generate mark array equal to curve points and set true where need to put a mark
        mask = np.zeros(len(gamma_x - 1), dtype=bool)
        mask[mark_values] = True

        plotting_area = gamma_graph.add_subplot(111)
        # plotting_area.plot(gamma_x, self.gamma_lut)
        # plotting_area.plot(gamma_x, gamma_lut_2_2)
        plotting_area.grid()
        # Plot the curve with marks
        plotting_area.plot(
            gamma_x,
            self.gamma_lut,
            "-o",
            color="blue",
            markerfacecolor="red",
            markeredgecolor="red",
            markersize=6,
            markevery=mask,
            label="User-defined Gamma",
        )

        plotting_area.plot(
            gamma_x,
            gamma_lut_2_2,
            "-*",
            color="green",
            markerfacecolor="black",
            markeredgecolor="black",
            markersize=8,
            markevery=mask,
            label="Gamma 2.2",
        )

        # Add labels and title
        plotting_area.set_xlabel("Intensity Levels")
        plotting_area.set_ylabel("Gamma")
        plotting_area.legend(loc="upper left")

        txt_bits_depth = "Bits depth = " + str(self.bpp)

        plotting_area.text(
            0.5,
            0.95,
            txt_bits_depth,
            transform=plotting_area.transAxes,
            ha="center",
            va="top",
            bbox=dict(facecolor="white", edgecolor="gray", pad=5.0),
        )

        # Add annotations to display values on hover
        cursor = mplcursors.cursor(plotting_area)
        cursor.connect("add")

    def on_left_click(self, sel):
        """
        Event handler to display anotation when clicked on the curve.
        """
        x_iter, y_iter = sel.target
        sel.annotation.set(text=(x_iter, y_iter))

    def get_plotting_data(self):
        """
        Get the data from the selected yml file for plotting user defined gamma
        """
        read_yml_file = ReadYMLFile(self.config_path)
        self.bpp = read_yml_file.get_bits_depth()
        gamma_luts = read_yml_file.get_gamma_correction()

        if self.bpp == 8:
            gamma_y = gamma_luts[0]
        elif self.bpp == 10:
            gamma_y = gamma_luts[1]
        elif self.bpp == 12:
            gamma_y = gamma_luts[2]
        elif self.bpp == 14:
            gamma_y = gamma_luts[3]
        else:
            print("\033[31mError!\033[0m Invalid bits depth in the YAML file.")
            generate_separator("", "*")

            return False

        # Save gamma lut
        self.gamma_lut = gamma_y
        return True

    def load_ymal_file(self):
        """
        Return true if file is selected
        """
        title = "Open a YAML file."
        filetypes = (("YAML Files", "*.yml"),)
        is_selected, file_name = select_file(title, filetypes)
        if is_selected:
            self.config_path = file_name.name
            return True
        else:
            print("\033[31mError!\033[0m File is not selected.\n")
            generate_separator("", "*")

            return False

    def on_save_btn_clicked(self, gammagraph, root):
        """
        Save the designed graphs
        """
        def_ext = ".png"
        file_types = [
            ("PNG Files", "*.png"),
        ]
        initial_file = "Gamma.png"

        # Allow user to select the path to save the .yml file and set file name.
        file_path = file_saving_path(def_ext, file_types, initial_file)
        if file_path:
            self.save_plots(gammagraph, file_path)
            print("File saved at:", file_path)
            root.destroy()
        else:
            pop_up_msg("File is not saved.")
            print("\033[31mWarning!\033[0m File destination path is not selected.")

    def save_plots(self, gamma_graph, file_name):
        """
        Function to save the gamma graph
        """
        gamma_graph.savefig(file_name)
        plt.close(gamma_graph)
