"""
Module with the Board class
"""

import logging
import random
from minesweeper_details import LEVEL_INFO
from tile import Tile


class Board():
    """Class that represents the minesweeper board"""
    def __init__(self, level):
        """Initializes a Board object

        Args:
            level (str): The difficulty level of the game
        """
        self.rows = None
        self.columns = None
        self.mines = None
        self.num_mines_left = None
        self.tiles = {}
        self._set_board_info(level)
        self._create_tiles()

    def _set_board_info(self, level):
        """Sets the board info based on the difficulty level

        Args:
            level (str): The difficulty level of the game
        """
        self.rows = LEVEL_INFO[level]['rows']
        self.columns = LEVEL_INFO[level]['columns']
        self.mines = LEVEL_INFO[level]['mines']
        self.num_mines_left = LEVEL_INFO[level]['mines']
        logging.debug(f'Setting up the board with {self.columns} columns, '
                      f'{self.rows} rows, and {self.mines} mines')

    def _create_tiles(self):
        """Creates the tile objects and adds them to the tiles dictionary"""
        for column in range(self.columns):
            for row in range(self.rows):
                tile_name = str(column) + ',' + str(row)
                self.tiles[tile_name] = Tile(column=column, row=row)

    def count_adjacent_mines(self, *, column, row):
        """Counts the number of adjacent tiles that have a mine

        Args:
            column (int): Column number where the tile to check is located
            row (int): Row number where the tile to check is located
        Returns:
            int: Number of adjacent tiles with a mine
        """
        num_adjacent_mines = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                test_column = column + i
                test_row = row + j
                # Make sure that the tile we're checking is an actual tile
                if ((test_column < 0 or test_column >= self.columns) or
                        (test_row < 0 or test_row >= self.rows)):
                    continue
                test_tile = str(test_column) + ',' + str(test_row)
                if self.tiles[test_tile].is_mine:
                    num_adjacent_mines += 1
        logging.debug(f'The tile at column {column}, row {row} has '
                      f'{num_adjacent_mines} adjacent mine(s)')
        return num_adjacent_mines

    def set_the_mines(self, tile):
        """Randomly places the mines throughout the tiles, except for the
        passed tile which is the first tile chosen by the user. Additionally,
        that passed tile must not have any mines adjacent to it

        Args:
            tile (Tile): Tile which should not have a mine or adjacent mines
        """
        num_mines_placed = 0

        # Create the lists of not allowed tiles
        restricted_columns = []
        restricted_rows = []
        for i in range(-1, 2):
            test_column = tile.column + i
            test_row = tile.row + i
            if not test_column < 0 or test_column >= self.columns:
                restricted_columns.append(test_column)
            if not test_row < 0 or test_row >= self.rows:
                restricted_rows.append(test_row)

        while num_mines_placed < self.mines:
            rand_column = random.randint(0, self.columns - 1)
            rand_row = random.randint(0, self.rows - 1)
            tile_name = str(rand_column) + ',' + str(rand_row)
            if not (self.tiles[tile_name].is_mine or
                    (rand_column in restricted_columns and
                     rand_row in restricted_rows)):
                self.tiles[tile_name].is_mine = True
                logging.debug(f'Mine placed at column {rand_column}, row '
                              f'{rand_row}')
                num_mines_placed += 1
                logging.debug(f'{num_mines_placed} mines have been placed')

        # Figure out how many adjacent mines each tile has
        for column in range(self.columns):
            for row in range(self.rows):
                tile_name = str(column) + ',' + str(row)
                num_mines = self.count_adjacent_mines(column=column, row=row)
                if num_mines > 0:
                    self.tiles[tile_name].num_adjacent_mines = num_mines

    def count_num_adjacent_flags(self, tile):
        """Counts the number of adjacent tiles with a flag

        Args:
            tile (Tile): Tile to check for adjacent flags
        Returns:
            int: Number of adjacent tiles with a flag
        """
        num_adjacent_flags = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                test_column = tile.column + i
                test_row = tile.row + j
                # Make sure that the tile we're checking is on the board
                if ((test_column < 0 or test_column >= self.columns) or
                        (test_row < 0 or test_row >= self.rows)):
                    continue
                test_tile_location = (str(test_column) + ',' +
                                      str(test_row))
                test_tile = self.tiles[test_tile_location]
                if test_tile.is_flag_set:
                    num_adjacent_flags += 1
        logging.debug(f'The tile at column {test_column}, row {test_row} has '
                      f'{num_adjacent_flags} adjacent flag(s)')
        return num_adjacent_flags

    def check_if_all_tiles_cleared(self):
        """Checks if all the tiles without a mine have been cleared

        Returns:
            bool: If all the tiles without a mine have been cleared
        """
        all_cleared = True
        for tile in self.tiles.values():
            if not tile.is_mine:
                if tile.is_hidden:
                    all_cleared = False
                    break
        return all_cleared
