"""
Basic minesweeper unit tests
"""

from unittest import main, TestCase
from board import Board
from game import Game
from tile import Tile

# Test constants
COLUMN = 4
ROW = 4


class BoardTests(TestCase):
    """Basic tests for the minesweeper board class"""
    def test_num_tiles_easy(self):
        """Tests that the correct number of tiles are created for a game
        played at the easy level"""
        num_expected_tiles = 9 * 9
        board = Board(level='easy')
        num_tiles = len(board.tiles)
        self.assertEqual(num_tiles, num_expected_tiles)

    def test_num_tiles_medium(self):
        """Tests that the correct number of tiles are created for a game
        played at the easy level"""
        num_expected_tiles = 16* 16
        board = Board(level='medium')
        num_tiles = len(board.tiles)
        self.assertEqual(num_tiles, num_expected_tiles)

    def test_num_tiles_hard(self):
        """Tests that the correct number of tiles are created for a game
        played at the easy level"""
        num_expected_tiles = 16 * 30
        board = Board(level='hard')
        num_tiles = len(board.tiles)
        self.assertEqual(num_tiles, num_expected_tiles)


class GameTests(TestCase):
    """Basic tests for the minesweeper game class"""
    def setUp(self):
        """Creates a new Tile object before each test"""
        self.game = Game(level='easy')

    def test_level_saved_correctly(self):
        """Tests that the passed level was saved correctly"""
        self.assertEqual(self.game._game_level, 'easy')

    def test_first_tile_flag(self):
        """Tests that the game first tile flag is initialized to True"""
        self.assertTrue(self.game._is_first_tile)

    def test_set_button_clicked(self):
        """Tests the set button clicked method"""
        self.game._set_button_clicked('right')
        self.assertTrue(self.game._is_right_clicked)

    def test_set_button_unclicked(self):
        """Tests the set button unclicked method"""
        self.game._set_button_unclicked('right')
        self.assertFalse(self.game._is_right_clicked)


class TileTests(TestCase):
    """Basic tests for the minesweeper tile class"""
    def setUp(self):
        """Creates a new Tile object before each test"""
        self.tile = Tile(column=COLUMN, row=ROW)

    def test_is_mine_false(self):
        """Tests that the tile is instantiated without a mine"""
        self.assertFalse(self.tile.is_mine)

    def test_is_mine_hidden(self):
        """Tests that the tile is instantiated as hidden"""
        self.assertTrue(self.tile.is_hidden)


if __name__ == '__main__':
    main()
