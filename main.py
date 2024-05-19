from tkinter import *
from tkinter import messagebox
from random import choice
import pandas as pd
import os
import glob
import sys

# Setting constants
BACKGROUND_COLOR = "#B1DDC6"
LANGUAGE_LABEL_FONT = ("Helvetica", 40, "italic")
TEST_WORD_FONT = ("Helvetica", 60, "bold")

# Determine the base path for data and images
if getattr(sys, 'frozen', False):
    # The application is frozen by PyInstaller
    base_path = sys._MEIPASS
else:
    # The application is not frozen
    base_path = os.path.abspath(".")

# default language
language_to_learn = "French"
words_list = pd.read_csv(os.path.join(base_path, 'data', f'{language_to_learn}_words.csv'))
base_language = "English"


# -------------- CREATING NEW FLASH CARDS -------------------------------------------
def update_words_to_learn():
    global words_to_learn, language_to_learn
    # saves the new words to learn list as csv, overwriting the old one
    words_to_learn.to_csv(os.path.join(base_path, "data", f"{language_to_learn}_words_to_learn.csv"), index=False)


def right_button_clicked():
    global words_to_learn, test_word, language_to_learn

    # Select the rows of the dataframe that don't contain the word
    words_to_learn = words_to_learn[words_to_learn[language_to_learn] != test_word]
    update_words_to_learn()

    # moves on to next word, using the new words_to_learn
    pick_random_word_translation()
    print(len(words_to_learn))


def pick_random_word_translation():
    global flip_timer, test_word, words_to_learn, language_to_learn

    # Every time the right button is clicked, timer restarts and front card is shown
    window.after_cancel(flip_timer)
    canvas.itemconfig(canvas_image, image=front_card)

    # check to see if all words have been learnt
    if len(words_to_learn) > 0:
        # pick a random integer location in the range of number of rows
        random_index = choice(range(0, len(words_to_learn)))
        test_word = words_to_learn.iloc[random_index][language_to_learn]

        card_title_text = language_to_learn

        # update the words on the flash card
        canvas.itemconfig(card_title, text=card_title_text, fill="black")
        canvas.itemconfig(card_word, text=test_word, fill="black")

        # start the 3 second timer until the card is turned around
        flip_timer = window.after(3000, flip_the_card, random_index)
    else:
        messagebox.showinfo(title="There is no more words to learn",
                            message="Congratulations! You've reviewed all the words!\nThe flash cards are reset.")
        # words to learn is removed, progress starts over
        words_to_learn = words_list


def flip_the_card(random_index):
    global base_language, words_to_learn
    canvas.itemconfig(canvas_image, image=back_card)

    word_translation = words_to_learn.iloc[random_index][base_language]
    card_title_text = base_language

    # update the words on the flash card
    canvas.itemconfig(card_title, text=card_title_text, fill="white")
    canvas.itemconfig(card_word, text=word_translation, fill="white")


# -------------- LOADING WORD LIST -------------------------------------------

# check which languages are available
def check_language_lists():
    list_location = os.path.join(base_path, "data")

    # Set the pattern to match the CSV files
    pattern = os.path.join(list_location, "*_words.csv")

    # Use glob to find files matching the pattern
    csv_files = glob.glob(pattern)

    # Extract the language part from each file name
    options = [os.path.basename(f).split('_')[0] for f in csv_files]

    return options


def select_language(*args):
    global base_language, language_to_learn, words_list

    language_to_learn = selected_option.get()

    # Path to the CSV file
    csv_file_path = os.path.join(base_path, 'data', f'{language_to_learn}_words.csv')

    words_list = pd.read_csv(csv_file_path)

    # Extract the language to be learnt and the base language, depends on column order
    base_language = words_list.columns[1]
    language_to_learn = words_list.columns[0]

    check_progress()
    pick_random_word_translation()


def check_progress():
    global words_to_learn, language_to_learn
    try:
        words_to_learn = pd.read_csv(os.path.join(base_path, "data", f"{language_to_learn}_words_to_learn.csv"))
    except FileNotFoundError:  # words to learn list not yet created
        # No words learnt yet, therefore entire list to learn
        words_to_learn = words_list
        update_words_to_learn()

test_word = ""

# -------------- USER INTERFACE -------------------------------------------

# Initialize window
window = Tk()
window.title("Flash card learning")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

flip_timer = window.after(3000, lambda: flip_the_card(choice(range(0, len(words_list)))))

# Canvas of logo
canvas = Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)

# Photo Image creation to convert file for the canvas
front_card = PhotoImage(file=os.path.join(base_path, "images", "card_front.png"))
back_card = PhotoImage(file=os.path.join(base_path, "images", "card_back.png"))

# Placing the image onto the canvas
canvas_image = canvas.create_image(400, 263, image=front_card)
canvas.grid(column=1, row=1, columnspan=2)
# Creating text on canvas
card_title = canvas.create_text(400, 150, text="", font=LANGUAGE_LABEL_FONT)
card_word = canvas.create_text(400, 263, text="", font=TEST_WORD_FONT)

# Dropdown menu of which language to learn
languages = check_language_lists()
# Create a StringVar to hold the selected value
selected_option = StringVar()
selected_option.set(languages[1])  # Set the default value
# Create the OptionMenu widget
dropdown = OptionMenu(window, selected_option, *languages)
dropdown.config(bd=0, highlightthickness=0)
dropdown.grid(column=0, row=0)

# Trace the selected_option variable to detect changes
selected_option.trace("w", select_language)

# Wrong button
wrong_button_image = PhotoImage(file=os.path.join(base_path, "images", "wrong.png"))
wrong_button = Button(image=wrong_button_image, highlightthickness=0, bd=0, command=pick_random_word_translation)
wrong_button.grid(column=1, row=2)

# Right button
right_button_image = PhotoImage(file=os.path.join(base_path, "images", "right.png"))
right_button = Button(image=right_button_image, highlightthickness=0, bd=0, command=right_button_clicked)
right_button.grid(column=2, row=2)

# Pick random card when UI is loaded
check_progress()
pick_random_word_translation()

# Keep window open
window.mainloop()
