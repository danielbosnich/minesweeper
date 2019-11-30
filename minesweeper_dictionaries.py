"""
Dictionaries used for the minesweeper project

Created on Thu Jun 27 19:08:36 2019

@author: danielb
"""

# Dictionary with number colors based on number of adjacent mines
number_colors = {
    None: "pink", # Should never be shown
    1: "blue",
    2: "green",
    3: "red",
    4: "purple",
    5: "maroon",
    6: "turquoise",
    7: "black",
    8: "grey"
    }

# Dictionaries with column, row, mine, and display size info based on
# difficulty level
EASY = {
    'rows': 9,
    'columns': 9,
    'mines': 10,
    'display_width': 450,
    'display_height': 450,
    'tile_size': 50
    }
MEDIUM = {
    'rows': 16,
    'columns': 16,
    'mines': 40,
    'display_width': 800,
    'display_height': 800,
    'tile_size': 50
    }
HARD = {
    'rows': 16,
    'columns': 30,
    'mines': 99,
    'display_width': 1500,
    'display_height': 800,
    'tile_size': 50
    }
level_info = {
    'easy': EASY,
    'medium': MEDIUM,
    'hard': HARD
    }
