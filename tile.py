"""
Created on Thu Sep 12 19:23:11 2019

@author: danielb
"""

from tkinter import Button, Label


class Tile():
    """Class that represents a tile on the minesweeper board"""
    def __init__(self, column, row, size):
        self.is_mine = False # Instantiate the tile without a mine
        self.is_hidden = True
        self.num_adjacent_mines = None
        self.is_flag_set = False
        self.column = column
        self.row = row
        self.position = {'x': None, 'y': None}
        self.tile_size = size
        self.button = None
        self.button_type = None

    def add_display_position(self, offset):
        """Add the x position and y position instance variables for the tile
        location in the display"""
        self.position['x'] = self.column * self.tile_size
        self.position['y'] = self.row * self.tile_size + offset

    def create_button(self, display):
        """Creates the button"""
        self.button = Button(display, relief="raised")
        self.button.place(x=self.position['x'],
                          y=self.position['y'],
                          height=self.tile_size,
                          width=self.tile_size)

    def create_label(self, display):
        """Creates the label. Label was chosen here instead of creating a
        button and setting the state to 'disabled' because that causes
        all button images to look weird and there is apparently no work
        around for that problem"""
        self.button = Label(display, relief="raised")
        self.button.place(x=self.position['x'],
                          y=self.position['y'],
                          height=self.tile_size,
                          width=self.tile_size)

    def set_button_color(self, bg_color, fg_color=None):
        self.button.configure(bg=bg_color,
                              activebackground=bg_color)
        if fg_color is not None:
            self.button.configure(fg=fg_color,
                                  activeforeground=fg_color)

    def disable_button(self, display):
        """Disables the button by creating a label"""
        self.button.destroy()
        self.create_label(display)
