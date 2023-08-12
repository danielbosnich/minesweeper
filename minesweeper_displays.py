"""
Module with the class implementations for each of the displays
"""

import logging
import random
from tkinter import (Tk, Button, Label, Checkbutton, BooleanVar, PhotoImage,
                     Toplevel, Entry, StringVar)
from minesweeper_details import LEVEL_INFO, DISPLAY_OFFSET

# Randomly chooses which bob-omb icon should be used for the displays
if random.choice([True, False]):
    ICON_PATH = 'images/bob-omb.ico'
else:
    ICON_PATH = 'images/bob-omb_red.ico'


class LevelChoiceDisplay():
    """Class for the display used to select a level and whether to play a game
    or view the leaderboard"""
    def __init__(self):
        """Initializes a LevelChoiceDisplay object"""
        # Display and widgets
        self.root = None
        self._checkbox_play = None
        self._checkbox_view = None
        # User choice variables
        self.level = None
        self.play_game = None
        self.view_leaderboard = None
        self._check_var_play = None
        self._check_var_view = None
        # Initialization methods
        self._create_display_geometry()
        self._add_widgets()

    def _create_display_geometry(self):
        """Creates the overall display"""
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.title('Level Choice')
        self.root.iconbitmap(ICON_PATH)
        display_width = 300
        display_height = 165
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        display_x_pos = screen_width/2 - display_width/2
        display_y_pos = screen_height*0.45 - display_height/2
        self.root.geometry(f'{display_width}x{display_height}'
                           f'+{display_x_pos}+{display_y_pos}')

    def _add_widgets(self):
        """Adds the widgets to the display"""
        # Text label
        choose_label = Label(self.root,
                             text='Choose a level',
                             font='Arial 14')
        choose_label.place(x=80, y=10, width=140, height=30)
        # Level choice buttons
        easy_button = Button(self.root,
                             text='Easy',
                             background='green4',
                             activebackground='dark green',
                             foreground='white',
                             activeforeground='white',
                             font='Arial 12',
                             cursor='hand2',
                             command=lambda: self._set_level('easy'))
        easy_button.place(x=15, y=50, width=80, height=40)
        easy_button.bind('<Enter>',
                         lambda event,
                                arg1=easy_button,
                                arg2='dark green':
                         update_button_color(arg1, arg2))
        easy_button.bind('<Leave>',
                         lambda event,
                                arg1=easy_button,
                                arg2='green4':
                         update_button_color(arg1, arg2))
        medium_button = Button(self.root,
                               text='Medium',
                               background='blue',
                               activebackground='medium blue',
                               foreground='white',
                               activeforeground='white',
                               font='Arial 12',
                               cursor='hand2',
                               command=lambda: self._set_level('medium'))
        medium_button.place(x=110, y=50, width=80, height=40)
        medium_button.bind('<Enter>',
                           lambda event,
                                  arg1=medium_button,
                                  arg2='medium blue':
                           update_button_color(arg1, arg2))
        medium_button.bind('<Leave>',
                           lambda event,
                                  arg1=medium_button,
                                  arg2='blue':
                           update_button_color(arg1, arg2))
        hard_button = Button(self.root,
                             text='Hard',
                             background='red',
                             activebackground='red3',
                             foreground='white',
                             activeforeground='white',
                             font='Arial 12',
                             cursor='hand2',
                             command=lambda: self._set_level('hard'))
        hard_button.place(x=205, y=50, width=80, height=40)
        hard_button.bind('<Enter>',
                         lambda event,
                                arg1=hard_button,
                                arg2='red3':
                         update_button_color(arg1, arg2))
        hard_button.bind('<Leave>',
                         lambda event,
                                arg1=hard_button,
                                arg2='red':
                         update_button_color(arg1, arg2))

        # Create the checkboxes
        self._check_var_play = BooleanVar()
        self._check_var_view = BooleanVar()
        self._checkbox_play = Checkbutton(self.root,
                                          text='Play Game',
                                          font='Arial 11',
                                          variable=self._check_var_play,
                                          command=self._update_view_check)
        self._checkbox_play.place(x=50, y=100, width=200, height=25)
        self._checkbox_view = Checkbutton(self.root,
                                          text='View Leaderboard',
                                          font='Arial 11',
                                          variable=self._check_var_view,
                                          command=self._update_play_check)
        self._checkbox_view.place(x=50, y=130, width=200, height=25)
        self._checkbox_play.select()

    def _set_level(self, chosen_level):
        """Sets the game level and closes the level choice display

        Args:
            chosen_level (str): The difficulty level chosen by the user
        """
        self.level = chosen_level
        self.play_game = self._check_var_play.get()
        self.view_leaderboard = self._check_var_view.get()
        if self.play_game:
            logging.info(f'The user chose to play a game at level: '
                         f'{self.level}')
        else:
            logging.info(f'The user chose to view the leaderboard for level: '
                         f'{self.level}')
        self.root.destroy()

    def _update_view_check(self):
        """Removes the check for view leaderboard if play game was selected"""
        if self._check_var_play.get():
            self._checkbox_view.deselect()

    def _update_play_check(self):
        """Removes the check for play game if view leaderboard was selected"""
        if self._check_var_view.get():
            self._checkbox_play.deselect()


class BoardDisplay():
    """Class for the minesweeper board display"""
    def __init__(self, level):
        """Initializes a BoardDisplay object

        Args:
            level (str): The difficulty level of the game
        """
        # Display and widgets
        self.root = None
        self._miley_button = None
        self._mine_count_label = None
        self._timer_label = None
        # Variables
        self._display_width = None
        # Initialization methods
        self._create_display_geometry(level)
        self._add_widgets()

    def _create_display_geometry(self, level):
        """Creates the overall display"""
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.title('Minesweeper')
        self.root.iconbitmap(ICON_PATH)
        self._display_width = LEVEL_INFO[level]['display_width']
        display_height = (LEVEL_INFO[level]['display_height'] + DISPLAY_OFFSET)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        display_x_pos = screen_width/2 - self._display_width/2
        display_y_pos = screen_height*0.45 - display_height/2
        self.root.geometry(f'{self._display_width}x{display_height}'
                           f'+{display_x_pos}+{display_y_pos}')

        # Load images
        # Need to define the file paths separately for tkinter
        cool_emoji_path = 'images/cool_emoji.gif'
        dead_emoji_path = 'images/dead_emoji.gif'
        scared_emoji_path = 'images/scared_emoji.gif'
        smiley_emoji_path = 'images/smiley_emoji.gif'
        self.root.cool_emoji = PhotoImage(file=cool_emoji_path)
        self.root.dead_emoji = PhotoImage(file=dead_emoji_path)
        self.root.scared_emoji = PhotoImage(file=scared_emoji_path)
        self.root.smiley_emoji = PhotoImage(file=smiley_emoji_path)

    def _add_widgets(self):
        """Adds widgets to the display"""
        # Create the header label
        header_label = Label(self.root,
                             background='gray70',
                             relief='raised')
        header_label.place(x=0,
                           y=0,
                           height=DISPLAY_OFFSET,
                           width=self._display_width)

        # Create the mines count label
        self._mine_count_label = Label(self.root,
                                       background='gray22',
                                       foreground='red')
        self._mine_count_label.configure(font=('stencil', 28))
        self._mine_count_label.place(x=10,
                                     y=5,
                                     width=90,
                                     height=40)

        # Create the smiley button
        self.smiley_button = Button(self.root,
                                    background='white',
                                    cursor='hand2')
        self.smiley_button.place(x=self._display_width/2 - 40/2,
                                 y=5,
                                 width=40,
                                 height=40)

        # Create the timer label
        self._timer_label = Label(self.root,
                                  background='gray22',
                                  foreground='red',
                                  font='Stencil 28')
        self._timer_label.place(x=self._display_width - 100,
                                y=5,
                                width=90,
                                height=40)

    def update_smiley_button(self, smiley_type):
        """Updates the smiley button in the header

        Args:
            smiley_type (str): Type of smiley to update the button to
        """
        if smiley_type == 'smiley':
            self.smiley_button.configure(image=self.root.smiley_emoji)
        elif smiley_type == 'scared':
            self.smiley_button.configure(image=self.root.scared_emoji)
        elif smiley_type == 'cool':
            self.smiley_button.configure(image=self.root.cool_emoji)
        elif smiley_type == 'dead':
            self.smiley_button.configure(image=self.root.dead_emoji)

    def update_timer(self, time):
        """Updates the timer text

        Args:
            time (int): Time to update the label to
        """
        self._timer_label.configure(text=time)

    def update_mine_count(self, mine_count):
        """Updates the mine count label text

        Args:
            mine_count (int): Mine count to update the label to
        """
        self._mine_count_label.configure(text=mine_count)


class TimesDisplay():
    """Class for the minesweeper top times display"""
    header_height = 50
    footer_height = 50
    entry_height = 40
    window_bg_color = 'gray98'
    light_gray = 'gray90'
    dark_gray = 'gray80'

    def __init__(self, *, get_input, num_entries):
        """Initializes a TimesDisplay object

        Args:
            get_input (bool): If user input is needed
            num_entries (int): Number of entries for the list
        """
        # Display and widgets
        self.root = None
        self.user_entry = None
        self.enter_button = None
        # Variables
        self._get_input = get_input
        self._display_width = 400
        self._display_height = None
        self.input_var = None
        # Initialization methods
        self._determine_height(num_entries)
        self._create_display_geometry()
        self._add_widgets()

    def _determine_height(self, num_entries):
        """Determines the height of the display based on the number of entries
        and if user input is required

        Args:
            num_entries (int): Number of entries for the list
        """
        self._display_height = (num_entries * self.entry_height +
                                self.header_height)
        if self._get_input:
            self._display_height += self.footer_height
            if num_entries < 10:
                self._display_height += self.entry_height

    def _create_display_geometry(self):
        """Creates the overall display"""
        if self._get_input:
            self.root = Toplevel()
        else:
            self.root = Tk()
        self.root.resizable(False, False)
        self.root.title('Top Times')
        self.root.iconbitmap(ICON_PATH)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        display_x_pos = screen_width/2 - self._display_width/2
        display_y_pos = screen_height*0.45 - self._display_height/2
        self.root.geometry(f'{self._display_width}x{self._display_height}'
                           f'+{display_x_pos}+{display_y_pos}')

    def _add_widgets(self):
        """Adds widgets to the display"""
        # Create the background and header
        header_background = Label(self.root,
                                  background=self.window_bg_color,
                                  relief='raised')
        header_background.place(x=0, y=0,
                                width=self._display_width,
                                height=self.header_height)
        if self._get_input:
            footer_background = Label(self.root,
                                      background=self.window_bg_color,
                                      relief='raised')
            footer_background.place(x=0,
                                    y=self._display_height - self.footer_height,
                                    width=self._display_width,
                                    height=self.footer_height)
        rank_label = Label(self.root,
                           text='Rank',
                           background=self.window_bg_color,
                           foreground='black',
                           font='Arial 14 bold')
        rank_label.place(x=30, y=5, width=60, height=40)
        username_label = Label(self.root,
                               text='User',
                               background=self.window_bg_color,
                               foreground='black',
                               font='Arial 14 bold')
        username_label.place(x=140, y=5, width=120, height=40)
        time_label = Label(self.root,
                           text='Time',
                           background=self.window_bg_color,
                           foreground='black',
                           font='Arial 14 bold')
        time_label.place(x=300, y=5, width=80, height=40)

    def add_entry(self, *, rank, time, username, user_input):
        """Adds a time to the display

        Args:
            rank (int): Rank of the new entry
            time (int): Time of the new entry
            username (str): Username for the new entry
            user_input (bool): The entry should be created with an Entry widget
                for the user to add their username
        """
        color = self._determine_color(rank)
        y_pos = (rank - 1) * self.entry_height + self.header_height
        # Color separation label
        entry_label = Label(self.root, background=color, relief='raised')
        entry_label.place(x=0, y=y_pos,
                          width=self._display_width,
                          height=self.entry_height)
        y_pos += 5  # Add 5 so that the entry label's edges are clean
        self._add_rank(y_pos, color, rank)
        self._add_time(y_pos, color, time)
        if user_input:
            self._create_username_entry(y_pos)
        else:
            self._add_username(y_pos, color, username)

    def _add_rank(self, y_pos, color, rank):
        """Adds the rank number

        Args:
            y_pos (int): Y position for the rank label
            color (str): Color of the label
            rank (int): Rank of the entry
        """
        entry_rank = Label(self.root,
                           text=rank,
                           background=color,
                           font='Arial 12')
        entry_rank.place(x=50, y=y_pos, width=20, height=30)

    def _add_time(self, y_pos, color, time):
        """Adds the time

        Args:
            y_pos (int): Y position for the time label
            color (str): Color of the label
            time (int): Time for the entry
        """
        entry_time = Label(self.root,
                           text=time,
                           background=color,
                           font='Arial 12')
        entry_time.place(x=320, y=y_pos, width=40, height=30)

    def _add_username(self, y_pos, color, username):
        """Adds the username

        Args:
            y_pos (int): Y position for the username label
            color (str): Color of the label
            username (str): Username for the label
        """
        entry_username = Label(self.root,
                               text=username,
                               background=color,
                               font='Arial 12')
        entry_username.place(x=100, y=y_pos, width=200, height=30)

    def _create_username_entry(self, y_pos):
        """Creates the username entry widget

        Args:
            y_pos (int): Y position for the entry widget
        """
        self.input_var = StringVar()
        self.user_entry = Entry(self.root,
                                textvariable=self.input_var,
                                justify='center',
                                font='Arial 12')
        self.user_entry.place(x=100, y=y_pos, width=200, height=30)

    def create_enter_button(self):
        """Creates the enter button"""
        self.enter_button = Button(self.root,
                                   text='Enter Username',
                                   background=self.window_bg_color,
                                   activebackground=self.window_bg_color,
                                   cursor='hand2',
                                   font='Arial 14')
        self.enter_button.place(x=100,
                                y=self._display_height-43,
                                width=200,
                                height=36)
        self.enter_button.bind('<Enter>',
                               lambda event,
                                      arg1=self.enter_button,
                                      arg2='gray94':
                               update_button_color(arg1, arg2))
        self.enter_button.bind('<Leave>',
                               lambda event,
                                      arg1=self.enter_button,
                                      arg2='gray98':
                               update_button_color(arg1, arg2))

    def _determine_color(self, num):
        """Returns a shade of gray for the top times display based on whether
        the passed number is odd or even

        Args:
            num (int): Number to check
        Returns:
            str: The correct shade of gray
        """
        if num % 2 == 0:
            return self.light_gray
        return self.dark_gray


def update_button_color(button, color):
    """Updates the passed button's color

    Args:
        button: Tkinter button object
        color (str): Color to set the button background
    """
    button.configure(background=color, activebackground=color)
