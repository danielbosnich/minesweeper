"""
Variables and dictionaries used for game and display details
"""

# Offset to the first tile and side length of each
display_offset = 50  # pylint: disable=invalid-name
tile_size = 30  # pylint: disable=invalid-name

# Dictionary with number colors based on number of adjacent mines
number_colors = {
    None: 'pink',  # Should never be shown!
    1: 'blue',
    2: 'green',
    3: 'red',
    4: 'purple',
    5: 'maroon',
    6: 'turquoise',
    7: 'black',
    8: 'grey'
}

# Dictionaries with column, row, mine, and display size info based on the level
EASY = {
    'rows': 9,
    'columns': 9,
    'mines': 10,
    'display_width': tile_size * 9,
    'display_height': tile_size * 9,
}

MEDIUM = {
    'rows': 16,
    'columns': 16,
    'mines': 40,
    'display_width': tile_size * 16,
    'display_height': tile_size * 16,
}

HARD = {
    'rows': 16,
    'columns': 30,
    'mines': 99,
    'display_width': tile_size * 30,
    'display_height': tile_size * 16,
}

level_info = {
    'easy': EASY,
    'medium': MEDIUM,
    'hard': HARD
}
