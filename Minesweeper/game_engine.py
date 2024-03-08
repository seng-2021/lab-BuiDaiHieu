"""
This file compiles modules and defines functions that run the Minesweeper.
state = stores important values for all functions to share.
game_choices, scoreboard_choices = choices for user input when starting
a new game and for browsing though the scoreboard.
buttons = assigns mouse clicks to right, left and middle from sweeperlib

Made by:
    Hieu Bui
    Niklas Raesalmi
    Niranjan Sreegith
"""
import math
import random
import datetime as dt
import os
import csv
import sys
import sweeperlib as sw
from pathlib import Path

scoreboard_location = Path(__file__).with_name("scoreboard.csv")
sprites_location = "sprites"

state = {
    "field": [],
    "player_field": [],
    "available_tiles": [],
    "mines": 0,
    "remaining": 0,
    "size": 40,
    "first_click": False,
    "winning": False,
    "mines_count": 0,
    "time": 0,
    "move": 0,
    "date": "",
    "player_name": ""
}


game_choices = ["n", "s", "q"]
scoreboard_choices = ["1", "2", "q"]

buttons = {
    sw.MOUSE_LEFT: "left",
    sw.MOUSE_MIDDLE: "middle",
    sw.MOUSE_RIGHT: "right"
}

def show_score():
    """
    Prints the result of game, date and time, time taken, no. of moves
    and unflgged mines after the game ends
    """
    os.system('cls')
    if state["winning"]:
        print("You win!")
    else:
        print("You lose!")
    state["date"] = state["date"].strftime('%d.%m.%Y %H:%M:%S')
    date, time, move, count = state['date'], state['time'], state['move'], state['mines_count']
    print(f"Date: {date}, Time Elapsed: {time} seconds, Moves: {move}, Unflagged mines: {count}")
    add_score(scoreboard_location)

def count_mines(_x, _y, given_field):
    """
    Counts the number of mines around a tile and assigns the
    value to the counter
    """
    row = len(given_field)
    column = len(given_field[0])
    counter = 0

    for j in range(row):
        for i in range(column):
            if i in (_x-1, _x, _x+1) and j in (_y-1, _y, _y+1) and given_field[j][i] == "x":
                counter += 1
    return counter

def floodfill(player_field, field, starting_x, starting_y):
    """
    Marks previously unknown connected areas as safe, starting from the given
    x, y coordinates.

    player_field: the field which the player see
    field: the field which control the moves
    starting_x, starting_y: initial coordinates
    """
    state["move"] += 1
    if field[starting_y][starting_x] == "x":
        sw.close()
        state["date"] = dt.datetime.now()
        show_score()
        return

    safe = [(starting_x, starting_y)]
    safe_values = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
    nearby_tiles = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    state["remaining"] -= 1

    while safe:
        col, row = safe.pop(-1)
        field[row][col] = str(count_mines(col, row, field))
        player_field[row][col] = field[row][col]
        for step in nearby_tiles:
            if 0 <= step[0]+col < len(field[0]) and 0 <= step[1]+row < len(field):
                if field[step[1]+row][step[0]+col] in safe_values:
                    pass
                elif field[step[1]+row][step[0]+col] != "x":
                    field[step[1]+row][step[0]+col]=str(count_mines(step[0]+col,step[1]+row,field))
                    player_field[step[1]+row][step[0]+col] = field[step[1]+row][step[0]+col]
                    if field[step[1]+row][step[0]+col] == "0":
                        safe.append((step[0]+col, step[1]+row))
                    state["remaining"] -= 1

    if state["remaining"] == state["mines"]:
        state["winning"] = True
        sw.close()
        state["date"] = dt.datetime.now()
        show_score()
        return


def first_click_handler(col, row):
    """
    Prevents the player from landing on a mine on the first click.
    Also the function starts the timer function upon the player's first click.
    """
    while not state["first_click"]:
        sw.set_interval_handler(timer, 1)
        state["available_tiles"].remove((col, row))
        state["field"] = place_mines(state["field"], state["available_tiles"], state["mines"])
        floodfill(state["player_field"], state["field"], col, row)
        state["first_click"] = True

def click_handle(_x, _y, button, modifiers):
    """
    This function is called when a mouse button is clicked inside the game window.
    Prints the position and clicked button of the mouse to the terminal.
    """

    col = _x // state["size"]
    row = _y // state["size"]

    if buttons[button] == "right":
        if state["player_field"][row][col] == " ":
            state["player_field"][row][col] = "f"
            state["mines_count"] -= 1
        elif state["player_field"][row][col] == "f":
            state["player_field"][row][col] = " "
            state["mines_count"] += 1
    else:
        if state["player_field"][row][col] == " ":
            first_click_handler(col, row)
            floodfill(state["player_field"], state["field"], col, row)

def place_mines(field_to_place, available_tile, mines_number):
    """
    Places N mines to a field in random tiles.
    """
    for _ in range(mines_number):
        (col_number, row_number) = random.choice(available_tile)
        field_to_place[row_number][col_number] = "x"
        available_tile.remove((col_number, row_number))
    return field_to_place

def draw_field():
    """
    A handler function that draws a field represented by a two-dimensional list
    into a game window. This function is called whenever the game engine requests
    a screen update.
    """
    field_to_draw = state["player_field"]
    sw.clear_window()
    sw.draw_background()
    sw.begin_sprite_draw()
    for row_num, row_content in enumerate(field_to_draw):
        for column_num, cell_content in enumerate(row_content):
            key = cell_content
            sw.prepare_sprite(key, column_num*state["size"], row_num*state["size"])
    sw.draw_sprites()

def field_data():
    """
    A function that collects player name, field dimensions and number of mines.
    The function then assigns the inputs into state.
    """
    while True:
        p_name = str(input("Give player name (max 15 characters): "))
        if len(p_name) > 14:
            print("Name must be under 15 characters!")
        elif len(p_name) == 0:
            print("Name must have at least 1 character!")
        else:
            break

    while True:
        try:
            width = int(input("Give width (Must be between 5-45): "))
        except ValueError:
            print("Invalid input")
            continue
        if width < 5 or width > 45:
            print("Invalid size")
        else:
            break

    while True:
        try:
            height = int(input("Give height (Must be between 5-25): "))
        except ValueError:
            print("Invalid input")
            continue
        if height < 5 or height > 25:
            print("Invalid size")
        else:
            break

    while True:
        try:
            mines = int(input("Give the number of mines (Must be 10 or more): "))
        except ValueError:
            print("Invalid input")
            continue
        if mines < 10 or mines > width * height - 1:
            print(("Too many or too few mines"))
        else:
            break

    field = []
    player_field = []
    for _ in range(height):
        field.append([])
        player_field.append([])
        for _ in range(width):
            field[-1].append(" ")
            player_field[-1].append(" ")

    available = []
    for _y in range(height):
        for _x in range(width):
            available.append((_x, _y))

    state["field"] = field
    state["player_field"] = player_field
    state["mines"] = mines
    state["available_tiles"] = available
    state["remaining"] = width * height
    state["mines_count"] = mines
    state["player_name"] = p_name

def timer(elapsed):
    """
    A function that counts the length of a game in seconds
    and assigns the value to state at the end.
    """
    os.system('cls')
    elapsed = state["time"]
    print(f"Time elapsed: {elapsed}")
    state["time"] += 1

def new_game():
    """
    Clears previous data and presents a new game window
    """
    state["winning"] = False
    state["first_click"] = False
    state["time"] = 0
    state["move"] = 0
    state["date"] = 0
    field_data()
    sw.load_sprites(sprites_location)
    sw.create_window(len(state["field"][0])*state["size"], len(state["field"])*state["size"])
    sw.set_draw_handler(draw_field)
    sw.set_mouse_handler(click_handle)
    sw.start()

def prompt_choice(choices):
    """
    Function to input the next action you want to do with the pet:
    q: quit the game
    n: new game
    s: show scoreboard
    """
    print(f"Select one choice: {', '.join(choices)}")
    while True:
        choice = input("Input next choice: ").lower()
        if choice in choices:
            return choice
        print("Invalid input!")

def no_entry(file):
    """
    A function that finds the number of rows in current scoreboard entries.
    """
    with open(file, 'r', encoding="utf-8") as data:
        no_rows = 0
        for _ in data:
            no_rows += 1
        return no_rows

def add_score(file):
    """
    Function that pulls current state values into end_values and then makes
    a new entry to scoreboard.csv as a new row.
    """
    with open(file, 'a', newline='', encoding="utf-8") as data:
        new_entry = no_entry(file) + 1
        end_values = [new_entry, state["player_name"], state["date"]]
        end_values.extend([state["time"],state["move"],state["winning"],state["mines_count"]])
        for i in end_values:
            str(i)
        new_score = csv.writer(data)
        new_score.writerow(end_values)

def show_page(file, page):
    """
    The function reads the scoreboard.csv file and splits the list into pages
    Also the function prints the results in a more presentable form.
    """
    os.system('cls')
    first = (page - 1) * 10
    last = page * 10

    with open(file, encoding="utf-8") as data:
        content = data.readlines()
        for elem in range(first, last):
            if elem < no_entry(file):
                line = "".join(content[elem])
                if line.strip() != "":
                    game_no, pl_name, date, time, moves, outcome, left = line.strip().split(",")
                    for value in line:
                        value = value.strip()
                    minute, second = divmod(int(time), 60)
                    time = f'{minute:02}:{second:02}'
                    if outcome == "True":
                        outcome = "WON!"
                    else:
                        outcome = "LOST!"
                    print(f"{game_no}. {pl_name} {outcome}")
                    print(f"Date: {date}, Time: {time}, Moves: {moves}, Unflagged mines: {left}")
                    print()

def scoreboard(file):
    """
    The function allows the user to browse between different pages of scoreboard
    results
    Previous page = "1"
    Next page = "2"
    Back to main menu = "e"
    """
    os.system('cls')
    pages = math.ceil(no_entry(file) / 10)
    current_page = 1
    show_page(file, current_page)

    print(f"Pages: {pages}, current page: {current_page}")
    print()
    print("Previous page      (1)")
    print("Next page          (2)")
    print("Back to main menu  (q)")
    print()
    while True:
        choice = prompt_choice(scoreboard_choices)
        if choice == "1":
            if current_page > 1:
                current_page -= 1
                os.system('cls')
                show_page(file, current_page)
                print(f"Pages: {pages}, current page: {current_page}")
                print()
                print("Previous page      (1)")
                print("Next page          (2)")
                print("Back to main menu  (q)")
                print()
            else:
                print("This is the first page!")
        if choice == "2":
            if current_page < pages:
                current_page += 1
                os.system('cls')
                show_page(file, current_page)
                print(f"Pages: {pages}, current page: {current_page}") 
                print()
                print("Previous page      (1)")
                print("Next page          (2)")
                print("Back to main menu  (q)")
                print()
            else:
                print("This is the last page!")
        if choice == "q":
            os.system('cls')
            main()

def main():
    """
    This function provides the starting Main menu interface
    Defines what each input choice is supposed to do
    New Game = "n"
    Scoreboard = "s"
    Quit = "q"
    """
    os.system('cls')
    print(r" __  __ _             _____")
    print(r"|  \/  (_)           / ____|")
    print(r"| \  / |_ _ __   ___| (_____      _____  ___ _ __   ___ _ __")
    print(r"| |\/| | | '_ \ / _ \\___ \ \ /\ / / _ \/ _ \ '_ \ / _ \ '__|")
    print(r"| |  | | | | | |  __/____) \ V  V /  __/  __/ |_) |  __/ |")
    print(r"|_|  |_|_|_| |_|\___|_____/ \_/\_/ \___|\___| .__/ \___|_|")
    print(r"                                            | |")
    print(r" By Hieu, Niklas, Niranjan                  |_|")
    print()
    print("    New Game   (n)")
    print("    Scoreboard (s)")
    print("    Quit       (q)")
    print()
    while True:
        choice = prompt_choice(game_choices)
        if choice == "q":
            os.system('cls')
            sys.exit()
        if choice == "s":
            scoreboard(scoreboard_location)
        if choice == "n":
            new_game()


if __name__ == "__main__":
    main()
