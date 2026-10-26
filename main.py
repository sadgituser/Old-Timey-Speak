import os
import sys
import tkinter as tk
from tkinter import *
from tkinter import font, messagebox, scrolledtext
from openai import OpenAI, AuthenticationError
from PIL import Image, ImageTk
import webbrowser
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

# Resource Path Initialiser
def resource_path(relative_path: str):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "Assets", relative_path)

# Colours
background_colour = "#3B1A22"
foreground_colour = "#D4AF37"
active_background_colour = "#5C2834"
active_foreground_colour = "#FFE875"

# Paths
bg_music_path = resource_path("oldtimebackground.mp3").replace(os.sep, '/')


root = tk.Tk()
root.title("Old Timey Speak")
root.geometry("800x550+100+100")
root.resizable(False, False)
root.configure(bg=background_colour, takefocus=True)


# Fonts
titleFont = font.Font(family="Georgia", size=28, underline=True, weight="bold")
textFont = font.Font(family="Georgia", size=15)
buttonFont = font.Font(family="Georgia", size=17)


titleLabel = Label(root,
    text="Old Timey Speak / Fusty Timey Speaketh",
    font=titleFont,
    bg=background_colour,
    fg=foreground_colour,
    wraplength=750,
    justify="center"
)
titleLabel.pack(anchor="center", pady=(15, 10))

descLabel = Label(root,
    text="Here you can input your text and an AI will turn the text into words from Shakespeare's era!",
    font=textFont,
    bg=background_colour,
    fg=foreground_colour,
    wraplength=750,
    justify="center"
)
descLabel.pack(pady=10)






play_music = tk.BooleanVar(value=True)
pygame.mixer.init()
try:
    pygame.mixer.music.load(bg_music_path)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
except Exception as e:
    messagebox.showerror("Music Failed to Play", f"Failed to load background music: {e}")

def toggle_music():
    if play_music.get() == True:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def check_music():
    toggle_music()
    root.after(100, check_music)

check_music()

menubar = tk.Menu(root)
moreMenu = Menu(menubar,
    tearoff=0,
    bg=background_colour,
    fg=foreground_colour,
    activebackground=active_background_colour,
    activeforeground=active_foreground_colour
)
menubar.add_cascade(label="More", menu=moreMenu)
moreMenu.add_command(label="Test", command=None)
moreMenu.add_separator()
moreMenu.add_checkbutton(label="Toggle BG Music", variable=play_music, command=lambda:[toggle_music()])
moreMenu.add_separator()
moreMenu.add_command(label="Close Program", command=lambda: [root.destroy()])

root.config(menu=menubar)
root.mainloop()
