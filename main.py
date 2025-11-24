import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import pyautogui
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox
from threading import Thread
import pywhatkit
import webbrowser
import requests
import re
from bs4 import BeautifulSoup

engine = pyttsx3.init()
engine.setProperty("rate", 175)
voices = engine.getProperty("voices")
if len(voices) > 1:
    try:
        engine.setProperty("voice", voices[1].id)
    except Exception:
        pass

settings = {"language": "en-in", "stay_on": True}


window = tk.Tk()
window.title("020 Assistant")
window.geometry("1100x720")
window.config(bg="#ffffff")

tab_notebook = None
tabs = []  # list of {"frame","entry","output"}

def get_current_tab_index():
    if not tabs:
        return None
    try:
        return tab_notebook.index(tab_notebook.select())
    except Exception:
        return None

def get_current_output_box():
    idx = get_current_tab_index()
    return tabs[idx]["output"] if idx is not None else None

def get_current_entry_box():
    idx = get_current_tab_index()
    return tabs[idx]["entry"] if idx is not None else None

def speak(text, display_prefix="020 Assistant:"):
    try:
        current_output = get_current_output_box()
        if current_output:
            current_output.insert(tk.END, f"{display_prefix} {text}\n\n")
            current_output.see(tk.END)
    except Exception:
        pass
    tts_text = text.replace("020 Assistant", "zero two zero").replace("020", "zero two zero")
    try:
        engine.stop()
        engine.say(tts_text)
        engine.runAndWait()
    except Exception:
        pass

def wish_me():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning. I am 020 Assistant.")
    elif 12 <= hour < 18:
        speak("Good afternoon. I am 020 Assistant.")
    else:
        speak("Good evening. I am 020 Assistant.")
    speak("How can I assist you today?")


def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        recognizer.pause_threshold = 1
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
        except Exception:
            speak("Microphone timed out or couldn't access audio.")
            return "None"
    try:
        query = recognizer.recognize_google(audio, language=settings["language"])
        current_output = get_current_output_box()
        if current_output:
            current_output.insert(tk.END, f"You (Mic): {query}\n\n")
            current_output.see(tk.END)
    except Exception:
        speak("Sorry, I couldn’t catch that. Please say it again.")
        return "None"
    return query.lower()

def process_command(command):
    if not command or command.strip() == "" or command.lower() == "none":
        return
    cmd = command.lower()
    if any(phrase in cmd for phrase in ["who created you", "who made you", "who make you"]):
        speak("I was created by Shivam Paliwal, powered by Professor Tarun.")
        return
    if 'open notepad' in cmd:
        try:
            os.system('notepad.exe')
            speak("Opening Notepad.")
        except Exception:
            speak("Could not open Notepad.")
    elif 'open chrome' in cmd:
        path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        try:
            os.startfile(path)
            speak("Opening Google Chrome.")
        except Exception:
            speak("Could not open Chrome. Please check the path or install Chrome.")
    elif 'play' in cmd:
        song = cmd.replace('play', '').strip()
        if song:
            speak(f"Playing {song} on YouTube.")
            Thread(target=lambda: pywhatkit.playonyt(song)).start()
        else:
            speak("Please say the song name after 'play'.")
    elif 'time' in cmd:
        str_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {str_time}")
    elif 'date' in cmd:
        today = datetime.date.today()
        speak(f"Today's date is {today.strftime('%B %d, %Y')}")
    elif any(k in cmd for k in ['who is', 'what is', 'search','how to calculate']):
        term = cmd.replace('search', '').replace('who is', '').replace('what is', '').replace('how to calculate', '').strip()
        if term:
            Thread(target=lambda: show_search_result(term)).start()
        else:
            speak("Please tell me what to search for.")
    elif 'screenshot' in cmd:
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            speak("Screenshot captured successfully and saved as screenshot.png.")
        except Exception:
            speak("Failed to take a screenshot.")
    elif 'exit' in cmd or 'quit' in cmd:
        speak("Goodbye. zero two zero signing off.")
        try:
            window.destroy()
        except Exception:
            pass
        sys.exit()
    else:
        speak("Sorry, I didn’t understand that command.")
    if not settings["stay_on"]:
        speak("Shutting down as per your settings.")
        try:
            window.destroy()
        except Exception:
            pass
        sys.exit()

def open_link(event, url):
    try:
        webbrowser.open_new_tab(url)
    except Exception:
        speak("Could not open the link in a browser.")

def show_search_result(query):
    query = (query or "").strip()
    if not query:
        speak("Please provide something to search.")
        return
    current_output = get_current_output_box()
    if current_output is None:
        create_new_tab()
        current_output = get_current_output_box()
    try:
        speak(f"Searching for {query}. Please wait.")
        try:
            summary = wikipedia.summary(query, sentences=3)
            page = wikipedia.page(query)
            page_url = page.url
            current_output.insert(tk.END, f"🔍 Wikipedia result for '{query}':\n{summary}\n\n")
            current_output.insert(tk.END, "🔗 Wikipedia Link: ")
            current_output.insert(tk.END, page_url + "\n\n", ("link",))
            current_output.tag_config("link", foreground="#007acc", underline=True)
            current_output.tag_bind("link", "<Button-1>", lambda e, url=page_url: open_link(e, url))
            current_output.see(tk.END)
            speak("According to Wikipedia, " + summary)
        except (wikipedia.DisambiguationError, wikipedia.PageError, Exception):
            google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0"}
            try:
                response = requests.get(google_url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception:
                response = None
                soup = None
            snippet = None
            if soup:
                for tag in soup.find_all(["div", "span"]):
                    cls = tag.get("class")
                    if cls:
                        cls_str = " ".join(cls)
                        if any(name in cls_str for name in ("BNeawe", "hgKElc", "IsZvec", "kno-rdesc")):
                            text = tag.get_text().strip()
                            if len(text.split()) > 6:
                                snippet = text
                                break
            if snippet:
                current_output.insert(tk.END, f"🔎 Google Summary for '{query}':\n{snippet}\n\n")
                current_output.see(tk.END)
                speak("According to Google, " + snippet)
            else:
                current_output.insert(tk.END, f"No direct Google snippet found for '{query}'.\n", "normal")
                current_output.insert(tk.END, "🔗 Open on Google: ")
                current_output.insert(tk.END, google_url + "\n\n", ("link",))
                current_output.tag_config("link", foreground="#007acc", underline=True)
                current_output.tag_bind("link", "<Button-1>", lambda e, url=google_url: open_link(e, url))
                current_output.see(tk.END)
                speak("I couldn't find a direct summary. I placed a Google link in the results.")
        current_output.insert(tk.END, f"🎥 Top YouTube videos for '{query}':\n", "bold")
        current_output.tag_config("bold", foreground="#007acc", font=("Arial", 11, "bold"))
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            response = requests.get(search_url, timeout=10).text
            video_ids = re.findall(r"watch\?v=(\S{11})", response)
        except Exception:
            video_ids = []
        shown = set()
        count = 0
        for vid in video_ids:
            if vid not in shown:
                shown.add(vid)
                count += 1
                video_url = f"https://www.youtube.com/watch?v={vid}"
                current_output.insert(tk.END, f"{count}. {video_url}\n", ("ytlink",))
                current_output.tag_config("ytlink", foreground="#ff3333", underline=True)
                current_output.tag_bind("ytlink", "<Button-1>", lambda e, url=video_url: open_link(e, url))
                if count == 3:
                    break
        if count == 0:
            current_output.insert(tk.END, "No YouTube results found.\n\n")
            speak("No related YouTube videos found.")
        else:
            speak(f"I found {count} YouTube videos related to your query — links are shown in the results.")
        current_output.insert(tk.END, "\n")
        current_output.see(tk.END)
    except requests.RequestException:
        speak("Network error occurred while searching. Please check your connection.")
    except Exception as e:
        speak("Something went wrong while searching.")
        try:
            current_output.insert(tk.END, f"Error: {e}\n\n")
            current_output.see(tk.END)
        except Exception:
            pass

theme_colors = {"White": "#ffffff", "Blue": "#e8f1ff", "Pink": "#ffe8f0", "Skin": "#fbe8d3"}
app_bg_color = tk.StringVar(value="White")
text_color_choices = {"Black":"black","Blue":"#0057e7","Green":"#008744","Red":"#d62d20","Purple":"#673ab7","Gray":"#555555"}
text_color_var = tk.StringVar(value="Black")
result_text_color = tk.StringVar(value="black")

def create_new_tab():
    global tab_notebook
    bg = theme_colors.get(app_bg_color.get(), "#ffffff")
    fg = result_text_color.get()
    tab_frame = tk.Frame(tab_notebook, bg=bg)
    output_box = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, font=("Consolas", 13), bg=bg, fg=fg)
    output_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    frame = tk.Frame(tab_frame, bg=bg)
    frame.pack(fill=tk.X, pady=10)
    entry_box = tk.Entry(frame, font=("Arial", 13), bg="white", fg="black")
    entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
    def mic_action_for_tab():
        q = take_command()
        if q and q.lower() != "none":
            process_command(q)
    mic_button = tk.Button(frame, text="🎤 Mic", font=("Arial", 12, "bold"), bg="#45a29e", fg="white",
                           command=lambda: Thread(target=mic_action_for_tab).start())
    mic_button.pack(side=tk.LEFT, padx=5)
    def go_action_for_tab():
        txt = entry_box.get().strip()
        entry_box.delete(0, tk.END)
        if not txt:
            speak("Please type something first.")
            return
        output_box.insert(tk.END, f"You (Typed): {txt}\n\n")
        output_box.see(tk.END)
        Thread(target=lambda: show_search_result(txt)).start()
    go_button = tk.Button(frame, text="Go 🔍", font=("Arial", 12, "bold"), bg="#007acc", fg="white", command=go_action_for_tab)
    go_button.pack(side=tk.LEFT, padx=5)
    tab_notebook.add(tab_frame, text=f"Chat {len(tabs) + 1}")
    tabs.append({"frame": tab_frame, "entry": entry_box, "output": output_box})
    tab_notebook.select(tab_frame)
    output_box.insert(tk.END, "020 Assistant: New chat tab ready!\n\n")
    output_box.see(tk.END)
    def on_enter(event, entry=entry_box):
        txt = entry.get().strip()
        entry.delete(0, tk.END)
        if not txt:
            speak("Please type something first.")
            return "break"
        current_output = get_current_output_box()
        if current_output:
            current_output.insert(tk.END, f"You (Typed): {txt}\n\n")
            current_output.see(tk.END)
        Thread(target=lambda: show_search_result(txt)).start()
        return "break"
    entry_box.bind("<Return>", on_enter)
    window.bind("<Return>", lambda event: on_enter(event, entry=get_current_entry_box()))

sidebar_button = tk.Button(window, text="⚙️ Settings", bg="#007acc", fg="white",
    font=("Arial", 12, "bold"),
    command=lambda: sidebar_frame.pack_forget() if sidebar_frame.winfo_viewable() else sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5))
sidebar_button.pack(anchor="nw", padx=5, pady=5)

sidebar_frame = tk.Frame(window, bg="#f0f0f0", width=300)
sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

tk.Label(sidebar_frame, text="⚙️ Settings", bg="#f0f0f0", fg="#007acc", font=("Arial", 14, "bold")).pack(pady=8)
tk.Label(sidebar_frame, text="🌐 Default Language:", bg="#f0f0f0", fg="black", font=("Arial", 11)).pack(pady=(6,2))
language_combo = ttk.Combobox(sidebar_frame, values=["en-in", "en-us", "hi-IN", "es-ES"], font=("Arial", 10))
language_combo.set(settings["language"])
language_combo.pack(pady=2, padx=6, fill=tk.X)

stay_on_var = tk.BooleanVar(value=settings["stay_on"])
stay_check = tk.Checkbutton(sidebar_frame, text="Stay On After Tasks", variable=stay_on_var,
    bg="#f0f0f0", fg="black", selectcolor="#ffffff", font=("Arial", 11))
stay_check.pack(pady=8)

def save_settings_action():
    settings["language"] = language_combo.get()
    settings["stay_on"] = stay_on_var.get()
    speak("Settings updated successfully.")

tk.Button(sidebar_frame, text="💾 Save Settings", bg="#007acc", fg="white",
    font=("Arial", 12, "bold"), command=save_settings_action).pack(pady=6)

tk.Label(sidebar_frame, text="📝 Notepad", bg="#f0f0f0", fg="#007acc", font=("Arial", 14, "bold")).pack(pady=(12,6))
notepad_frame = tk.Frame(sidebar_frame, bg="#f0f0f0")
notepad_frame.pack(fill=tk.BOTH, expand=False, padx=6, pady=4)
notepad_tabs = ttk.Notebook(notepad_frame)
notepad_tabs.pack(fill=tk.BOTH, expand=True)
notes = []
def create_note_tab(title="Note", content=""):
    note_tab = tk.Frame(notepad_tabs, bg="#ffffff")
    text_area = scrolledtext.ScrolledText(note_tab, wrap=tk.WORD, width=30, height=8, font=("Consolas", 11), bg="white", fg="black")
    text_area.pack(fill=tk.BOTH, expand=True)
    text_area.insert(tk.END, content)
    notepad_tabs.add(note_tab, text=title)
    notes.append(text_area)
    notepad_tabs.select(note_tab)
def get_current_note():
    try:
        idx = notepad_tabs.index(notepad_tabs.select())
        return notes[idx]
    except Exception:
        return None
def note_save():
    note = get_current_note()
    if note:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(note.get("1.0", tk.END))
            speak("Note saved successfully.")
def note_open():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        create_note_tab(title=os.path.basename(file_path), content=content)
        speak("Opened note in new tab.")
def note_clear():
    note = get_current_note()
    if note:
        note.delete("1.0", tk.END)
        speak("Note cleared.")
def note_new():
    create_note_tab(title=f"Note {len(notes)+1}")
    speak("New note tab created.")
create_note_tab("Note 1")
btn_frame = tk.Frame(sidebar_frame, bg="#f0f0f0")
btn_frame.pack(pady=6)
tk.Button(btn_frame, text="🗂 New", width=6, bg="#007acc", fg="white", font=("Arial", 10, "bold"), command=note_new).grid(row=0, column=0, padx=3)
tk.Button(btn_frame, text="💾 Save", width=6, bg="#007acc", fg="white", font=("Arial", 10, "bold"), command=note_save).grid(row=0, column=1, padx=3)
tk.Button(btn_frame, text="📂 Open", width=6, bg="#45a29e", fg="white", font=("Arial", 10, "bold"), command=note_open).grid(row=0, column=2, padx=3)
tk.Button(btn_frame, text="🧹 Clear", width=6, bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), command=note_clear).grid(row=0, column=3, padx=3)

tk.Label(sidebar_frame, text="🧮 Calculator", bg="#f0f0f0", fg="#007acc", font=("Arial", 14, "bold")).pack(pady=(12,6))
calc_frame = tk.Frame(sidebar_frame, bg="#f0f0f0")
calc_frame.pack(pady=5, padx=6, fill=tk.X)
calc_entry = tk.Entry(calc_frame, width=20, font=("Arial", 12), justify='right', bg="#ffffff", fg="black")
calc_entry.grid(row=0, column=0, columnspan=4, pady=5)
def calc_click(symbol):
    if symbol == "=":
        try:
            expression = calc_entry.get().replace("×", "*").replace("÷", "/")
            result = eval(expression)
            calc_entry.delete(0, tk.END)
            calc_entry.insert(tk.END, str(result))
            speak(f"The result is {result}")
        except Exception:
            calc_entry.delete(0, tk.END)
            calc_entry.insert(tk.END, "Error")
            speak("There is an error in the calculation.")
    elif symbol == "C":
        calc_entry.delete(0, tk.END)
    else:
        calc_entry.insert(tk.END, symbol)
for (text, row, col) in [
    ("7",1,0),("8",1,1),("9",1,2),("÷",1,3),
    ("4",2,0),("5",2,1),("6",2,2),("×",2,3),
    ("1",3,0),("2",3,1),("3",3,2),("-",3,3),
    ("0",4,0),(".",4,1),("C",4,2),("+",4,3),
    ("=",5,0)
]:
    tk.Button(calc_frame,text=text,width=4,height=1,
              bg="#007acc" if text=="=" else "#45a29e",
              fg="white",font=("Arial",11,"bold"),command=lambda t=text: calc_click(t)).grid(
                  row=row,column=col,padx=3,pady=3,
                  columnspan=1 if text!="=" else 4,sticky="nsew")

tk.Label(sidebar_frame, text="🎨 Drawing Notebook", bg="#f0f0f0", fg="#007acc", font=("Arial", 14, "bold")).pack(pady=(12,6))
def open_drawing_notebook():
    draw_window = tk.Toplevel(window)
    draw_window.title("🎨 Drawing Notebook")
    screen_w = window.winfo_screenwidth()
    new_w = int(screen_w * 0.9)
    new_h = int(new_w * 0.9)
    draw_window.geometry(f"{new_w}x{new_h}+30+30")
    draw_window.config(bg="#ffffff")
    canvas = tk.Canvas(draw_window, bg="white", cursor="pencil")
    canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    last = {"x": None, "y": None}
    pen = {"color": "black", "size": 3}
    def start_draw(event):
        last["x"], last["y"] = event.x, event.y
    def draw(event):
        if last["x"] is not None and last["y"] is not None:
            canvas.create_line(last["x"], last["y"], event.x, event.y,
                               fill=pen["color"], width=pen["size"], capstyle=tk.ROUND, smooth=True)
        last["x"], last["y"] = event.x, event.y
    def stop_draw(event):
        last["x"], last["y"] = None, None
    canvas.bind("<Button-1>", start_draw)
    canvas.bind("<B1-Motion>", draw)
    canvas.bind("<ButtonRelease-1>", stop_draw)
    control_frame = tk.Frame(draw_window, bg="#ffffff")
    control_frame.pack(pady=6)
    color_frame = tk.Frame(draw_window, bg="#ffffff")
    color_frame.pack(pady=4)
    tk.Label(color_frame, text="Color:", bg="#ffffff").pack(side=tk.LEFT, padx=(6,4))
    def set_color(c): pen["color"] = c
    for c in ("black", "red", "blue", "green", "orange", "purple"):
        tk.Button(color_frame, bg=c, width=2, command=lambda col=c: set_color(col)).pack(side=tk.LEFT, padx=3)
    tk.Label(color_frame, text="   Brush size:", bg="#ffffff").pack(side=tk.LEFT, padx=(10,2))
    size_var = tk.IntVar(value=3)
    def set_size(): pen["size"] = size_var.get()
    tk.Spinbox(color_frame, from_=1, to=30, width=4, textvariable=size_var, command=set_size).pack(side=tk.LEFT)
    def clear_canvas():
        canvas.delete("all")
        speak("Canvas cleared.")
    def save_drawing():
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if not file_path:
            return
        try:
            ps_path = file_path + ".ps"
            canvas.postscript(file=ps_path, colormode='color')
            try:
                from PIL import Image
                img = Image.open(ps_path)
                img.save(file_path, "png")
                os.remove(ps_path)
                speak("Drawing saved successfully.")
            except Exception:
                speak("Pillow not available or conversion failed. PostScript saved instead.")
                messagebox.showinfo("Saved", f"PostScript saved at:\n{ps_path}\n\nInstall Pillow to save directly as PNG.")
        except Exception:
            speak("Error while saving drawing.")
    def close_drawing():
        speak("Closing drawing notebook.")
        draw_window.destroy()
    tk.Button(control_frame, text="🧹 Clear", bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), command=clear_canvas).pack(side=tk.LEFT, padx=6)
    tk.Button(control_frame, text="💾 Save", bg="#007acc", fg="white", font=("Arial", 11, "bold"), command=save_drawing).pack(side=tk.LEFT, padx=6)
    tk.Button(control_frame, text="❌ Close", bg="#45a29e", fg="white", font=("Arial", 11, "bold"), command=close_drawing).pack(side=tk.LEFT, padx=6)

tk.Button(sidebar_frame, text="🖌️ Open Drawing Notebook", bg="#007acc", fg="white", font=("Arial", 12, "bold"), command=open_drawing_notebook).pack(pady=6)

tk.Label(sidebar_frame, text="🎨 Background Theme:", bg="#f0f0f0", fg="black", font=("Arial", 11, "bold")).pack(pady=(10, 4))
def apply_bg_theme():
    selected = app_bg_color.get()
    color = theme_colors.get(selected, "#ffffff")
    window.config(bg=color)
    main_frame.config(bg=color)
    title_frame.config(bg=color)
    for tab in tabs:
        try:
            tab["frame"].config(bg=color)
            tab["output"].config(bg=color)
        except Exception:
            pass
    speak(f"{selected} theme applied.")
bg_dropdown = ttk.Combobox(sidebar_frame, values=list(theme_colors.keys()), textvariable=app_bg_color, font=("Arial", 10))
bg_dropdown.pack(padx=6, pady=2, fill=tk.X)
tk.Button(sidebar_frame, text="🎨 Apply Theme", bg="#007acc", fg="white", font=("Arial", 11, "bold"), command=apply_bg_theme).pack(pady=(4, 10))

main_frame = tk.Frame(window, bg="#ffffff")
main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
title_frame = tk.Frame(main_frame, bg="#ffffff")
title_frame.pack(fill=tk.X)
title_label = tk.Label(title_frame, text="🤖 020 — PERSONAL AI ASSISTANT", font=("Arial", 20, "bold"), bg="#ffffff", fg="#007acc")
title_label.pack(side=tk.LEFT, pady=10, padx=10)
tab_notebook = ttk.Notebook(main_frame)
tab_notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

new_tab_button = tk.Button(title_frame, text="🗂 New Tab", font=("Arial", 12, "bold"), bg="#007acc", fg="white", command=create_new_tab)
new_tab_button.pack(side=tk.RIGHT, padx=8, pady=8)
tk.Label(title_frame, text="🎨 Text Color:", bg="#ffffff", fg="#007acc", font=("Arial", 11, "bold")).pack(side=tk.RIGHT, padx=(10,4))
def apply_text_color():
    color = text_color_choices.get(text_color_var.get(), "black")
    result_text_color.set(color)
    for tab in tabs:
        try:
            tab["output"].config(fg=color)
        except Exception:
            pass
    speak(f"{text_color_var.get()} color applied to search results.")
color_dropdown = ttk.Combobox(title_frame, values=list(text_color_choices.keys()), textvariable=text_color_var, width=10, font=("Arial", 10))
color_dropdown.pack(side=tk.RIGHT, padx=(4,6), pady=8)
tk.Button(title_frame, text="Apply 🎨", bg="#45a29e", fg="white", font=("Arial", 10, "bold"), command=apply_text_color).pack(side=tk.RIGHT, padx=(4,8), pady=8)

create_new_tab()
window.update_idletasks()
window.minsize(1000,700)
Thread(target=wish_me).start()
window.mainloop()
