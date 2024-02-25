import random
import tkinter as tk

# Define options and their winning combinations
options = ["Rock", "Paper", "Scissors"]
win_combinations = {
    "Rock": "Scissors",
    "Paper": "Rock",
    "Scissors": "Paper"
}

# Create the main window
window = tk.Tk()
window.title("Rock Paper Scissors")

# Initialize variables
user_choice = None
computer_choice = None
result = None

# Functions for button clicks
def user_rock():
    global user_choice, computer_choice, result
    user_choice = "Rock"
    computer_choice = random.choice(options)
    play_game()

def user_paper():
    global user_choice, computer_choice, result
    user_choice = "Paper"
    computer_choice = random.choice(options)
    play_game()

def user_scissors():
    global user_choice, computer_choice, result
    user_choice = "Scissors"
    computer_choice = random.choice(options)
    play_game()

# Function to evaluate the game
def play_game():
    global result
    if user_choice == computer_choice:
        result = "It's a tie!"
    elif win_combinations[user_choice] == computer_choice:
        result = "You win!"
    else:
        result = "Computer wins!"

    # Display results
    user_label.config(text=f"You chose: {user_choice}")
    computer_label.config(text=f"Computer chose: {computer_choice}")
    result_label.config(text=result)

# Create labels and buttons
user_label = tk.Label(window, text="Choose your weapon:")
user_label.pack()

rock_button = tk.Button(window, text="Rock", command=user_rock)
rock_button.pack()

paper_button = tk.Button(window, text="Paper", command=user_paper)
paper_button.pack()

scissors_button = tk.Button(window, text="Scissors", command=user_scissors)
scissors_button.pack()

computer_label = tk.Label(window, text="")
computer_label.pack()

result_label = tk.Label(window, text="")
result_label.pack()

# Run the main loop
window.mainloop()