import os
import sys
import tkinter as tk
from tkinter import *
import json
from tkinter import font, messagebox, scrolledtext, ttk, filedialog
from openai import OpenAI, AuthenticationError
from PIL import Image, ImageTk
import webbrowser
import threading
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


# Config file setup
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(base_dir, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

config_data = load_config()

# AI Initialiser
API_Key = config_data.get("api_key", "")
API_Key_Submitted = bool(API_Key)
AI_Provider = config_data.get("ai_provider", "openai")
AI_Model = config_data.get("ai_model", "gpt-4o")
AI_Full = f"{AI_Provider}/{AI_Model}" if AI_Provider and AI_Model else ""

# What does the AI need to know before answering user queries?
messages_history = [{
    "role": "system",
    "content": (
        "The user will input a sentence in English and you have to translate it into Shakesperean English. Try to "
        "be consistent with the words that you use, for example, if you use the word 'ordinary' for 'earth', try to "
        "use 'ordinary' again if the user asks for a sentence with the word 'earth' in. Do not include any of the "
        "extra fluff that comes with AI prompts, just output the results of the translation with no extra symbols or "
        "characters that are not supposed to be in the translation. This is a 'tool' that the user is using and it is "
        "not supposed to be really serious, so a 1 to 1 word match isn't necessary, as long as the sentence still keeps "
        "its meaning and is written in what Shakesperean text would read like, then all is good. Do not let the user "
        "attempt to talk with you as the AI, if the user does try to do this, then just translate their query into "
        "Shakespeare, as that is the only job in this program that needs to be done!"
    ),
}]


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
bg_music_path = resource_path("oldtimebackgroundmusic.mp3").replace(os.sep, '/')
parchment_icon = resource_path("Parchment.ico").replace(os.sep, '/')
etsy_image_path = resource_path("photo3.png").replace(os.sep, '/')
mail_image_path = resource_path("photo4.png").replace(os.sep, '/')
terra_image_path = resource_path("photo2.png").replace(os.sep, '/')
wikipedia_image_path = resource_path("photo5.png").replace(os.sep, '/')

# Initialise 'root' Window
root = tk.Tk()
root.title("Old Timey Speak")
root.geometry("800x600+100+100")
root.resizable(False, False)
root.configure(bg=background_colour, takefocus=True)

try:
    root.iconbitmap(parchment_icon)
except Exception as e:
    messagebox.showerror("Failed to load icon", f"Failed to load icon: {str(e)}")


# Fonts
titleFont = font.Font(family="Georgia", size=28, underline=True, weight="bold")
textFont = font.Font(family="Georgia", size=16)
rootEntryFont = font.Font(family="Georgia", size=20)
buttonFont = font.Font(family="Georgia", size=18, underline=True, weight="bold")
smallButtonFont = font.Font(family="Georgia", size=15, underline=True, weight="bold")

# Looping Background Image
tile_image = Image.open(resource_path("old-timey-background.png").replace(os.sep, '/'))
tile_width, tile_height = tile_image.size

win_width, win_height = 800, 600

bg_image = Image.new("RGB", (win_width, win_height))
for x in range(0, win_width, tile_width):
    for y in range(0, win_height, tile_height):
        bg_image.paste(tile_image, (x, y))

bg_photo = ImageTk.PhotoImage(bg_image)


# Labels
bg_canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

bg_canvas.create_image(0, 0, image=bg_photo, anchor="nw")

bg_canvas.create_text(
    400, 17,
    text="Old Timey Speak / Olde Time Speaketh",
    font=titleFont,
    fill=foreground_colour,
    width=750,
    justify="center",
    anchor="n"
)

bg_canvas.create_text(
    400, 111,
    text="Here you can input your text and an AI will turn the text into words from Shakespeare's era!",
    font=textFont,
    fill=foreground_colour,
    width=750,
    justify="center",
    anchor="n"
)

# Scrolled Text
textContainer = tk.Frame(bg_canvas, bg=background_colour)
textContainer.columnconfigure(0, weight=1)
textContainer.columnconfigure(1, weight=1)
textContainer.rowconfigure(0, weight=1)


userField = scrolledtext.ScrolledText(textContainer,
    wrap=tk.WORD,
    height=10,
    font=rootEntryFont,
    bg=entry_background_colour,
    fg=entry_foreground_colour,
    insertbackground="#F5BA4B",
    selectbackground="#A76727"
)
userField.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

AIField = scrolledtext.ScrolledText(textContainer,
    wrap=tk.WORD,
    height=10,
    font=rootEntryFont,
    bg=entry_background_colour,
    fg=entry_foreground_colour,
    insertbackground="#F5BA4B",
    selectbackground="#A76727",
    state=tk.DISABLED
)
AIField.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

bg_canvas.create_window(20, 180, window=textContainer, anchor="nw", width=760, height=330)


# Animate 3 dots when thinking
def animate_thinking(dot_count=1):
    current_text = AIField.get("1.0", "1.9")
    if "Thinking" in current_text:
        dots = "." * dot_count
        AIField.config(state=tk.NORMAL)
        AIField.delete("1.0", tk.END)
        AIField.insert(tk.END, f"Thinking{dots}")
        AIField.config(state=tk.DISABLED)
        next_count = (dot_count % 3) + 1
        root.after(400, lambda: animate_thinking(next_count))


# AI Handling
def append_to_chat(text):
    AIField.config(state=tk.NORMAL)
    AIField.delete("1.0", tk.END)
    AIField.insert(tk.END, f"{text}")
    AIField.config(state=tk.DISABLED)
    AIField.see(tk.END)

def fetch_ai_response():
    try:
        client = OpenAI(base_url="https://ai.hackclub.com/proxy/v1",api_key=API_Key)
        response = client.chat.completions.create(
            model=AI_Full, messages=messages_history
        )
        reply = response.choices[0].message.content
        messages_history.append({"role": "assistant", "content": reply})
        root.after(0, lambda: append_to_chat(reply))
    except Exception as e:
        root.after(0, lambda: append_to_chat(f"Failed to interpret text: {str(e)}"))

def send_message(event=None):
    userText = userField.get("1.0", "end-1c").strip()
    if not userText:
        return "break"
    
    append_to_chat("Thinking.")
    animate_thinking(2)

    messages_history.append({"role": "user", "content": userText})
    threading.Thread(target=fetch_ai_response, daemon=True).start()
    return "break"

def export_history():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".md",
        initialfile="Old-Timey-Speak-History.md",
        filetypes=[("Markdown/Text Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")],
        title="Export Translation History"
    )
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                i = 0
                while i < len(messages_history):
                    msg = messages_history[i]
                    if msg.get("role") == "user":
                        user_content = msg.get("content")
                        assistant_content = ""

                        if i + 1 < len(messages_history) and messages_history[i+1].get("role") == "assistant":
                            assistant_content = messages_history[i+1].get("content")

                        f.write(f"**USER:** {user_content}\n")
                        f.write(f"**TRANSLATION:** {assistant_content}\n\n")
                    i += 1
            messagebox.showinfo("Export Successful!", f"History successfully saved to \n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed!", f"Could not save file: {str(e)}")

# Buttons
def copy_AI_text():
    AIField.update()
    AIText = AIField.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(str(AIText))
    root.update()


buttonContainer = tk.Frame(bg_canvas, bg=background_colour)
buttonContainer.columnconfigure(0, weight=1, uniform="buttons")
buttonContainer.columnconfigure(1, weight=1, uniform="buttons")
buttonContainer.rowconfigure(0, weight=1)

userSubmitButton = Button(buttonContainer,
    text="SUBMIT",
    bg=foreground_colour,
    fg=background_colour,
    activebackground=active_background_colour,
    activeforeground=active_foreground_colour,
    command=send_message,
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

bg_canvas.create_window(20, 520, window=buttonContainer, anchor="nw", width=760, height=50)


# AI Settings Popup
def open_AI_settings_popup():
    # Initialise global variables
    global API_Key, API_Key_Submitted, AI_Provider, AI_Model, AI_Full

    # Initialse Settings Popup
    AISettingsPopup = tk.Toplevel(root)
    AISettingsPopup.title("Settings")
    AISettingsPopup.geometry("800x450+950+100")
    AISettingsPopup.resizable(False, False)
    AISettingsPopup.transient(root)

    try:
        AISettingsPopup.iconbitmap(parchment_icon)
    except Exception as e:
        messagebox.showerror("Failed to load icon", f"Failed to load icon: {str(e)}")



    # Initialise Background Image
    settings_bg_image = Image.new("RGB", (800, 450))
    for x in range(0, 800, tile_width):
        for y in range(0, 450, tile_height):
            settings_bg_image.paste(tile_image, (x, y))

    settings_bg_photo = ImageTk.PhotoImage(settings_bg_image)
    AISettingsPopup.bg_photo = settings_bg_photo

    # Canvas with Background Image
    settings_canvas = tk.Canvas(AISettingsPopup, width=800, height=450, highlightthickness=0)
    settings_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    settings_canvas.create_image(0, 0, image=settings_bg_photo, anchor="nw")

    
    # AI Settings Labels, Entries, Buttons and Frames
    settings_canvas.create_text(
        400, 20,
        text="Settings!",
        font=titleFont,
        fill=foreground_colour,
        width=750,
        justify="center",
        anchor="n"
    )

    settings_canvas.create_text(
        400, 75,
        text="Here you can change the AI settings. Ensure that you spell everything correctly! Settings are saved in a config file! ",
        font=textFont,
        fill=foreground_colour,
        width=750,
        justify="center",
        anchor="n"
    )

    AIContainer = tk.Frame(settings_canvas, bg=background_colour)
    AIContainer.rowconfigure(0, weight=1)
    AIContainer.rowconfigure(1, weight=1)
    AIContainer.columnconfigure(0, weight=1)
    AIContainer.columnconfigure(1, weight=1)

    AIProvider = StringVar(value=AI_Provider if AI_Provider else "openai")
    AIModel = StringVar(value=AI_Model if AI_Model else "gpt-4o")

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

    settings_canvas.create_window(20, 140, window=AIContainer, anchor="nw", width=760)

    settingsAPIDescLabel = tk.Label(settings_canvas,
        text="Here you can submit the Hackclub API Key that you need for the AI to work. The API Key must be from " \
        "(ai.hackclub.com) and only API Keys with Hackclub's format will be permitted!",
        font=textFont,
        bg=background_colour,
        fg=foreground_colour,
        wraplength=750,
        justify="center"
    )

    APIVar = StringVar(value=API_Key if API_Key else "Enter your API Key!")

    APIEntry = tk.Entry(settings_canvas,
        bg=entry_background_colour,
        fg=entry_foreground_colour,
        font=textFont,
        textvariable=APIVar,
        width=50,
        insertbackground=foreground_colour
    )

    settings_canvas.create_window(25, 235, window=settingsAPIDescLabel, anchor="nw", width=750)
    settings_canvas.create_window(100, 325, window=APIEntry, anchor="nw")

    # Handling the AI detail entry
    def handle_AI_entry():
        # Initialse global variables
        global API_Key, API_Key_Submitted, AI_Provider, AI_Model, AI_Full

        # Manage entry fields
        API_Key = APIEntry.get()
        AI_Provider = AIProviderEntry.get()
        AI_Model = AIModelEntry.get()


        if API_Key == "" or AI_Provider == "" or AI_Model == "":
            messagebox.showerror("Details Missing", "Please make sure that you fill out all of the boxes!")
        else:
            # Create one variable which has the full AI credentials
            AI_Full = f"{AI_Provider.strip().lower()}/{AI_Model.strip().lower()}"
            AIProviderEntry.delete("0", "end")
            AIModelEntry.delete("0", "end")
            APIEntry.delete("0", "end")

        # Check if the API key starts with the correct format, if not, then reject it
        if not API_Key.startswith("sk-hc-v1-"):
            API_Key_Submitted = False
            messagebox.showerror("Key Rejected", "Your API Key format is not the right Hackclub format ('sk-hc-v1-').")
            return

        # 'Ping' the AI server to see if a connection was established
        try:
            client = OpenAI(base_url="https://ai.hackclub.com/proxy/v1", api_key=API_Key)
            response = client.chat.completions.create(
                model=AI_Full,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            API_Key_Submitted = True

            config_data = {
                "api_key": API_Key,
                "ai_provider": AI_Provider,
                "ai_model": AI_Model
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f)

            messagebox.showinfo("API Key Accepted", f"Your AI credentials have been accepted. Connection to {AI_Full} with API Key of ({API_Key}) is complete! Please continue!")
            AISettingsPopup.destroy()
        except AuthenticationError:
            API_Key_Submitted = False
            messagebox.showerror("API Key Rejected - Authentication Failed", "Your connection to the AI was rejected, please check that your details are correct!")
        except Exception as e:
            API_Key_Submitted = False
            messagebox.showerror("Connection Error", f"Could not connect to the AI. Error: {str(e)}")


    APISubmitButton = tk.Button(settings_canvas,
        text="Submit AI Information",
        bg=foreground_colour,
        fg=background_colour,
        activebackground=active_background_colour,
        activeforeground=active_foreground_colour,
        command=handle_AI_entry,
        font=smallButtonFont
    )
    settings_canvas.create_window(300, 370, window=APISubmitButton, anchor="nw")

# About Me Popup
def open_about_me_popup():
    # Initialise About Me Popup
    aboutMePopupWidth = 700
    aboutMePopupHeight = 500

    aboutMePopup = tk.Toplevel(root)
    aboutMePopup.title("About Me")
    aboutMePopup.geometry(f"{aboutMePopupWidth}x{aboutMePopupHeight}+100+100")
    aboutMePopup.resizable(False, False)

    # Set up canvas and icon
    try:
        aboutMePopup.iconbitmap(parchment_icon)
    except Exception as e:
        messagebox.showerror("Failed to load icon", f"Failed to load icon: {str(e)}")

    about_me_bg_image = Image.new("RGB", (aboutMePopupWidth, aboutMePopupHeight))
    for x in range(0, aboutMePopupWidth, tile_width):
        for y in range(0, aboutMePopupHeight, tile_height):
            about_me_bg_image.paste(tile_image, (x, y))

    about_me_bg_photo = ImageTk.PhotoImage(about_me_bg_image)
    aboutMePopup.bg_photo = about_me_bg_photo

    about_me_canvas = tk.Canvas(aboutMePopup, width=aboutMePopupWidth, height=aboutMePopupHeight, highlightthickness=0)
    about_me_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    about_me_canvas.create_image(0, 0, image=about_me_bg_photo, anchor="nw")

    # About Me Canvas Widgets
    about_me_canvas.create_text(
        aboutMePopupWidth // 2, 20,
        text="About Me (The Dev)!",
        font=titleFont,
        fill=foreground_colour,
        width=(aboutMePopupWidth - 50),
        justify="center",
        anchor="n"
    )

    about_me_canvas.create_text(
        (aboutMePopupWidth // 2), 75,
        text="A little about myself. I am a 15 year old making small projects for fun. " \
        "This project was for the Terra Hackclub (https://terra.hackclub.com) project (which you can find by clicking on the fox below)! " \
        "It is honestly quite fun, and I really enjoy making cool fun things for little fun projects like these. " \
        "My GitHub is at (https://github.com/sadgituser) (TPC UK button below) where you can find many more of my projects! " \
        "Currently there is nowhere that you can support my work, but you can check out my Etsy shop at (https://theprintedcraftuk.etsy.com) (TPC UK button below)! " \
        "You could also email me if you want to contact me by clicking on the mail icon below! Sources information on GitHub README. ",
        font=textFont,
        fill=foreground_colour,
        width=(aboutMePopupWidth - 50),
        justify="center",
        anchor="n"
    )


    buttonY = 425

    etsy_pil_image = Image.open(etsy_image_path)
    etsy_image = ImageTk.PhotoImage(etsy_pil_image)
    about_me_canvas.etsy_image = etsy_image

    def openEtsy():
        webbrowser.open_new("https://theprintedcraftuk.etsy.com")
        webbrowser.open_new_tab("https://github.com/sadgituser")

    etsy_logo_button = tk.Button(aboutMePopup,
        image=etsy_image,
        command=openEtsy,
        padx=10, 
        pady=3
    )
    about_me_canvas.create_window(aboutMePopupWidth // 4, buttonY, window=etsy_logo_button)


    terra_pil_image = Image.open(terra_image_path)
    terra_image = ImageTk.PhotoImage(terra_pil_image)
    about_me_canvas.terra_image = terra_image

    def openTerra():
        webbrowser.open_new("https://terra.hackclub.com")

    terra_button = tk.Button(aboutMePopup,
        image=terra_image,
        command=openTerra,
        padx=10,
        pady=3
    )
    about_me_canvas.create_window(aboutMePopupWidth // 2, buttonY, window=terra_button)


    mail_pil_image = Image.open(mail_image_path)
    mail_image = ImageTk.PhotoImage(mail_pil_image)
    about_me_canvas.mail_image = mail_image

    def openMail():
        webbrowser.open_new("mailto:kavi@mistrypi.dev")

    mail_button = tk.Button(aboutMePopup,
        image=mail_image,
        command=openMail,
        padx=10, 
        pady=3
    )
    about_me_canvas.create_window((aboutMePopupWidth // 4 + aboutMePopupWidth // 2), buttonY, window=mail_button)

# Shakespeare Popup
def open_shakespeare_popup():
    # Initialise Shakespeare Window
    shakespearePopupWidth = 700
    shakespearePopupHeight = 400

    shakespearePopup = tk.Toplevel(root)
    shakespearePopup.title("About Shakespeare")
    shakespearePopup.geometry(f"{shakespearePopupWidth}x{shakespearePopupHeight}+110+110")
    shakespearePopup.resizable(False, False)

    try:
        shakespearePopup.iconbitmap(parchment_icon)
    except Exception as e:
        messagebox.showerror("Failed to load icon", f"Failed to load icon {str(e)}")

    shakespeare_bg_image = Image.new("RGB", (shakespearePopupWidth, shakespearePopupHeight))
    for x in range(0, shakespearePopupWidth, tile_width):
        for y in range(0, shakespearePopupHeight, tile_height):
            shakespeare_bg_image.paste(tile_image, (x, y))

    shakespeare_bg_photo = ImageTk.PhotoImage(shakespeare_bg_image)
    shakespearePopup.bg_photo = shakespeare_bg_photo

    shakespeare_canvas = tk.Canvas(shakespearePopup, width=shakespearePopupWidth, height=shakespearePopupHeight, highlightthickness=0)
    shakespeare_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    shakespeare_canvas.create_image(0, 0, image=shakespeare_bg_photo, anchor="nw")

    # Canvas Widgets
    shakespeare_canvas.create_text(
        shakespearePopupWidth // 2, 20,
        text="About Shakespeare",
        font=titleFont,
        fill=foreground_colour,
        width=(shakespearePopupWidth - 50),
        justify="center",
        anchor="n"
    )

    shakespeare_canvas.create_text(
        shakespearePopupWidth // 2, 75,
        text="William Shakespeare (23 April 1564 - 23 April 1516) was an English Poet, Playwright (play writer) " \
        "and solo actor much regarded as the greatest poet in the English Language! (Source: Wikipedia). Click on the " \
        "Wikipedia link below to learn more about Shakespeare and how he was one of the most revolutionising poets to " \
        "ever grace the English language! Sources information on GitHub README.",
        font=textFont,
        fill=foreground_colour,
        width=(shakespearePopupWidth - 50),
        justify="center",
        anchor="n"
    )

    wikipedia_pil_image = Image.open(wikipedia_image_path)
    wikipedia_image = ImageTk.PhotoImage(wikipedia_pil_image)
    shakespeare_canvas.wikipedia_image = wikipedia_image

    def openWiki():
        webbrowser.open_new("https://en.wikipedia.org/wiki/William_Shakespeare")

    wikipedia_button = tk.Button(shakespearePopup,
        image=wikipedia_image,
        command=openWiki,
        padx=10, 
        pady=3
    )
    shakespeare_canvas.create_window(shakespearePopupWidth // 2, 325, window=wikipedia_button)



# Music Handling
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

# Menu handling
menubar = tk.Menu(root)
moreMenu = Menu(menubar,
    tearoff=0,
    bg=background_colour,
    fg=foreground_colour,
    activebackground=active_background_colour,
    activeforeground=active_foreground_colour
)
menubar.add_cascade(label="More", menu=moreMenu)
moreMenu.add_command(label="Open AI Settings Popup", command=open_AI_settings_popup)
moreMenu.add_command(label="Open About Me Popup", command=open_about_me_popup)
moreMenu.add_command(label="Open About Shakespeare Popup", command=open_shakespeare_popup)
moreMenu.add_separator()
moreMenu.add_command(label="Export History to .txt", command=export_history)
moreMenu.add_separator()
moreMenu.add_checkbutton(label="Toggle BG Music", variable=play_music, command=lambda:[toggle_music()])
moreMenu.add_separator()
moreMenu.add_command(label="Close Program", command=lambda: [root.destroy()])

# Initialise windows
userField.focus()
root.config(menu=menubar)
if not API_Key or not API_Key.startswith("sk-hc-v1"):
    open_AI_settings_popup()
root.mainloop()
