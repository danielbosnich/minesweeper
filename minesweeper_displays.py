"""
Created on Mon Nov 18 16:47:36 2019

@author: danielb
"""

import logging
from tkinter import (Tk, Button, Label, Checkbutton, BooleanVar, PhotoImage,
                     Toplevel, Entry, StringVar)
from minesweeper_dictionaries import level_info


class LevelChoiceDisplay():
    """Class for the display used to select a level and whether to play a game
    or view the leaderboard"""
    def __init__(self):
        # Display and widgets
        self.root = None
        self.checkbox_play = None
        self.checkbox_view = None
        # User choice variables
        self.play_game = None
        self.view_leaderboard = None
        self.check_var_play = None
        self.check_var_view = None
        self.level = None
        # Initialization methods
        self.__create_display_geometry()
        self.__add_widgets()

    def __create_display_geometry(self):
        """Creates the overall display"""
        self.root = Tk()
        self.root.title("Level Choice")
        display_width = 340
        display_height = 185
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        display_x_pos = screen_width/2 - display_width/2
        display_y_pos = screen_height*0.45 - display_height/2
        self.root.geometry('%dx%d+%d+%d' % (display_width,
                                            display_height,
                                            display_x_pos,
                                            display_y_pos))

    def __add_widgets(self):
        """Adds the widgets to the display"""
        # Text label
        choose_label = Label(self.root,
                             text="Choose a level",
                             font="Helvetica 12")
        choose_label.place(x=90, y=10, width=160, height=40)
        # Level choice buttons
        easy_button = Button(self.root,
                             text="Easy",
                             bg="green",
                             activebackground="dark green",
                             fg="white",
                             activeforeground="white",
                             font="Helvetica 11",
                             cursor="hand2")
        easy_button.place(x=10, y=55, width=100, height=50)
        easy_button.bind("<ButtonRelease-1>",
                         lambda event,
                                arg1="easy":
                         self.set_level(event, arg1))
        easy_button.bind("<Enter>",
                         lambda event,
                                arg1=easy_button,
                                arg2="dark green":
                         update_button_color(event, arg1, arg2))
        easy_button.bind("<Leave>",
                         lambda event,
                                arg1=easy_button,
                                arg2="green":
                         update_button_color(event, arg1, arg2))
        medium_button = Button(self.root,
                               text="Medium",
                               bg="blue",
                               activebackground="medium blue",
                               fg="white",
                               activeforeground="white",
                               font="Helvetica 11",
                               cursor="hand2")
        medium_button.place(x=120, y=55, width=100, height=50)
        medium_button.bind("<ButtonRelease-1>",
                           lambda event,
                                  arg1="medium":
                           self.set_level(event, arg1))
        medium_button.bind("<Enter>",
                           lambda event,
                                  arg1=medium_button,
                                  arg2="medium blue":
                           update_button_color(event, arg1, arg2))
        medium_button.bind("<Leave>",
                           lambda event,
                                  arg1=medium_button,
                                  arg2="blue":
                           update_button_color(event, arg1, arg2))
        hard_button = Button(self.root,
                             text="Hard",
                             bg="red",
                             activebackground="red3",
                             fg="white",
                             activeforeground="white",
                             font="Helvetica 11",
                             cursor="hand2")
        hard_button.place(x=230, y=55, width=100, height=50)
        hard_button.bind("<ButtonRelease-1>",
                         lambda event,
                                arg1="hard":
                         self.set_level(event, arg1))
        hard_button.bind("<Enter>",
                         lambda event,
                                arg1=hard_button,
                                arg2="red3":
                         update_button_color(event, arg1, arg2))
        hard_button.bind("<Leave>",
                         lambda event,
                                arg1=hard_button,
                                arg2="red":
                         update_button_color(event, arg1, arg2))

        # Create the checkboxes
        self.check_var_play = BooleanVar()
        self.check_var_view = BooleanVar()
        self.checkbox_play = Checkbutton(self.root,
                                         text="Play Game",
                                         font="Helvetica 11",
                                         variable=self.check_var_play,
                                         command=self.update_view_check)
        self.checkbox_play.place(x=70, y=120, width=200, height=25)
        self.checkbox_view = Checkbutton(self.root,
                                         text="View Leaderboard",
                                         font="Helvetica 11",
                                         variable=self.check_var_view,
                                         command=self.update_play_check)
        self.checkbox_view.place(x=70, y=150, width=200, height=25)
        self.checkbox_play.select()

    def set_level(self, event, chosen_level):
        """Sets the game level and closes the level choice display"""
        logging.debug("The button event info is: %s", event)
        self.level = chosen_level
        self.play_game = self.check_var_play.get()
        self.view_leaderboard = self.check_var_view.get()
        if self.play_game:
            logging.info("The user chose to play a game at level %s",
                         self.level)
        else:
            logging.info("The user chose to view the leaderboard for level %s",
                         self.level)
        self.root.destroy()

    def update_view_check(self):
        """Removes the check for view leaderboard if play game was selected"""
        if self.check_var_play.get():
            self.checkbox_view.deselect()

    def update_play_check(self):
        """Removes the check for play game if view leaderboard was selected"""
        if self.check_var_view.get():
            self.checkbox_play.deselect()


class BoardDisplay():
    """Class for the minesweeper board display"""
    def __init__(self, level):
        # Display and widgets
        self.root = None
        self.mine_count_label = None
        self.smiley_button = None
        self.timer_label = None
        # Variables
        self.display_width = None
        self.display_offset = 60
        # Initialization methods
        self.__create_display_geometry(level)
        self.__add_widgets()

    def __create_display_geometry(self, level):
        """Creates the overall display"""
        self.root = Tk()
        self.root.title("Minesweeper")
        self.display_width = level_info[level]['display_width']
        display_height = (level_info[level]['display_height'] +
                          self.display_offset)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        display_x_pos = screen_width/2 - self.display_width/2
        display_y_pos = screen_height*0.45 - display_height/2
        self.root.geometry('%dx%d+%d+%d' % (self.display_width,
                                            display_height,
                                            display_x_pos,
                                            display_y_pos))

        # Load images
        # Need to define the file paths separately for tkinter
        cool_emoji_path = "Images/cool_emoji.gif"
        dead_emoji_path = "Images/dead_emoji.gif"
        scared_emoji_path = "Images/scared_emoji.gif"
        smiley_emoji_path = "Images/smiley_emoji.gif"
        self.root.cool_emoji = PhotoImage(file=cool_emoji_path)
        self.root.dead_emoji = PhotoImage(file=dead_emoji_path)
        self.root.scared_emoji = PhotoImage(file=scared_emoji_path)
        self.root.smiley_emoji = PhotoImage(file=smiley_emoji_path)

    def __add_widgets(self):
        """Adds widgets to the display"""
        # Create the header label
        header_label = Label(self.root,
                             bg="gray70",
                             relief="raised")
        header_label.place(x=0, y=0,
                           height=self.display_offset,
                           width=self.display_width)

        # Create the mines count label
        self.mine_count_label = Label(self.root,
                                      bg="gray22",
                                      fg="red")
        self.mine_count_label.configure(font=('stencil', 28))
        self.mine_count_label.place(x=15, y=5, width=100, height=50)

        # Create the smiley button
        self.smiley_button = Button(self.root, bg="white", cursor="hand2")
        self.smiley_button.place(x=self.display_width/2 - 50/2, y=5,
                                 width=50, height=50)

        # Create the timer label
        self.timer_label = Label(self.root,
                                 bg="gray22",
                                 fg="red",
                                 font="Stencil 28")
        self.timer_label.place(x=self.display_width - 115, y=5,
                               width=100, height=50)

    def update_smiley_button(self, smiley_type):
        """Updates the smiley button in the header"""
        if smiley_type == 'smiley':
            self.smiley_button.configure(image=self.root.smiley_emoji)
        elif smiley_type == 'scared':
            self.smiley_button.configure(image=self.root.scared_emoji)
        elif smiley_type == 'cool':
            self.smiley_button.configure(image=self.root.cool_emoji)
        elif smiley_type == 'dead':
            self.smiley_button.configure(image=self.root.dead_emoji)

    def update_timer(self, time):
        """Updates the timer text"""
        self.timer_label.configure(text=time)

    def update_mine_count(self, mine_count):
        """Updates the mine count label text"""
        self.mine_count_label.configure(text=mine_count)


class TimesDisplay():
    """Class for the minesweeper top times display"""
    def __init__(self, get_input, display_height):
        # Display and widgets
        self.root = None
        self.user_entry = None
        self.enter_button = None
        # Variables
        self.get_input = get_input
        self.display_width = 400
        self.display_height = display_height
        self.input_var = None
        # Initialization methods
        self.__create_display_geometry()
        self.__add_widgets()

    def __create_display_geometry(self):
        """Creates the overall display"""
        if self.get_input:
            self.root = Toplevel()
        else:
            self.root = Tk()
        self.root.title("Top Times")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        display_x_pos = screen_width/2 - self.display_width/2
        display_y_pos = screen_height*0.45 - self.display_height/2
        self.root.geometry('%dx%d+%d+%d' % (self.display_width,
                                            self.display_height,
                                            display_x_pos,
                                            display_y_pos))

    def __add_widgets(self):
        """Adds widgets to the display"""
        # Create the background and header
        header_background = Label(self.root,
                                  bg="gray98",
                                  relief="raised")
        header_background.place(x=0, y=0, width=self.display_width, height=60)
        if self.get_input:
            footer_background = Label(self.root,
                                      bg="gray98",
                                      relief="raised")
            footer_background.place(x=0, y=self.display_height-60,
                                    width=self.display_width, height=60)
        rank_label = Label(self.root,
                           text='Rank',
                           bg="gray98",
                           fg="black",
                           font="Helvetica 14 bold")
        rank_label.place(x=30, y=10, width=60, height=40)
        username_label = Label(self.root,
                               text='User',
                               bg="gray98",
                               fg="black",
                               font="Helvetica 14 bold")
        username_label.place(x=140, y=10, width=120, height=40)
        time_label = Label(self.root,
                           text='Time',
                           bg="gray98",
                           fg="black",
                           font="Helvetica 14 bold")
        time_label.place(x=300, y=10, width=80, height=40)

    def add_entry(self, rank, time, username, user_input):
        """Adds a time to the display"""
        color = determine_color(rank)
        y_pos = (rank) * 60 + 10
        # Color separation label
        entry_label = Label(self.root, bg=color, relief="raised")
        entry_label.place(x=0, y=y_pos-10, width=self.display_width, height=60)
        self.add_rank(y_pos, color, rank)
        self.add_time(y_pos, color, time)
        if user_input:
            self.create_username_entry(y_pos)
        else:
            self.add_username(y_pos, color, username)

    def add_rank(self, y_pos, color, rank):
        """Adds the rank number"""
        entry_rank = Label(self.root,
                           text=rank,
                           bg=color,
                           font="Helvetica 12")
        entry_rank.place(x=50, y=y_pos, width=20, height=40)

    def add_time(self, y_pos, color, time):
        """Adds the time"""
        entry_time = Label(self.root,
                           text=time,
                           bg=color,
                           font="Helvetica 12")
        entry_time.place(x=320, y=y_pos, width=40, height=40)

    def add_username(self, y_pos, color, username):
        """Adds the username"""
        entry_username = Label(self.root,
                               text=username,
                               bg=color,
                               font="Helvetica 12")
        entry_username.place(x=100, y=y_pos, width=200, height=40)

    def create_username_entry(self, y_pos):
        """Creates the username entry widget"""
        self.input_var = StringVar()
        self.user_entry = Entry(self.root,
                                textvariable=self.input_var,
                                justify="center",
                                font="Helvetica 12")
        self.user_entry.place(x=100, y=y_pos, width=200, height=40)

    def create_enter_button(self):
        """Creates the enter button"""
        self.enter_button = Button(self.root,
                                   text="Enter Username",
                                   bg="gray98",
                                   activebackground="gray98",
                                   cursor="hand2",
                                   font="Helvetica 14")
        self.enter_button.place(x=100, y=self.display_height-50,
                                width=200, height=40)
        self.enter_button.bind("<Enter>",
                               lambda event,
                                      arg1=self.enter_button,
                                      arg2="gray94":
                               update_button_color(event, arg1, arg2))
        self.enter_button.bind("<Leave>",
                               lambda event,
                                      arg1=self.enter_button,
                                      arg2="gray98":
                               update_button_color(event, arg1, arg2))


def update_button_color(event, button, color):
    """Updates the button color"""
    logging.debug("The button event info is: %s", event)
    button.configure(bg=color, activebackground=color)

def determine_color(num):
    """Returns a shade of gray for the top times display based on whether the
    passed number is odd or even"""
    if num % 2 == 0:
        return "gray90"
    return "gray80"
