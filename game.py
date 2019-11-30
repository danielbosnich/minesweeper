"""
Created on Thu Sep 12 19:44:06 2019

@author: danielb
"""

import logging
import sqlite3
import threading
import time
from datetime import datetime, timezone
from tkinter import PhotoImage
from board import Board
from minesweeper_dictionaries import level_info, number_colors
from minesweeper_displays import BoardDisplay, TimesDisplay


class Game():
    """Class that represents a running of the game"""
    def __init__(self, level):
        # Game variables
        self.game_level = level
        self.tile_size = level_info[level]['tile_size']
        self.game_start_time = None
        self.game_end_time = None
        self.game_run_time = None
        self.game_over = False
        self.game_won = None
        self.is_first_tile = True # Set to True until the first click
        self.board = None
        self.db_id = None
        # Display and user variables
        self.board_display = None
        self.times_display = None
        self.is_left_clicked = False
        self.is_right_clicked = False
        self.closing_game = False
        self.restart_game_flag = False
        self.timer_thread = None
        self.username = None
        # Images
        self.photo_exploded_mine = None
        self.photo_flag = None
        self.photo_mine = None
        self.photo_wrong_mine = None

    def create_display(self):
        """Creates the minesweeper board display"""
        logging.debug("Creating the minesweeper board display")
        self.board_display = BoardDisplay(self.game_level)
        self.board_display.root.protocol("WM_DELETE_WINDOW",
                                         self.close_window)
        # Create the tile buttons
        for tile in self.board.tiles.values():
            tile.create_button(self.board_display.root)
            tile.button_type = 'blank'
            self.update_button(tile)
            # Set the button click bindings for the tile buttons. Setting
            # these here because they will never change.
            tile.button.bind('<Button-1>',
                             lambda event, arg1='left':
                             self.set_button_clicked(event, arg1))
            tile.button.bind('<Button-3>',
                             lambda event, arg1='right':
                             self.set_button_clicked(event, arg1))
        # Create the header
        self.board_display.smiley_button.configure(command=self.restart_game)
        self.update_header('smiley')

    def start_game(self):
        """Starts the game by creating the board"""
        logging.info("Starting a game at level: %s", self.game_level)
        self.board = Board(self.game_level)
        self.create_display()

        # Load images
        # Need to define the file paths separately for tkinter
        exploded_mine_path = "Images/exploded_mine.gif"
        flag_path = "Images/blue_flag.gif"
        mine_path = "Images/mine.gif"
        wrong_mine_path = "Images/wrong_mine.gif"
        self.photo_exploded_mine = PhotoImage(file=exploded_mine_path)
        self.photo_flag = PhotoImage(file=flag_path)
        self.photo_mine = PhotoImage(file=mine_path)
        self.photo_wrong_mine = PhotoImage(file=wrong_mine_path)

    def close_window(self):
        """Updates the proper flags and ensures that threads are closed before
        closing the window"""
        self.closing_game = True
        logging.debug("Closing the main window")
        # Wait for the timer thread to close
        loop_count = 0
        if self.timer_thread:
            logging.info(self.timer_thread)
            while self.timer_thread.is_alive():
                loop_count += 1
                logging.debug("Waiting another .15 seconds for the timer "
                              "thread to close")
                if loop_count > 7:
                    logging.info("Timer thread took longer than 1 second to "
                                 "close")
                    # TODO: Throw an exception here
                    break
                time.sleep(.15)
        # Destroy all the displays
        if self.times_display is not None:
            self.times_display.root.destroy()
        self.board_display.root.destroy()

    def update_database(self):
        """Updates the database with info from the game when it starts and
        after it is finished"""
        create_tables()
        conn = sqlite3.connect('minesweeper.db')
        cur = conn.cursor()

        if not self.game_over:
            # Add starting info to the table
            start_time = datetime.fromtimestamp(self.game_start_time,
                                                timezone.utc)
            insert_values = (self.game_level, self.game_over, start_time)
            sql_statement = """INSERT INTO
                               play_history(level,
                                            finished,
                                            start_time)
                               VALUES (?,?,?)"""
            cur.execute(sql_statement, insert_values)
            conn.commit()
            logging.info("Adding a database entry for the start of a game "
                         "with level: %s, and start time: %s",
                         self.game_level,
                         start_time)
            self.db_id = cur.lastrowid
        else:
            # Update the table when the game has finished
            end_time = datetime.fromtimestamp(self.game_end_time, timezone.utc)
            insert_values = (self.game_won,
                             self.game_run_time,
                             self.game_over,
                             end_time,
                             self.db_id)
            sql_statement = """UPDATE play_history SET
                               game_won = ?,
                               game_run_time = ?,
                               finished = ?,
                               end_time = ?
                               WHERE id = ?"""
            cur.execute(sql_statement, insert_values)
            conn.commit()
            logging.info("Updating entry #%i in the database by adding game "
                         "won: %s, game run time: %i, game over: %s, and "
                         "end time: %s",
                         self.db_id,
                         self.game_won,
                         self.game_run_time,
                         self.game_over,
                         end_time)
            if self.game_won:
                self.check_for_fastest_time(conn, cur)
        logging.info("Closing the database connection")
        conn.close()

    def display_fastest_times(self):
        """Selects the 10 fastest times for the given level and calls
        show_top_times in order to create the display"""
        conn = sqlite3.connect('minesweeper.db')
        cur = conn.cursor()

        sql_statement = ("SELECT game_run_time, username FROM fastest_times "
                         "WHERE level=?")
        cur.execute(sql_statement, (self.game_level,))
        times_list = cur.fetchall()

        if not times_list:
            logging.info("There are no saved times for level: %s",
                         self.game_level)
            return
        else:
            sorted_times_list = sorted(times_list, key=lambda x: x[0])
            self.show_top_times(False, sorted_times_list)

    def check_for_fastest_time(self, conn, cur):
        """Checks if the finished game qualifies as one of the 10 fastest
        times for that level.  If so, a window will pop up showing the fastest
        times and asking the user to enter a username"""

        sql_statement = ("SELECT game_run_time, username FROM fastest_times "
                         "WHERE level=?")
        cur.execute(sql_statement, (self.game_level,))
        times_list = cur.fetchall()

        # If this is the first entry, then it must be the fastest
        if not times_list:
            logging.info("This is the first entry in the fastest times table "
                         "for level: %s", self.game_level)
            logging.info("Getting user info for a top time")
            self.show_top_times(True, [], 1)
            self.update_fastest_times(conn, cur, 1)
            return

        # Sort the list of time, username tuples by time
        sorted_times_list = sorted(times_list, key=lambda x: x[0])
        # Figure out the new entry's rank
        rank = 1
        for entry in sorted_times_list:
            if self.game_run_time <= entry[0]:
                break
            else:
                rank += 1
        if rank == 1:
            logging.info("Congrats! You just set the fastest time for "
                         "level: %s", self.game_level)

        # If there are less than 10 entries, just insert the new time
        if len(sorted_times_list) < 10:
            logging.info("Getting user info for a top time")
            self.show_top_times(True, sorted_times_list, rank)
            self.update_fastest_times(conn, cur, rank)

        # If there are more than 10 entries, then check if the new time
        # qualifies as one of the 10 fastest times. If so, then add the time
        # and remove the entry with the slowest time
        else:
            if rank <= 10:
                logging.info("Getting user info for a top time")
                self.show_top_times(True, sorted_times_list, rank)
                self.update_fastest_times(conn, cur, rank, sorted_times_list)
            else:
                logging.info("The previous game with a run time of %i seconds "
                             "does not qualify as one of the top 10 fastest "
                             "times for level %s",
                             self.game_run_time,
                             self.game_level)

    def update_fastest_times(self, conn, cur, rank, sorted_times_list=None):
        """Updates the fastest times table by adding an entry and by
        optionally deleting the slowest entry"""
        # Make sure the username was set before adding or deleting an entry
        if not self.username:
            logging.warning("Aborting fastest times table update because "
                            "one of the windows was closed")
            return

        # Delete the slowest entry if a list of times was passed
        if sorted_times_list is not None:
            # Remove the slowest time
            slowest_time = sorted_times_list[-1][0]
            sql_statement = ("SELECT id FROM fastest_times WHERE "
                             "game_run_time=? LIMIT 1")
            cur.execute(sql_statement, (slowest_time,))
            slow_id_arr = cur.fetchall()
            slow_id = slow_id_arr[0][0]
            sql_statement = "DELETE FROM fastest_times WHERE id=?"
            cur.execute(sql_statement, (slow_id,))
            conn.commit()
            logging.info("Removing the 10th place entry from the fastest "
                         "times table which had run time: %i seconds",
                         slowest_time)

        # Update the table with the new entry
        insert_values = (self.game_level,
                         self.game_run_time,
                         self.username)
        sql_statement = ("INSERT INTO "
                         "fastest_times(level, game_run_time, username) "
                         "VALUES (?,?,?)")
        cur.execute(sql_statement, insert_values)
        conn.commit()
        logging.info("Adding an entry to the fastest times table with "
                     "rank: %i, level: %s, run time: %i, and "
                     "username: %s",
                     rank,
                     self.game_level,
                     self.game_run_time,
                     self.username)

    def show_top_times(self, get_input, sorted_times_list, rank=-1):
        """Creates an entry line and enter button where the user can enter
        their username. If get_input is set to False then this method
        will only display the top times"""
        times_display_height = len(sorted_times_list) * 60 + 60
        if get_input:
            times_display_height = times_display_height + 60
            if len(sorted_times_list) < 10:
                times_display_height = times_display_height + 60
        logging.debug("Creating a display with height: %i",
                      times_display_height)
        self.times_display = TimesDisplay(get_input, times_display_height)

        # Add the times and usernames
        entry_num = 1
        if rank != -1:
            logging.info("The passed time rank is: %i", rank)
        for entry in sorted_times_list:
            logging.debug(entry)
            # If the entry number is equal to the rank being added, then
            # create a line with a username entry widget
            if entry_num == rank:
                self.times_display.add_entry(rank=entry_num,
                                             time=self.game_run_time,
                                             username=None,
                                             user_input=True)
                entry_num += 1

            # Otherwise, create a line with the entry info
            if entry_num <= 10:
                self.times_display.add_entry(rank=entry_num,
                                             time=entry[0],
                                             username=entry[1],
                                             user_input=False)
                entry_num += 1

        # If the user input is needed because this entry is slower than the
        # rest in the database but the number of entries is less than 10
        if get_input and rank > len(sorted_times_list):
            logging.debug("Adding the entry's results at the end")
            self.times_display.add_entry(rank=entry_num,
                                         time=self.game_run_time,
                                         username=None,
                                         user_input=True)

        # Create the enter button if the user is inputing their name
        if get_input:
            self.times_display.create_enter_button()
            self.times_display.root.bind("<Return>", self.check_user_input)
            self.times_display.enter_button.bind("<ButtonRelease-1>",
                                                 self.check_user_input)
            # Focus on the user entry
            self.times_display.user_entry.focus()

        # Maintain the user input display
        if get_input:
            self.board_display.root.wait_window(self.times_display.root)
        else:
            self.times_display.root.mainloop()
        logging.info("The input window has been closed")

    def check_user_input(self, event):
        """Checks the user input and then closes the window"""
        logging.debug("The button event info is: %s", event)
        input_text = self.times_display.input_var.get()
        if input_text == "":
            logging.warning("The input text was empty, please try again.")
        elif input_text is not None:
            logging.info("The passed text was: %s", input_text)
            self.username = input_text
            self.times_display.root.destroy()
        else:
            logging.error("Error, the input text variable was undefined")

    def update_header(self, smiley_type, display_time=0, num_mines=None):
        """Updates the smiley face button, the mine number label, and the
        timer label"""
        self.board_display.update_smiley_button(smiley_type)
        if num_mines is None:
            num_mines = self.board.num_mines_left
        self.update_mine_counter_display(num_mines)
        self.update_timer_display(display_time)

    def update_timer_display(self, display_time=None):
        """Updates the timer display in the header"""
        # If the game has been started and is currently ongoing
        if not self.game_over and self.game_start_time is not None:
            while not (self.closing_game or self.game_over):
                elapsed_time = int(round(time.time() -
                                         self.game_start_time, 0))
                elapsed_time = str(elapsed_time)
                num_chars = len(elapsed_time)
                if num_chars == 1:
                    elapsed_time = '0' + '0' + elapsed_time
                elif num_chars == 2:
                    elapsed_time = '0' + elapsed_time
                self.board_display.update_timer(elapsed_time)
                # Two .5 second sleeps instead of a 1 second sleep so that the
                # thread will close faster
                time.sleep(.5)
                if self.closing_game or self.game_over:
                    return
                time.sleep(.5)
            logging.info("Closing the timer thread")
        # If the game isn't currently running, populate the timer label
        # with the passed time
        else:
            display_time = str(display_time)
            num_chars = len(display_time)
            if num_chars == 1:
                display_time = '0' + '0' + display_time
            elif num_chars == 2:
                display_time = '0' + display_time
            self.board_display.update_timer(display_time)

    def update_mine_counter_display(self, num_mines):
        """Updates the mine counter display in the header"""
        if num_mines >= 0:
            num_mines = str(num_mines)
            num_chars = len(num_mines)
            if num_chars == 1:
                num_mines = '0' + '0' + num_mines
            elif num_chars == 2:
                num_mines = '0' + num_mines
        else:
            num_mines = str(num_mines)
            num_chars = len(num_mines)
            if num_chars == 2:
                num_mines = '-' + '0' + num_mines[1]
        self.board_display.update_mine_count(num_mines)

    def set_button_clicked(self, event, button):
        """Sets the button clicked flags"""
        logging.debug("The button event info is: %s", event)
        if button == 'right':
            self.is_right_clicked = True
        elif button == 'left':
            self.board_display.update_smiley_button('scared')
            self.is_left_clicked = True

    def set_button_unclicked(self, event, button):
        """Sets the button clicked flags"""
        logging.debug("The button event info is: %s", event)
        if button == 'right':
            self.is_right_clicked = False
        elif button == 'left':
            self.board_display.update_smiley_button('smiley')
            self.is_left_clicked = False

    def update_button(self, tile):
        """Updates the tile button"""
        logging.debug("Updating the button of type '%s' at column %s, row %s",
                      tile.button_type,
                      tile.column,
                      tile.row)
        # Delete the previous button bindings
        tile.button.unbind("<ButtonRelease-1>")
        tile.button.unbind("<ButtonRelease-3>")
        if tile.button_type == 'flag':
            tile.button.configure(image=self.photo_flag)
            tile.set_button_color("gray95")
            tile.button.bind('<ButtonRelease-1>',
                             lambda event, arg1='left':
                             self.set_button_unclicked(event, arg1))
            tile.button.bind('<ButtonRelease-3>',
                             lambda event, arg1=tile, arg2='right':
                             self.check_button_click(event, arg1, arg2))
        elif tile.button_type == 'blank':
            tile.button.configure(image='')
            tile.set_button_color("gray75")
            tile.button.bind('<ButtonRelease-1>',
                             lambda event, arg1=tile, arg2='left':
                             self.check_button_click(event, arg1, arg2))
            tile.button.bind('<ButtonRelease-3>',
                             lambda event, arg1=tile, arg2='right':
                             self.check_button_click(event, arg1, arg2))
        elif tile.button_type == 'uncovered':
            tile.button.configure(text=tile.num_adjacent_mines,
                                  font=('helvetica', 14))
            tile.set_button_color("gray95",
                                  number_colors[tile.num_adjacent_mines])
            tile.button.bind('<ButtonRelease-1>',
                             lambda event, arg1=tile, arg2='left':
                             self.check_button_click(event, arg1, arg2))
            tile.button.bind('<ButtonRelease-3>',
                             lambda event, arg1=tile, arg2='right':
                             self.check_button_click(event, arg1, arg2))

    def empty_tile_recursive_check(self, tile):
        """If the user clicks on an empty tile - no adjacent mines - then this
        function will uncover all self-contained empty tiles"""
        logging.debug("Running the empty tile recursive check on the tile at "
                      "column %i, row %i",
                      tile.column,
                      tile.row)
        for i in range(-1, 2):
            for j in range(-1, 2):
                test_column = tile.column + i
                test_row = tile.row + j
                # Make sure that the tile we're checking is an actual tile
                if ((test_column < 0 or test_column >= self.board.columns) or
                        (test_row < 0 or test_row >= self.board.rows)):
                    continue
                elif i == 0 and j == 0:
                    continue
                else:
                    test_tile = str(test_column) + ',' + str(test_row)
                    new_tile = self.board.tiles[test_tile]
                    if new_tile.is_flag_set:
                        continue
                    elif new_tile.is_hidden:
                        self.select_tile(new_tile, False)
                        if new_tile.num_adjacent_mines is None:
                            self.empty_tile_recursive_check(new_tile)

    def check_button_click(self, event, tile, button):
        """Checks if the user is attempting a left and right click at the same
        time, meaning that we should uncover all adjacent tiles at once. If
        just one button is pressed, the appropriate function is then called"""
        logging.debug("The button event info is: %s", event)
        if ((button == 'right' and self.is_left_clicked) or
                (button == 'left' and self.is_right_clicked)):
            self.board_display.update_smiley_button('smiley')
            if (tile.num_adjacent_mines ==
                    self.board.count_num_adjacent_flags(tile) and
                    not tile.is_hidden):
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        test_column = tile.column + i
                        test_row = tile.row + j
                        if self.game_over:
                            break
                        # Make sure that the tile is on the board
                        if ((test_column < 0 or
                             test_column >= self.board.columns) or
                                (test_row < 0 or
                                 test_row >= self.board.rows)):
                            continue
                        elif i == 0 and j == 0:
                            continue
                        else:
                            test_tile = str(test_column) + ',' + str(test_row)
                            new_tile = self.board.tiles[test_tile]
                            self.select_tile(new_tile, True)

            # Reset the button clicked flags
            self.is_left_clicked = False
            self.is_right_clicked = False
        else:
            if button == 'right':
                self.is_right_clicked = False
                if tile.is_hidden:
                    self.update_flag(tile)
            elif button == 'left':
                self.is_left_clicked = False
                self.board_display.update_smiley_button('smiley')
                if tile.is_hidden:
                    self.select_tile(tile, True)

    def update_flag(self, tile):
        """Add a flag to a tile, or remove it if there's already one there"""
        if not tile.is_flag_set:
            logging.debug("Adding a flag to the tile at column %s, row %s",
                          tile.column,
                          tile.row)
            tile.is_flag_set = True
            self.board.num_mines_left -= 1
            logging.debug("There are now %i mines left to clear",
                          self.board.num_mines_left)
            self.update_mine_counter_display(self.board.num_mines_left)
            tile.button_type = 'flag'
            self.update_button(tile)

        elif tile.is_flag_set:
            logging.debug("Removing the flag from the tile at column %s, "
                          "row %s",
                          tile.column,
                          tile.row)
            tile.is_flag_set = False
            self.board.num_mines_left += 1
            logging.debug("There are now %i mines left to clear",
                          self.board.num_mines_left)
            self.update_mine_counter_display(self.board.num_mines_left)
            tile.button_type = 'blank'
            self.update_button(tile)

    def select_tile(self, tile, recursive_check):
        """Check a tile and see if it was hiding a mine"""
        if self.is_first_tile:
            logging.debug("The first tile of the game was selected, now "
                          "setting all the mines")
            self.start_game_timer()
            self.board.set_the_mines(tile)
            self.is_first_tile = False
            # Update the database with the game info
            self.update_database()
            # Start the timer display
            self.timer_thread = threading.Thread(target=
                                                 self.update_timer_display)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            logging.info("Started timer thread: %s", self.timer_thread)

        if tile.is_mine and not tile.is_flag_set:
            self.game_won = False
            self.show_game_over(tile)
        elif not tile.is_mine:
            logging.debug("Selecting the tile at column %s, row %s",
                          tile.column,
                          tile.row)
            tile.is_hidden = False
            if tile.num_adjacent_mines is None:
                tile.disable_button(self.board_display.root)
                tile.set_button_color("gray95")
            else:
                tile.button_type = 'uncovered'
                self.update_button(tile)

            # Check if all the non-mine tiles have been cleared
            if (self.board.check_if_all_tiles_cleared() and not
                    self.game_over):
                self.game_won = True
                self.show_game_over()
            # Run the recursive check if there aren't any adjacent mines
            # Need to ensure that we aren't already running the recursive check
            if recursive_check and tile.num_adjacent_mines is None:
                self.empty_tile_recursive_check(tile)

    def show_game_over(self, exploded_tile=None):
        """Create the display for when the game is over"""
        # First, end the game timer
        self.end_game_timer()
        self.game_over = True

        if self.game_won:
            logging.info("Congrats! You safely cleared all the mines!")
            self.update_header('cool', self.game_run_time, 0)
        elif not self.game_won:
            self.update_header('dead', self.game_run_time)
            logging.info("Sorry, you exploded. Better luck next time!")
        if exploded_tile:
            exploded_x_pos = exploded_tile.position['x']
            exploded_y_pos = exploded_tile.position['y']

        # Disable all the tiles
        for tile in self.board.tiles.values():
            if tile.is_mine:
                if not self.game_won:
                    if ((tile.position['x'] == exploded_x_pos) and
                            (tile.position['y'] == exploded_y_pos)):
                        tile.disable_button(self.board_display.root)
                        tile.button.configure(image=self.photo_exploded_mine)
                    else:
                        tile.disable_button(self.board_display.root)
                        tile.button.configure(image=self.photo_mine)
                elif self.game_won:
                    tile.disable_button(self.board_display.root)
                    tile.button.configure(image=self.photo_flag)
                tile.set_button_color("gray95")
            else:
                tile.disable_button(self.board_display.root)
                tile.button.configure(text=tile.num_adjacent_mines,
                                      font=('helvetica', 14))
                tile.set_button_color("gray95",
                                      number_colors[tile.num_adjacent_mines])
                if tile.is_flag_set:
                    tile.button.configure(image=self.photo_wrong_mine)

        # Then update the database
        self.update_database()

    def restart_game(self):
        """Restars the game and resets the board"""
        self.restart_game_flag = True
        # Delete the whole display so the main thread can create a new one.
        # Due to Tkinter threading specifications, each instance of the game
        # needs to be started from the main thread.
        logging.info("Closing the window and starting another game")
        self.close_window()

    def start_game_timer(self):
        """Starts the game timer"""
        self.game_start_time = time.time()
        logging.debug("The game started at: %s", time.ctime())

    def end_game_timer(self):
        """Ends the game timer and calculates the game run time"""
        self.game_end_time = time.time()
        logging.debug("The game ended at: %s", time.ctime())
        self.game_run_time = int(round(self.game_end_time -
                                       self.game_start_time, 0))
        logging.info("The game lasted %i seconds", self.game_run_time)


def create_tables():
    """Creates the database and the tables, if they haven't already
    been created"""
    conn = sqlite3.connect('minesweeper.db')

    # Create the tables if they don't exist
    conn.execute("""CREATE TABLE IF NOT EXISTS play_history (
                        id integer PRIMARY KEY NOT NULL,
                        level text NOT NULL,
                        game_won int,
                        game_run_time int,
                        finished int NOT NULL,
                        start_time text NOT NULL,
                        end_time text);""")

    conn.execute("""CREATE TABLE IF NOT EXISTS fastest_times (
                        id integer PRIMARY KEY NOT NULL,
                        level text NOT NULL,
                        game_run_time int NOT NULL,
                        username text NOT NULL);""")
    conn.commit()
    conn.close()
