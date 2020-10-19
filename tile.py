"""
Module with the Tile class
"""

from tkinter import Button, Label
from minesweeper_details import display_offset, tile_size


class Tile():
    """Class that represents a tile on the minesweeper board"""
    def __init__(self, *, column, row):
        """Initializes a Tile object

        Keyword args:
            column (int): Column number where the tile is located
            row (int): Row number where the tile is located
        """
        self.is_mine = False  # Instantiate the tile without a mine
        self.is_hidden = True
        self.num_adjacent_mines = None
        self.is_flag_set = False
        self.column = column
        self.row = row
        self.position = {'x': None, 'y': None}
        self.button = None
        self.button_type = None
        self.position['x'] = self.column * tile_size
        self.position['y'] = self.row * tile_size + display_offset

    def create_button(self, display):
        """Creates the button

        Args:
            display: Root of the tkinter display
        """
        self.button = Button(display, relief='raised')
        self.button.place(x=self.position['x'],
                          y=self.position['y'],
                          height=tile_size,
                          width=tile_size)

    def create_label(self, display):
        """Creates the label. Label was chosen here instead of creating a
        button and setting the state to 'disabled' because that causes
        all button images to look weird and there is apparently no work
        around for that problem

        Args:
            display: Root of the tkinter display
        """
        self.button = Label(display, relief='raised')
        self.button.place(x=self.position['x'],
                          y=self.position['y'],
                          height=tile_size,
                          width=tile_size)

    def set_button_color(self, *, bg_color, fg_color=None):
        """Sets the button color

        Keyword args:
            bg_color (str): Button background color
            fg_color (str): Button foreground color. Defaults to None
        """
        self.button.configure(background=bg_color,
                              activebackground=bg_color)
        if fg_color is not None:
            self.button.configure(foreground=fg_color,
                                  activeforeground=fg_color)

    def disable_button(self, display):
        """Disables the button by creating a label

        Args:
            display: Root of the tkinter display
        """
        self.button.destroy()
        self.create_label(display)
