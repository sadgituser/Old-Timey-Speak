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

# AI Initialiser
API_Key = ""
API_Key_Submitted = False
AI_Provider = ""
AI_Model = ""
AI_Full = ""


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
entry_background_colour = "#2A1808"
entry_foreground_colour = "#F5EDE3"

# Paths
bg_music_path = resource_path("oldtimebackground.mp3").replace(os.sep, '/')

# Initialise 'root' Window
root = tk.Tk()
root.title("Old Timey Speak")
root.geometry("800x600+100+100")
root.resizable(False, False)
root.configure(bg=background_colour, takefocus=True)


# Fonts
titleFont = font.Font(family="Georgia", size=28, underline=True, weight="bold")
textFont = font.Font(family="Georgia", size=16)
buttonFont = font.Font(family="Georgia", size=18, underline=True, weight="bold")
smallButtonFont = font.Font(family="Georgia", size=15, underline=True, weight="bold")


# Labelss
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
descLabel.pack(anchor="center", pady=10)

# Scrolled Text (Conversation Widgets)
textContainer = tk.Frame(root, bg=background_colour)
textContainer.pack(fill=tk.BOTH, padx=20, pady=15)
textContainer.columnconfigure(0, weight=1)
textContainer.columnconfigure(1, weight=1)
textContainer.rowconfigure(0, weight=1)


userField = scrolledtext.ScrolledText(textContainer,
    wrap=tk.WORD,
    height=12,
    font=textFont,
    bg=entry_background_colour,
    fg=entry_foreground_colour,
    insertbackground="#F5BA4B",
    selectbackground="#A76727"
)
userField.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

AIField = scrolledtext.ScrolledText(textContainer,
    wrap=tk.WORD,
    height=12,
    font=textFont,
    bg=entry_background_colour,
    fg=entry_foreground_colour,
    insertbackground="#F5BA4B",
    selectbackground="#A76727",
    state=tk.DISABLED
)
AIField.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

AIField.insert(tk.END, "Holla ordinary!")
userText = userField.get("1.0", tk.END)

# Buttons (Conversation Widgets)
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

# AI Settings Popup
def open_AI_settings_popup():
    global API_Key
    global API_Key_Submitted
    global AI_Provider
    global AI_Model
    global AI_Full

    # Initialse Settings Popup
    AISettingsPopup = tk.Toplevel(root)
    AISettingsPopup.title("Settings")
    AISettingsPopup.geometry("800x600+950+100")
    AISettingsPopup.resizable(False, False)
    AISettingsPopup.transient(root)
    AISettingsPopup.configure(bg=background_colour, takefocus=True)

    # AI Settings Widgets
    settingsTitleLabel = tk.Label(AISettingsPopup,
        text="Settings!",
        font=titleFont,
        bg=background_colour,
        fg=foreground_colour,
        wraplength=750,
        justify="center"
    )
    settingsTitleLabel.pack(anchor="center", pady=(15, 10))

    settingsProviderLabel = tk.Label(AISettingsPopup,
        text="Here you can change the AI settings. Ensure that you spell everything correctly!",
        font=textFont,
        bg=background_colour,
        fg=foreground_colour,
        wraplength=750,
        justify="center"
    )
    settingsProviderLabel.pack(anchor="center", pady=(5, 10))

    AIContainer = tk.Frame(AISettingsPopup, bg=background_colour)
    AIContainer.pack(fill=tk.X, padx=20, pady=(0, 15))
    AIContainer.rowconfigure(0, weight=1)
    AIContainer.rowconfigure(1, weight=1)
    AIContainer.columnconfigure(0, weight=1)
    AIContainer.columnconfigure(1, weight=1)

    AIProvider = StringVar(value="openai")
    AIModel = StringVar(value="gpt-4o")


    AIProviderLabel = tk.Label(AIContainer,
        text="Enter the AI Provider Name: (e.g. openai, anthropic, deepseek)",
        font=textFont,
        bg=background_colour,
        fg=foreground_colour,
        wraplength=350
    )
    AIProviderLabel.grid(row=0, column=0, padx=(7, 7), pady=(0, 4))

    AIModelLabel = tk.Label(AIContainer,
        text="Enter the AI Model Name: (e.g. gpt-4o, claude-opus-5.5)",
        font=textFont,
        bg=background_colour,
        fg=foreground_colour,
        wraplength=350
    )
    AIModelLabel.grid(row=0, column=1, padx=(7, 7), pady=(0, 4))

    AIProviderEntry = tk.Entry(AIContainer,
        bg=entry_background_colour,
        fg=entry_foreground_colour,
        font=textFont,
        textvariable=AIProvider,
        width=18, 
        insertbackground=foreground_colour
    )
    AIProviderEntry.grid(row=1, column=0, sticky="ew", padx=(7, 7))

    AIModelEntry = tk.Entry(AIContainer,
        bg=entry_background_colour,
        fg=entry_foreground_colour,
        font=textFont,
        textvariable=AIModel,
        width=18,
        insertbackground=foreground_colour
    )
    AIModelEntry.grid(row=1, column=1, sticky="ew", padx=(7, 7))


    settingsAPIDescLabel = tk.Label(AISettingsPopup,
        text="Here you can submit the Hackclub API Key that you need for the AI to work. The API Key must be from " \
        "(ai.hackclub.com) and only API Keys with Hackclub's format will be permitted!",
        font=textFont,
        bg=background_colour,
        fg=foreground_colour,
        wraplength=750,
        justify="center"
    )
    settingsAPIDescLabel.pack(anchor="center", pady=(5, 10))

    APIVar = StringVar(value="Enter your API Key!")

    APIEntry = tk.Entry(AISettingsPopup,
        bg=entry_background_colour,
        fg=entry_foreground_colour,
        font=textFont,
        textvariable=APIVar,
        width=50,
        insertbackground=foreground_colour
    )
    APIEntry.pack(anchor="center", pady=(5, 10))

    def handle_API_entry():
        global API_Key
        global API_Key_Submitted
        global AI_Provider
        global AI_Model
        global AI_Full

        API_Key = APIEntry.get()
        AI_Provider = AIProviderEntry.get()
        AI_Model = AIModelEntry.get()
        AIProviderEntry.delete("0", "end")
        AIModelEntry.delete("0", "end")
        APIEntry.delete("0", "end")

        AI_Full = f"{AI_Provider.strip().lower()}/{AI_Model.strip().lower()}"

        if not API_Key.startswith("sk-hc-v1-"):
            API_Key_Submitted = False
            messagebox.showerror("Key Rejected", "Your API Key format is not the right Hackclub format ('sk-hc-v1-').")
            return

        try:
            client = OpenAI(base_url="https://ai.hackclub.com/proxy/v1", api_key=API_Key)
            response = client.chat.completions.create(
                model=AI_Full,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            API_Key_Submitted = True
            messagebox.showinfo("API Key Accepted", f"Your AI credentials have been accepted. Connection to {AI_Full} with API Key of {API_Key} is complete! Please continue!")
        except AuthenticationError:
            API_Key_Submitted = False
            messagebox.showerror("API Key Rejected - Authentication Failed", "Your connection to the AI was rejected, please check that your details are correct!")
        except Exception as e:
            API_Key_Submitted = False
            messagebox.showerror("Connection Error", f"Could not connect to the AI. Error: {str(e)}")


    APISubmitButton = tk.Button(AISettingsPopup,
        text="Submit AI Information",
        bg=foreground_colour,
        fg=background_colour,
        activebackground=active_background_colour,
        activeforeground=active_foreground_colour,
        command=handle_API_entry,
        font=smallButtonFont
    )
    APISubmitButton.pack(anchor="center", pady=(5, 10))









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
moreMenu.add_command(label="Open AI Settings Menu", command=open_AI_settings_popup)
moreMenu.add_separator()
moreMenu.add_checkbutton(label="Toggle BG Music", variable=play_music, command=lambda:[toggle_music()])
moreMenu.add_command(label="Test", command=lambda: [print(API_Key)])
moreMenu.add_separator()
moreMenu.add_command(label="Close Program", command=lambda: [root.destroy()])

userField.focus()
root.config(menu=menubar)
open_AI_settings_popup()
root.mainloop()
