"""
File: area_selection_frame.py
Description: This file contains common functions used for selection area.
Author: 10xEngineers
------------------------------------------------------------
"""
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk
from src.utils.gui_common_utils import (
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
        self.main_frame()

    def main_frame(self):
        """
        Design the frame which contains controls
         and image canvas init.
        """
        # Get data
        data = self.data

        # Define he main gui
        data.root = self.design_main_frame(data.root)

        # Design the scrolled window
        scroll_window = tk.Frame(data.root)
        scroll_window.grid(row=0, column=0)

        # Designed the control panel
        control_window = self.design_control_frame()
        control_window.grid(row=1, column=0, sticky="NSEW", padx=15, pady=10)

        display_image = self.customized_image()

        # Canvas to display image
        data.canvas = tk.Canvas(
            scroll_window,
            width=data.resize_width,
            height=data.resize_height,
        )

        data.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Create scrollbars and attach them to the canvas to view canvas window
        self.scrollbar_x = ttk.Scrollbar(
            scroll_window, orient="horizontal", command=data.canvas.xview
        )
        self.scrollbar_y = ttk.Scrollbar(
            scroll_window, orient="vertical", command=data.canvas.yview
        )

        # Set the size of the scrollbar
        style = ttk.Style()
        style.configure(
            "TScrollbar",
            gripcount=0,
            gripinset=0,
            gripwidth=10,
            troughcolor="#ffffff",
            borderwidth=0,
            background="#f0f0f0",
        )
        style.map("TScrollbar", background=[("active", "#c0c0c0")])

        self.scrollbar_x.grid(row=1, column=0, sticky="NSEW")
        self.scrollbar_y.grid(row=0, column=1, sticky="NS")

        data.canvas.config(scrollregion=data.canvas.bbox(tk.ALL))
        data.canvas.configure(
            xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set
        )

        # Set event handers for canvas
        self.bind_canvas_event_handlers()

        # Load image on the canvas
        self.data.canvas.create_image(
            0, 0, image=display_image, anchor=tk.NW, tags="image"
        )

        # Binding image tag to change cursor state
        data.canvas.tag_bind("image", "<Enter>", self.on_leave)

        # Creating default rectangles
        self.create_default_rect()
        self.data = data

        # Start the gui
        data.root.mainloop()

    def design_main_frame(self, root):
        """
        This is the main frame.
        """

        # Define he main gui
        root = tk.Tk()

        # Open dialog box in the foreground
        root.attributes("-topmost", True)
        root.title("ColorChecker Patches Selection")

        # Restrict the user to not resize the frame
        root.resizable(False, False)

        return root

    def design_control_frame(self):
        """
        This frame contains all the controls needed.
        """

        data = self.data

        # Adding a control frame
        control_frame = tk.Frame(data.root, borderwidth=1, relief=tk.SOLID)
        control_frame.grid(row=1, column=0, padx=10, pady=5)

        sliders = self.design_slider_frame(control_frame)
        sliders.pack(padx=10, pady=(10, 0))

        button_frame = self.design_buttons_frame(control_frame)
        button_frame.pack(padx=10, pady=10)

        self.data = data
        return control_frame

    def design_slider_frame(self, root):
        """
        Designed a frame to align the sliders.
        """
        data = self.data

        sliders_frame = tk.Frame(root, borderwidth=1, relief=tk.SOLID)

        s_label = tk.Label(sliders_frame, text="Adjust Size", borderwidth=1)
        s_label.grid(row=0, column=0, padx=5, pady=5)
        data.s_slider = ttk.Scale(
            sliders_frame,
            from_=0,
            to=90,
            value=30,
            orient="horizontal",
            command=self.update_patch_size,
        )
        data.s_slider.grid(row=0, column=1)

        # Create sliders for x and adding label to it
        x_label = tk.Label(sliders_frame, text="Adjust Width", borderwidth=1)
        x_label.grid(row=0, column=2, padx=(20, 5), pady=5)
        data.x_slider = ttk.Scale(
            sliders_frame,
            from_=0,
            to=90,
            value=30,
            orient="horizontal",
            command=self.update_size,
        )
        data.x_slider.grid(row=0, column=3, padx=10)

        # Create sliders for y and adding label to it
        y_label = tk.Label(sliders_frame, text="Adjust Height", borderwidth=1)
        y_label.grid(row=0, column=4, padx=(20, 5), pady=5)
        data.y_slider = ttk.Scale(
            sliders_frame,
            from_=0,
            to=90,
            value=30,
            orient="horizontal",
            command=self.update_size,
        )
        data.y_slider.grid(row=0, column=5, padx=10)

        # Set the size of the scrollbar
        style = ttk.Style()
        style.configure("TScale")
        style.map("TScale")

        self.data = data
        return sliders_frame

    def design_buttons_frame(self, root):
        """
        Designed a frame to align the buttons.
        """
        data = self.data

        button_frame = tk.Frame(root, borderwidth=1, relief=tk.SOLID)

        # Create a button to save the drawing
        btn_continue = tk.Button(
            button_frame,
            text="Continue",
            borderwidth=1,
            relief=tk.RIDGE,
            command=self.on_btn_continue_clicked,
        )
        btn_continue.grid(row=0, column=1, padx=50, pady=10)

        btn_reset = tk.Button(
            button_frame,
            text="Redraw",
            borderwidth=1,
            relief=tk.RIDGE,
            command=self.create_default_rect,
        )
        btn_reset.grid(row=0, column=0, padx=50, pady=10)

        self.data = data
        return button_frame

    def customized_image(self):
        """
        Resized the image w.r.t. screen resolution and make it
        ready to use for canvas.
        """

        data = self.data

        # Set offsets between screen and selection frame
        width_offset = 400
        height_offset = 250

        # Get user's screen resolution
        data.image_scale_factor = determine_image_scale_factor(
            data.root, data.image_width, data.image_height, width_offset, height_offset
        )

        # convert the image mat into PIL image
        pil_image = cv2_to_pil_image(data.rgb_image)

        data.resize_height = int(data.image_height / data.image_scale_factor)
        data.resize_width = int(data.image_width / data.image_scale_factor)

        # Resize the pil image to fit on the image canvas
        resized_image = pil_image.resize(
            (
                data.resize_width,
                data.resize_height,
            )
        )

        display_image = ImageTk.PhotoImage(image=resized_image)

        self.data = data

        return display_image

    def bind_canvas_event_handlers(self):
        """
        Bind event handlers with canvas.
        """
        data = self.data

        # Bind the mouse event handlers for drawing
        data.canvas.bind("<Button-1>", self.on_left_mouse_clicked)
        data.canvas.bind("<B1-Motion>", self.on_left_mouse_moving)
        data.canvas.bind("<ButtonRelease-1>", self.on_leave)
        data.canvas.tag_bind("upper_left", "<Enter>", self.on_enter)
        data.canvas.tag_bind("upper_right", "<Enter>", self.on_enter)
        data.canvas.tag_bind("bottom_left", "<Enter>", self.on_enter)
        data.canvas.tag_bind("bottom_right", "<Enter>", self.on_enter)
        data.canvas.bind("<MouseWheel>", self.mouse_scroll)

        self.data = data

    def zoom_in(self):
        """
        Scale up the image for zoom in
        """
        self.data.zoom_factor *= 1.1
        # Keeping a check to keep the maximum size of zoom in
        # image to be 3 times of the actual size
        if self.data.zoom_factor > 3.10:
            self.data.zoom_factor = 3.10
        self.update_image()

    def zoom_out(self):
        """
        Scale down the image for zoom out
        """
        self.data.zoom_factor /= 1.1
        # Keeping a check to keep the minimum size of zoom in
        # image to be the actual size
        if self.data.zoom_factor < 1.0:
            self.data.zoom_factor = 1.0
        self.update_image()

    def update_image(self):
        """
        Update image after scaling up/down
        for zoom in/out
        """
        data = self.data
        # Calculate the new size based on the zoom factor
        new_width = int(data.resize_width * self.data.zoom_factor)
        new_height = int(data.resize_height * self.data.zoom_factor)

        # Resize the image
        img = cv2_to_pil_image(data.rgb_image)
        resized_image = img.resize((new_width, new_height))

        # Create a new Tkinter PhotoImage from the resized image
        data.tk_image = ImageTk.PhotoImage(resized_image)

        # Update the canvas image and creating sub rect again
        self.data.canvas.itemconfig("image", image=data.tk_image)
        self.draw_patches_translated()

        # Configuring the window scroll bar to updated image
        data.canvas.config(scrollregion=data.canvas.bbox(tk.ALL))
        data.canvas.configure(
            xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set
        )

    def create_default_rect(self):
        """
        Reset the sub_rects
        """
        # Setting sliders positions to default state.
        default_offset = 30
        self.data.x_slider.set(default_offset)
        self.data.y_slider.set(default_offset)
        self.data.s_slider.set(default_offset)
        self.data.sub_rect_scale_factor_x = default_offset
        self.data.sub_rect_scale_factor_y = default_offset

        # Creating default starting and ending points for sub rectangles
        # First calculate the full image size rectangle height & width
        rect_width = int((self.data.image_width / self.data.image_scale_factor))
        rect_height = int((self.data.image_height / self.data.image_scale_factor))

        # To position the ColorChecker drawing in the center of the image,
        # calculate the height and width of the larger rectangle. Then,
        # divide the width and height in half to determine the center point.
        # From this center point, derive the starting and ending points for
        # the default rectangle by dividing the center again in half. By drawing
        # the sub rectangles based on these calculations, the ColorChecker drawing
        # is positioned in the middle of the image.
        # canvas.canvasx(0) & canvas.canvasy(0) to add offset due to scrolling window
        rect_start = (
            rect_width // 2 - rect_width // 4 + self.data.canvas.canvasx(0),
            rect_height // 2 - rect_height // 4 + self.data.canvas.canvasy(0),
        )
        rect_end = (
            rect_width // 2 + rect_width // 4 + self.data.canvas.canvasx(0),
            rect_height // 2 + rect_height // 4 + self.data.canvas.canvasy(0),
        )

        # W and H of each patch
        self.data.patch_width = rect_width // 6
        self.data.patch_height = rect_height // 4

        # Setting up default corner points for creating sub-rectangles
        self.data.upper_left = rect_start
        self.data.upper_right = (rect_end[0], rect_start[1])
        self.data.bottom_left = (rect_start[0], rect_end[1])
        self.data.bottom_right = rect_end
        self.draw_patches_translated()

    def update_size(self, event):
        """
        Update the size of rectangles using sliders
        """
        data = self.data
        # Get the values from the sliders
        x_size = data.x_slider.get()
        y_size = data.y_slider.get()

        # Condition to update size. The factor should not increase the 55% of
        # total patch (default rectangle drawn is 30% of this patch size)
        if x_size > data.x_size and x_size <= 90 and data.sub_rect_scale_factor_x < 90:
            data.sub_rect_scale_factor_x = int(data.sub_rect_scale_factor_x + 2)
            self.delete_all()
            self.draw_patches_translated()

        if y_size > data.y_size and y_size <= 90 and data.sub_rect_scale_factor_y < 90:
            data.sub_rect_scale_factor_y = int(data.sub_rect_scale_factor_y + 2)
            self.delete_all()
            self.draw_patches_translated()

        if x_size < data.x_size and x_size >= 0 and data.sub_rect_scale_factor_x > 8:
            data.sub_rect_scale_factor_x = int(data.sub_rect_scale_factor_x - 2)
            self.delete_all()
            self.draw_patches_translated()

        if y_size < data.y_size and y_size >= 0 and data.sub_rect_scale_factor_y > 8:
            data.sub_rect_scale_factor_y = int(data.sub_rect_scale_factor_y - 2)
            self.delete_all()
            self.draw_patches_translated()

        data.x_size = x_size
        data.y_size = y_size
        self.data = data

    def on_btn_continue_clicked(self):
        """
        Continue button event handler
        """
        data = self.data
        data.root.destroy()
        data.is_data_saved = True
        self.data = data

    def on_leave(self, event):
        """
        Cursor getting default state
        """
        data = self.data
        data.canvas.config(cursor="")

    def on_enter(self, event):
        """
        Cursor changes state on corner points
        """
        data = self.data
        data.canvas.config(cursor="crosshair")

    def on_left_mouse_clicked(self, event):
        """
        Left mouse event handler in which get the start points
        of the main rectangle
        """
        data = self.data
        # Declaring False to all flags whenever mouse button pressed
        data.up_left_flag = False
        data.up_right_flag = False
        data.bottom_left_flag = False
        data.bottom_right_flag = False

        # Extracting current cursor point
        # canvas.canvasx(0) & canvas.canvasy(0) to add offset due to scrolling window
        x_var = event.x + data.canvas.canvasx(0)
        y_var = event.y + data.canvas.canvasy(0)

        # Checking if the cursor is positioned over the corner
        # regions by comparing its tag. Setting the respective
        # flag to True upon finding a match.
        overlapping_items = data.canvas.find_overlapping(x_var, y_var, x_var, y_var)
        for item in overlapping_items:
            tags = data.canvas.gettags(item)
            if "upper_left" in tags:
                data.up_left_flag = True
            elif "upper_right" in tags:
                data.up_right_flag = True
            elif "bottom_left" in tags:
                data.bottom_left_flag = True
            elif "bottom_right" in tags:
                data.bottom_right_flag = True

    def on_left_mouse_moving(self, event):
        """
        Left mouse dragging event handler in which it can
        drag or adjust the sub-rectangles positions
        """
        # Setting data variable
        data = self.data

        # Extracting current point
        # canvas.canvasx(0) & canvas.canvasy(0) to add offset due to scrolling window
        x_var = event.x + data.canvas.canvasx(0)
        y_var = event.y + data.canvas.canvasy(0)
        new_xy = (x_var, y_var)

        # Check which flag is true, to update the respective corner
        # point with the new current point. Also check the point
        # should remain inside the image
        if data.up_left_flag is True:
            # Changing state of the cursor
            data.canvas.config(cursor="crosshair")
            data.upper_left = new_xy
        elif data.up_right_flag is True:
            # Changing state of the cursor
            data.canvas.config(cursor="crosshair")
            data.upper_right = new_xy
        elif data.bottom_left_flag is True:
            # Changing state of the cursor
            data.canvas.config(cursor="crosshair")
            data.bottom_left = new_xy
        elif data.bottom_right_flag is True:
            # Changing state of the cursor
            data.canvas.config(cursor="crosshair")
            data.bottom_right = new_xy

        # After setting corner points adjust the sub_rect by redrawing them
        self.draw_patches_translated()

    def mouse_scroll(self, event):
        """
        Event handler for mouse scrolling to resize the
        image. (zoom in and out)
        """
        if event.delta > 0:
            self.zoom_in()
        elif event.delta < 0:
            self.zoom_out()

    def update_patch_size(self, event):
        """
        Update the overall size of the sub_rectangles
        """
        data = self.data
        s_size = data.s_slider.get()
        if s_size > data.s_size:
            if data.sub_rect_scale_factor_x < 90 and data.sub_rect_scale_factor_y < 90:
                data.sub_rect_scale_factor_x = int(data.sub_rect_scale_factor_x + 2)
                data.sub_rect_scale_factor_y = int(data.sub_rect_scale_factor_y + 2)
                self.delete_all()
                self.draw_patches_translated()
        if s_size < data.s_size:
            if data.sub_rect_scale_factor_x > 8 and data.sub_rect_scale_factor_y > 8:
                data.sub_rect_scale_factor_x = int(data.sub_rect_scale_factor_x - 2)
                data.sub_rect_scale_factor_y = int(data.sub_rect_scale_factor_y - 2)
                self.delete_all()
                self.draw_patches_translated()
        data.s_size = s_size
        self.data = data

    def save_inner_rect_points(self, start_point, end_point):
        """
        Save the sub-rect points into a list after mapping on
        the original image.
        """
        data = self.data
        # Remap the points on the image
        start_x = int(
            (start_point[0] * data.image_scale_factor / self.data.zoom_factor)
        )
        start_y = int(
            (start_point[1] * data.image_scale_factor / self.data.zoom_factor)
        )

        end_x = int((end_point[0] * data.image_scale_factor / self.data.zoom_factor))
        end_y = int((end_point[1] * data.image_scale_factor / self.data.zoom_factor))

        start_sub_rect = (start_x, start_y)
        end_sub_rect = (end_x, end_y)

        # Save into the list
        data.sub_rect_points.append((start_sub_rect, end_sub_rect))

        self.data = data

    def get_sub_rect_points(self):
        """
        Return the sub-rect saved points
        """
        return self.data.sub_rect_points

    def draw_patches_translated(self):
        """
        Fucntion to draw sub-rect inside the main rectangle
        """
        # Setting local data variables
        data = self.data

        upper_left = self.check_boundary(data.upper_left)
        upper_right = self.check_boundary(data.upper_right)
        bottom_left = self.check_boundary(data.bottom_left)
        bottom_right = self.check_boundary(data.bottom_right)

        # Deleting default rectangles
        self.delete_all()

        # Define total number of rows and columns of sub-rects
        columns = 6
        rows = 4

        # Calculate the W and H of sub_rect from user input
        patch_width = int(data.patch_width * data.sub_rect_scale_factor_x / 100)
        patch_height = int(data.patch_height * data.sub_rect_scale_factor_y / 100)

        # Calculating vertical and horizontal offsets (dx & dy) for left and right
        # points in order to set starting and ending points of each row
        dx_l = (-upper_left[0] + bottom_left[0]) / 3
        dy_l = (-upper_left[1] + bottom_left[1]) / 3
        dx_r = (-upper_right[0] + bottom_right[0]) / 3
        dy_r = (-upper_right[1] + bottom_right[1]) / 3

        # Clear the array to save the sub-rects points
        data.sub_rect_points.clear()

        for row in range(rows):
            # Setting the starting and ending point for each row
            start_row = (
                (upper_left[0] + row * dx_l - patch_width // 2),
                (upper_left[1] + row * dy_l - patch_height // 2),
            )
            end_row = (
                (upper_right[0] + row * dx_r - patch_width // 2),
                (upper_right[1] + row * dy_r - patch_height // 2),
            )

            # Calculating offset for each patch in a row (column wise)
            offset_x1 = (end_row[0] - start_row[0]) / 5
            offset_y1 = (end_row[1] - start_row[1]) / 5
            for col in range(columns):
                # Calculating starting and ending point for each rectangle
                start_rect = (
                    (start_row[0] + col * offset_x1),
                    (start_row[1] + col * offset_y1),
                )
                end_rect = (
                    (start_rect[0] + patch_width),
                    (start_rect[1] + patch_height),
                )

                # Drawing asterisk character in the middle of the corner points
                if row == 0 and col == 0:
                    # Create a text widget to display the asterisk character
                    x_center = (start_rect[0] + end_rect[0]) / 2
                    y_center = (start_rect[1] + end_rect[1]) / 2 + 5
                    self.create_star(x_center, y_center, "upper_left")
                elif row == 0 and col == 5:
                    x_center = (start_rect[0] + end_rect[0]) / 2
                    y_center = (start_rect[1] + end_rect[1]) / 2 + 5
                    self.create_star(x_center, y_center, "upper_right")
                elif row == 3 and col == 0:
                    x_center = (start_rect[0] + end_rect[0]) / 2
                    y_center = (start_rect[1] + end_rect[1]) / 2 + 5
                    self.create_star(x_center, y_center, "bottom_left")
                elif row == 3 and col == 5:
                    x_center = (start_rect[0] + end_rect[0]) / 2
                    y_center = (start_rect[1] + end_rect[1]) / 2 + 5
                    self.create_star(x_center, y_center, "bottom_right")

                # Saving points for each rectangle drawn
                self.save_inner_rect_points(start_rect, end_rect)

                # Drawing rectangle
                data.canvas.create_rectangle(
                    start_rect[0],
                    start_rect[1],
                    end_rect[0],
                    end_rect[1],
                    outline="red",
                    tags="sub_rect",
                )

        data.upper_left = upper_left
        data.upper_right = upper_right
        data.bottom_left = bottom_left
        data.bottom_right = bottom_right
        self.data = data

    def create_star(self, x_center, y_center, tag_name):
        """
        Creating star in the center of corner rectangles
        """
        self.data.canvas.create_text(
            x_center,
            y_center,
            text="*",
            font=("Arial", 20),
            fill="white",
            tags=tag_name,
        )

    def delete_all(self):
        """
        Deleting all the relevant tags to create new sub rects
        """
        self.data.canvas.delete("sub_rect")
        self.data.canvas.delete("upper_left")
        self.data.canvas.delete("upper_right")
        self.data.canvas.delete("bottom_left")
        self.data.canvas.delete("bottom_right")

    def check_boundary(self, point):
        """
        Check boundary conditions on points
        and return updated point
        """
        data = self.data
        # Extracting current point
        x_var = point[0]
        y_var = point[1]

        # Calculating width and height of the image and drawn rectangle
        width_img = int(
            (data.image_width / data.image_scale_factor) * self.data.zoom_factor
        )
        height_img = int(
            (data.image_height / data.image_scale_factor) * self.data.zoom_factor
        )
        patch_width = int(data.patch_width * data.sub_rect_scale_factor_x / 100)
        patch_height = int(data.patch_height * data.sub_rect_scale_factor_y / 100)

        # Check to keep the drawn patches inside the image
        if x_var - patch_width // 2 < 0:
            x_var = 0 + patch_width // 2
            data.maxsize_flag = True
        elif x_var + patch_width // 2 > width_img:
            x_var = width_img - patch_width // 2
            data.maxsize_flag = True
        if y_var - patch_height // 2 < 0:
            y_var = 0 + patch_height // 2
            data.maxsize_flag = True
        elif y_var + patch_height // 2 > height_img:
            y_var = height_img - patch_height // 2
            data.maxsize_flag = True
        else:
            data.maxsize_flag = False
        new_xy = (x_var, y_var)
        return new_xy


class SelectionFrameStorage:
    """
    This class contains all the data variables that are used
     in selection area frame.
    """

    def __init__(self):
        self.rgb_image = None
        self.tk_image = None
        self.image_width = 1920
        self.image_height = 1080
        self.root = None
        self.canvas = None

        self.is_data_saved = False

        # Resized width and height after determining scaling factor
        self.resize_width = 1920
        self.resize_height = 1080

        # Defining corner points for sub-rectangles
        self.upper_left = (0, 0)
        self.upper_right = (0, 0)
        self.bottom_left = (0, 0)
        self.bottom_right = (0, 0)

        # Default flag status to see cursor position
        self.up_left_flag = False
        self.up_right_flag = False
        self.bottom_left_flag = False
        self.bottom_right_flag = False

        # Default patch width and height
        self.patch_width = 0
        self.patch_height = 0

        # Declaring sliders and flag
        self.x_slider = None
        self.y_slider = None
        self.s_slider = None
        self.maxsize_flag = False

        # Default value of sliders to set 0
        self.x_size = 0
        self.y_size = 0
        self.s_size = 0

        # Factor to scale the image canvas
        self.image_scale_factor = 2
        # Setting default zoom factor
        self.zoom_factor = 1.0

        # Factor to scale the sub_rect (in percentage)
        self.sub_rect_scale_factor_x = 8
        self.sub_rect_scale_factor_y = 8

        # Store the sub-rect points
        self.sub_rect_points = []
