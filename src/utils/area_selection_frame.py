"""
File: algo_common_utils.py
Description: This file contains common functions used for selection area.
Author: 10xEngineers
------------------------------------------------------------
"""
import tkinter as tk
from PIL import ImageTk
from src.utils.gui_common_utils import (
    pop_up_msg,
    cv2_to_pil_image,
    determine_image_scale_factor,
)


class SelectAreaFrame:
    """
    Define the class to select the ColorChecker patches.
    """

    def __init__(self, rgb_image):
        self.data = SelectionFrameStorage()
        self.data.rgb_image = rgb_image
        height, width, _ = rgb_image.shape

        self.data.image_width = width
        self.data.image_height = height

        self.create_frame()

    def create_frame(self):
        """
        Design the frame which contains controls
         and image canvas init.
        """
        # Get data
        data = self.data

        # Define he main gui
        data.root = tk.Tk()
        # Open dialog box in the foreground
        data.root.attributes("-topmost", True)
        data.root.title("ColorChecker Patches Selection")

        # Set offsets between screen and selection frame
        width_offset = 350
        height_offset = 190

        # Get user's screen resolution
        data.image_scale_factor = determine_image_scale_factor(
            data.root, data.image_width, data.image_height, width_offset, height_offset
        )
        descr_message = (
            "Use mouse to draw rectangle around ColorChecker "
            "and use side buttons to adjust and save it."
        )
        descr_lab = tk.Label(
            data.root, text=descr_message, borderwidth=1, relief="solid"
        )
        descr_lab.grid(row=0, column=0, padx=10, columnspan=2)

        # Frame for controls
        control_frame = tk.Frame(data.root, width=100)
        control_frame.grid(row=1, column=0, padx=10, pady=10)

        # Create a left arrow button
        btn_left_arrow = tk.Button(
            control_frame, text="<", padx=10, pady=5, command=self.on_btn_left_clicked
        )
        btn_left_arrow.grid(row=1, column=0)

        # Create a right arrow button
        btn_right_arrow = tk.Button(
            control_frame, text=">", padx=10, pady=5, command=self.on_btn_right_clicked
        )
        btn_right_arrow.grid(row=1, column=2)

        # Create an up arrow button
        btn_up_arrow = tk.Button(
            control_frame, text="^", padx=10, pady=5, command=self.on_btn_up_clicked
        )
        btn_up_arrow.grid(row=0, column=1)

        # Create a down arrow button
        btn_down_arrow = tk.Button(
            control_frame, text="v", padx=10, pady=5, command=self.on_btn_down_clicked
        )
        btn_down_arrow.grid(row=2, column=1)

        # Add empty space beetween buttons using label with no text
        tk.Label(master=control_frame).grid(row=3, column=0)

        # Create a button to save the drawing
        btn_continue = tk.Button(
            master=control_frame, text="Continue", command=self.on_btn_continue_clicked
        )
        btn_continue.grid(row=4, column=1)

        # convert the image mat into PIL image
        pil_image = cv2_to_pil_image(data.rgb_image)

        # Resize the pil image to fit on the image canvas
        resized_image = pil_image.resize(
            (
                int(data.image_width / data.image_scale_factor),
                int(data.image_height / data.image_scale_factor),
            )
        )

        # Canvas to display image
        data.canvas = tk.Canvas(
            data.root,
            width=(data.image_width / data.image_scale_factor),
            height=(data.image_height / data.image_scale_factor),
        )
        data.canvas.grid(row=1, column=1, pady=10)

        # Bind the mouse event handlers for drawing
        data.canvas.bind("<Button-1>", self.on_left_mouse_clicked)
        data.canvas.bind("<B1-Motion>", self.on_left_mouse_moving)
        data.canvas.bind("<MouseWheel>", self.mouse_scroll)

        # Convert the image into imagetk
        display_image = ImageTk.PhotoImage(image=resized_image)

        # Load image on the canvas
        data.canvas.create_image(0, 0, image=display_image, anchor=tk.NW)

        # Prevent frame from being resized
        data.root.resizable(False, False)

        # Start the gui
        data.root.mainloop()

        self.data = data

    def on_btn_continue_clicked(self):
        """
        Continue button event handler
        """
        data = self.data
        if data.is_main_rect_drawn:
            # If w or h is less than 20 then return becuase with
            # that size there are not made patches
            rec_w = abs(data.rect_start[0] - data.rect_end[0])
            rec_h = abs(data.rect_start[1] - data.rect_end[1])

            if rec_w < 20 or rec_h < 20:
                pop_up_msg("The size of the drawn rectangle is too small.")
                return
            data.root.destroy()
            data.is_data_saved = True
        else:
            pop_up_msg("Please draw the rectangle.")
        self.data = data

    def on_left_mouse_clicked(self, event):
        """
        Left mouse event handler in which get the start points
        of the main rectangle
        """

        self.data.rect_start = (event.x, event.y)
        self.data.is_main_rect_drawn = False

    def on_left_mouse_moving(self, event):
        """
        Left mouse dragging event handler in which get the end
        points of the main rectangle and
        draw rectangle along with sub-rectangles
        """

        data = self.data

        # Return if rectange is not drawn on the image.
        if event.x < 0 or event.x > (data.image_width // data.image_scale_factor):
            return

        if event.y < 0 or event.y > (data.image_height // data.image_scale_factor):
            return

        # Collect the end points
        data.rect_end = (event.x, event.y)

        # Set that main rect is drawn
        data.is_main_rect_drawn = True

        # Delete the previous drawn rectangle with tag rect if any
        data.canvas.delete("rect")

        # Draw the rectangle
        if data.rect_end != data.rect_start:
            data.canvas.create_rectangle(
                data.rect_start[0],
                data.rect_start[1],
                data.rect_end[0],
                data.rect_end[1],
                outline="red",
                tags="rect",
            )

            # Draw sub-rectangles
            self.draw_sub_rect()

        self.data = data

    def mouse_scroll(self, event):
        """
        Event handler for mouse scrolling to resize the
        sub-rectangles.
        Note: User is allowed to minimze and
        maximize the sub-rect upto 10% and 90% of the
        given space respectively
        """
        data = self.data

        # Return without performing any functionality if main
        # rectangle is not drawn
        if not data.is_main_rect_drawn:
            return

        # Increase or decrease the sub-rects 10% of its actual
        # size each time user scroll up or down
        if event.delta > 0:
            if data.sub_rect_scale_factor < 90:
                data.sub_rect_scale_factor = int(data.sub_rect_scale_factor + 10)
                self.draw_sub_rect()
        else:
            if data.sub_rect_scale_factor > 10:
                data.sub_rect_scale_factor = int(data.sub_rect_scale_factor - 10)
                self.draw_sub_rect()

        self.data = data

    def draw_sub_rect(self):
        """
        Fucntion to draw sub-rect inside the main rectangle
        """

        data = self.data

        # Get the main rect start and end points
        rect_start = data.rect_start
        rect_end = data.rect_end

        # Starting point for sub-rect
        starting_point_sub_rect = rect_start

        # Change the sub-rect start point if user start drawing
        # other than top left
        if (rect_start[0] > rect_end[0]) & (rect_start[1] > rect_end[1]):
            starting_point_sub_rect = rect_end
        elif (rect_start[0] > rect_end[0]) and (rect_start[1] < rect_end[1]):
            starting_point_sub_rect = (rect_end[0], rect_start[1])
        elif (rect_start[0] < rect_end[0]) and (rect_start[1] > rect_end[1]):
            starting_point_sub_rect = (rect_start[0], rect_end[1])

        # Get W and H of the main rect
        rect_width = abs(rect_start[0] - rect_end[0])
        rect_height = abs(rect_start[1] - rect_end[1])

        # Define total number of rows and columns of sub-rects
        columns = 6
        rows = 4

        # W and H of each patch
        patch_width = rect_width // columns
        patch_height = rect_height // rows

        # Calculate the W and H of sub_rect from user input
        sub_rect_width = int(patch_width * data.sub_rect_scale_factor / 100)
        sub_rect_height = int(patch_height * data.sub_rect_scale_factor / 100)

        # Findout the offset for sub_rect
        offset_x = abs(patch_width - sub_rect_width) // 2
        offst_y = abs(patch_height - sub_rect_height) // 2

        # Delete previous sub-rects if any exist with tag "sub_rect"
        data.canvas.delete("sub_rect")

        # Clear the array to save the sub-rects points
        data.sub_rect_points.clear()

        # Draw sub-rects
        for row in range(rows):
            for col in range(columns):
                # Get start and ent points of the current rect and
                # save them
                start_sub_rect = (
                    (starting_point_sub_rect[0] + col * patch_width + offset_x),
                    (starting_point_sub_rect[1] + row * patch_height + offst_y),
                )
                end_sub_rect = (
                    (start_sub_rect[0] + sub_rect_width),
                    (start_sub_rect[1] + sub_rect_height),
                )
                self.save_inner_rect_points(start_sub_rect, end_sub_rect)

                # Draw the sub-rect on canvas
                data.canvas.create_rectangle(
                    start_sub_rect[0],
                    start_sub_rect[1],
                    end_sub_rect[0],
                    end_sub_rect[1],
                    outline="red",
                    tags="sub_rect",
                )

        self.data = data

    def save_inner_rect_points(self, start_point, end_point):
        """
        Save the sub-rect points into a list after mapping on
        the original image.
        """
        data = self.data

        # Remap the points on the image
        start_x = int(start_point[0] * data.image_scale_factor)
        start_y = int(start_point[1] * data.image_scale_factor)

        end_x = int(end_point[0] * data.image_scale_factor)
        end_y = int(end_point[1] * data.image_scale_factor)

        start_sub_rect = (start_x, start_y)
        end_sub_rect = (end_x, end_y)

        # Save into the list
        data.sub_rect_points.append((start_sub_rect, end_sub_rect))

        self.data = data

    def on_btn_left_clicked(self):
        """
        Event handlers to move the rectangles on the left side
        and redraw the main and sub-rectangles.
        """

        data = self.data

        if ((data.rect_start[0] - data.rect_move_offset) >= 0) and (
            (data.rect_end[0] - data.rect_move_offset) >= 0
        ):
            data.rect_start = (
                data.rect_start[0] - data.rect_move_offset,
                data.rect_start[1],
            )
            data.rect_end = (data.rect_end[0] - data.rect_move_offset, data.rect_end[1])
            self.redraw_rectangles()

        self.data = data

    def on_btn_right_clicked(self):
        """
        Event handlers to move the rectangles on the right side
         and redraw the main and sub-rectangles.
        """

        data = self.data

        if (
            (data.rect_start[0] + data.rect_move_offset)
            <= (data.image_width // data.image_scale_factor)
        ) and (
            (data.rect_end[0] + data.rect_move_offset)
            <= (data.image_width // data.image_scale_factor)
        ):
            data.rect_start = (
                data.rect_start[0] + data.rect_move_offset,
                data.rect_start[1],
            )
            data.rect_end = (data.rect_end[0] + data.rect_move_offset, data.rect_end[1])
            self.redraw_rectangles()

        self.data = data

    def on_btn_up_clicked(self):
        """
        Event handlers to move the rectangles on the up side
        and redraw the main and sub-rectangles.
        """

        data = self.data

        if ((data.rect_start[1] - data.rect_move_offset) >= 0) and (
            (data.rect_end[1] - data.rect_move_offset) >= 0
        ):
            data.rect_start = (
                data.rect_start[0],
                data.rect_start[1] - data.rect_move_offset,
            )
            data.rect_end = (data.rect_end[0], data.rect_end[1] - data.rect_move_offset)
            self.redraw_rectangles()

        self.data = data

    def on_btn_down_clicked(self):
        """
        Event handlers to move the rectangles on the down side
        and redraw the main and sub-rectangles.
        """

        data = self.data

        if (
            (data.rect_start[1] + data.rect_move_offset)
            <= (data.image_height // data.image_scale_factor)
        ) and (
            (data.rect_end[1] + data.rect_move_offset)
            <= (data.image_height // data.image_scale_factor)
        ):
            data.rect_start = (
                data.rect_start[0],
                data.rect_start[1] + data.rect_move_offset,
            )
            data.rect_end = (data.rect_end[0], data.rect_end[1] + data.rect_move_offset)
            self.redraw_rectangles()

        self.data = data

    def redraw_rectangles(self):
        """
        Function to redraw main and sub rectangles.
        """

        data = self.data

        data.canvas.delete("rect")
        if data.rect_end != data.rect_start:
            data.canvas.create_rectangle(
                data.rect_start[0],
                data.rect_start[1],
                data.rect_end[0],
                data.rect_end[1],
                outline="red",
                tags="rect",
            )
            self.draw_sub_rect()

        self.data = data

    def get_sub_rect_points(self):
        """
        Return the sub-rect saved points
        """
        return self.data.sub_rect_points


class SelectionFrameStorage:

    """
    This class contains all the data variables that are used
     in selection area frame.
    """

    def __init__(self):
        self.rgb_image = None
        self.image_width = 1920
        self.image_height = 1080
        self.root = None
        self.canvas = None

        self.is_data_saved = False

        # Define the startup points for the main rectangle
        self.rect_start = (0, 0)
        self.rect_end = (0, 0)

        # Define parameter to check that either main rectangle
        # is drawn or not
        self.is_main_rect_drawn = False

        # Factor to scale the image canvas
        self.image_scale_factor = 2

        # Factor to scale the sub_rect (in percentage)
        self.sub_rect_scale_factor = 50

        # Store the sub-rect points
        self.sub_rect_points = []

        # Offset to move the rectangles using left, right, up
        # and down buttons
        self.rect_move_offset = 2
