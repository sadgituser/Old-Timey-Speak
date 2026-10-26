import os
import sys
import tkinter as tk
from tkinter import *
from tkinter import font, messagebox, scrolledtext, ttk
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
root.geometry("800x600+100+100")
root.resizable(False, False)
root.configure(bg=background_colour, takefocus=True)


# Fonts
titleFont = font.Font(family="Georgia", size=28, underline=True, weight="bold")
textFont = font.Font(family="Georgia", size=16)
buttonFont = font.Font(family="Georgia", size=18)


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

textContainer = tk.Frame(root, bg=background_colour)
textContainer.pack(fill=tk.BOTH, padx=20, pady=15)
textContainer.columnconfigure(0, weight=1)
textContainer.columnconfigure(1, weight=1)
textContainer.rowconfigure(0, weight=1)


userField = scrolledtext.ScrolledText(textContainer,
    wrap=tk.WORD,
    height=12,
    font=textFont,
    bg="#2A1808",
    fg="#F5EDE3",
    insertbackground="#F5BA4B",
    selectbackground="#A76727"
)
userField.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

AIField = scrolledtext.ScrolledText(textContainer,
    wrap=tk.WORD,
    height=12,
    font=textFont,
    bg="#2A1808",
    fg="#F5EDE3",
    insertbackground="#F5BA4B",
    selectbackground="#A76727",
    state=tk.DISABLED
)
AIField.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

AIField.insert(tk.END, "Hello World!")
userText = userField.get("1.0", tk.END)

def copy_AI_text():
    AIField.update()
    AIText = AIField.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(str(AIText))
    print(repr(AIText))
    root.update()


buttonContainer = tk.Frame(root, bg=background_colour)
buttonContainer.pack(fill=tk.X, padx=20, pady=(0, 15))
buttonContainer.columnconfigure(0, weight=1, uniform="buttons")
buttonContainer.columnconfigure(1, weight=1, uniform="buttons")
buttonContainer.rowconfigure(0, weight=1)

userSubmitButton = Button(buttonContainer,
    text="SUBMIT",
    bg=foreground_colour,
    fg=background_colour,
    activebackground=active_background_colour,
    activeforeground=active_foreground_colour,
    command=None,
    font=buttonFont
)
userSubmitButton.grid(row=0, column=0, sticky="ew", padx=(0, 10))

copyTextButton = Button(buttonContainer,
    text="COPY TEXT",
    bg=foreground_colour,
    fg=background_colour,
    activebackground=active_background_colour,
    activeforeground=active_foreground_colour,
    command=copy_AI_text,
    font=buttonFont
)
copyTextButton.grid(row=0, column=1, sticky="ew", padx=(10, 0))


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
moreMenu.add_command(label="Open Settings Menu", command=None)
moreMenu.add_separator()
moreMenu.add_checkbutton(label="Toggle BG Music", variable=play_music, command=lambda:[toggle_music()])
moreMenu.add_separator()
moreMenu.add_command(label="Close Program", command=lambda: [root.destroy()])

userField.focus()
root.config(menu=menubar)
root.mainloop()
