"""
Minesweeper!

Created on Wed May  1 22:49:31 2019

@author: danielb
"""

import logging
import time
from game import Game
from minesweeper_displays import LevelChoiceDisplay

def main():
    """Main"""
    restart_game = True
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s : %(funcName)s() - %(message)s',
        level=logging.INFO)
    program_start_time = time.time()

    # Create the level choice display
    level_choice = LevelChoiceDisplay()
    # Maintain the display; this will return when the window is closed
    level_choice.root.mainloop()

    # If view leaderboard was chosen then show the top times
    if level_choice.level and level_choice.view_leaderboard:
        view_board = Game(level_choice.level)
        view_board.display_fastest_times()

    # If play game was chosen then start a game
    elif level_choice.level and level_choice.play_game:
        while restart_game:
            # Force the restart game button to change the flag
            restart_game = False
            # Start the game
            new_game = Game(level_choice.level)
            new_game.start_game()
            # Maintain the display; this will return when the window is closed
            new_game.board_display.root.mainloop()
            if new_game.restart_game_flag:
                restart_game = True
            if not new_game.game_run_time:
                logging.info('The program was closed before the game finished')

    program_end_time = time.time()
    program_run_time = program_end_time - program_start_time
    logging.debug(f'The program ran for {program_run_time:.3f} seconds')
    logging.info('Ending the program and shutting down the logger')
    logging.shutdown()

if __name__ == '__main__':
    main()
