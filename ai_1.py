import sys
import random
import pyttsx3
import speech_recognition as sr
import pywhatkit
import datetime
import wikipedia
from datetime import date
import webbrowser
import os
import subprocess
import psutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import requests
from bs4 import BeautifulSoup
import noisereduce as nr
import pyautogui
import time
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from fuzzywuzzy import process
import openai
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QPen

load_dotenv()
api_key = os.getenv("GITHUB_TOKEN")
if not api_key:
    print("Error: API key not found. Please check your .env file.")
else:
    print("API key loaded successfully.")

client = openai.OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=api_key,
)

engine = pyttsx3.init(driverName="sapi5")
engine.setProperty("rate", 190)
engine.setProperty("volume", 1.0)
current_mode = "text"
is_speaking = False 

commands_dict = {
    "chrome": ["chrome", "chrom", "crome", "browsr", "google"],
    "notepad": ["notepad", "note", "notepd", "editor"],
    "calculator": ["calculator", "calc", "calcu"],
    "youtube": ["youtube", "yt", "utub", "you tube"],
    "screenshot": ["screenshot", "ss", "screen shot"],
    "shutdown": ["shutdown", "shut down", "exit", "quit"],
}

def get_best_match(user_input):
    best_match, score = process.extractOne(user_input, commands_dict.keys())
    if score > 70:
        return best_match
    return None

def talk(text, gui=None):
    global is_speaking
    print("Assistant:", text)
    if gui:
        gui.update_output(text)
    if current_mode == "voice" and text.strip():
        is_speaking = True
        engine.say(text)
        engine.runAndWait()
        is_speaking = False

def stop_talking():
    global is_speaking
    if is_speaking:
        engine.stop()
        is_speaking = False
        print("Speech stopped.")

class VoiceThread(QThread):
    voice_result = pyqtSignal(str)

    def run(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as mic:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio = recognizer.listen(mic, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                print(f"You (voice): {text}")
                self.voice_result.emit(text)
        except Exception as e:
            print(f"Voice Error: {e}")
            self.voice_result.emit("")

class HoloGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.voice_thread = None
        self.animation_radius = 50  
        self.animation_step = 2    
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50) 

    def initUI(self):
        self.setWindowTitle("Mysticai gui")
        self.setGeometry(200, 200, 800, 600) 
        self.setStyleSheet("background-color: #0a0a0a; border: 1px solid blue;")
        
        layout = QVBoxLayout()

    
        self.title = QLabel("MysticAI", self)
        self.title.setFont(QFont("Arial", 30))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color: white; text-shadow: 0 0 5px blue;")
        layout.addWidget(self.title)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 0.7); border: 2px solid blue;")
        self.output.setFont(QFont("Arial", 16))
        self.output.setMinimumHeight(400) 
        layout.addWidget(self.output)

       
        self.input_field = QLineEdit(self)
        self.input_field.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 0.7); border: 2px solid blue;")
        self.input_field.setFont(QFont("Arial", 14))
        self.input_field.returnPressed.connect(self.process_input)
        layout.addWidget(self.input_field)
        button_layout = QVBoxLayout()  

        
        self.toggle_btn = QPushButton("🎙️", self)  
        self.toggle_btn.setFixedSize(40, 40) 
        self.toggle_btn.setStyleSheet("background-color: transparent; border: 2px solid blue; color: white; font-size: 20px;")
        self.toggle_btn.clicked.connect(self.toggle_mode)
        button_layout.addWidget(self.toggle_btn, alignment=Qt.AlignCenter)

        self.stop_btn = QPushButton("⏹️", self) 
        self.stop_btn.setFixedSize(40, 40) 
        self.stop_btn.setStyleSheet("background-color: transparent; border: 2px solid blue; color: white; font-size: 20px;")
        self.stop_btn.clicked.connect(stop_talking)
        button_layout.addWidget(self.stop_btn, alignment=Qt.AlignCenter)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.flicker_timer = QTimer(self)
        self.flicker_timer.timeout.connect(self.flicker_effect)
        self.flicker_timer.start(500)
        self.update_output(get_greeting())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor(0, 0, 255, 100), 2)  
        painter.setPen(pen)
        center_x = self.width() // 2
        center_y = self.height() // 2 - 50 
        painter.drawEllipse(QRect(center_x - self.animation_radius, center_y - self.animation_radius,
                                  self.animation_radius * 2, self.animation_radius * 2))

        outer_pen = QPen(QColor(0, 0, 255, 50), 1)
        painter.setPen(outer_pen)
        painter.drawEllipse(QRect(center_x - self.animation_radius - 10, center_y - self.animation_radius - 10,
                                  (self.animation_radius + 10) * 2, (self.animation_radius + 10) * 2))

    def update_animation(self):
        self.animation_radius += self.animation_step
        if self.animation_radius >= 70 or self.animation_radius <= 50:
            self.animation_step = -self.animation_step 
        self.update()  

    def flicker_effect(self):
        current_style = self.title.styleSheet()
        if "opacity: 0.8" in current_style:
            self.title.setStyleSheet("color: white; text-shadow: 0 0 5px blue; opacity: 1;")
        else:
            self.title.setStyleSheet("color: white; text-shadow: 0 0 5px blue; opacity: 0.8;")

    def update_output(self, text):
        self.output.append(text)

    def toggle_mode(self):
        global current_mode
        if current_mode == "text":
            current_mode = "voice"
            self.update_output("Switched to voice mode. Listening...")
            talk("Voice mode activated. Say 'switch to text' to change back.", self)
            self.start_voice_input()
        else:
            current_mode = "text"
            self.update_output("Switched to text mode. Type your command.")
            talk("Text mode activated. Type 'switch to voice' to change back.", self)
            self.input_field.setFocus()

    def start_voice_input(self):
        if current_mode == "voice":
            self.voice_thread = VoiceThread(self)
            self.voice_thread.voice_result.connect(self.process_voice_input)
            self.voice_thread.start()

    def process_voice_input(self, text):
        if text:
            self.update_output(f"You (voice): {text}")
            self.process_command(text)
        else:
            talk("", self)
        if current_mode == "voice":
            self.start_voice_input()

    def process_input(self):
        if current_mode == "text":
            command = self.input_field.text().lower().strip()
            self.update_output(f"You: {command}")
            self.input_field.clear()
            self.process_command(command)

    def process_command(self, command):
        if not command:
            return

        if command == "switch to voice":
            self.toggle_mode()
            return
        elif command == "switch to text":
            self.toggle_mode()
            return
        elif command == "quit":
            talk("Shutting down. Have a nice day, sir!", self)
            QApplication.quit()
            return

        if control_pc(command):
            return
        
        if "open messenger" in command:
            open_messenger_in_chrome()
            return
        
        if "open facebook" in command:
            open_facebook_in_chrome()
            return
        if "open linkedin" in command:
            open_linkedin_in_chrome()
            return
        if "open github" in command:
            open_github_in_chrome()
            return


        best_match = get_best_match(command)
        if best_match:
            command = best_match

        print(f"Debug - Recognized Command: {command}")

        if "chat" in command or "talk to jarvis" in command:
            user_prompt = command.replace("chat", "").replace("talk to jarvis", "").strip()
            if not user_prompt:
                talk("What would you like to talk about?", self)
                return
            answer = chat_with_gpt(user_prompt)
            talk(answer, self)

        elif "play" in command:
            song = command.replace("play", "").strip()
            talk("Playing " + song, self)
            pywhatkit.playonyt(song)

        elif "hit the song" in command:
            talk("Playing the song", self)
            pywhatkit.playonyt("https://youtu.be/y-MtHQ-msFk?si=8pA8NEJtwUhAhv1G")

        elif "hit the funny" in command or "funny one" in command:
            talk("Playing the song", self)
            pywhatkit.playonyt("https://youtu.be/Jyeracn7S9I?si=fSggMt9uN83HcqXN")

        elif "hit the hindi" in command or "hindi song" in command:
            talk("Playing the song", self)
            pywhatkit.playonyt("https://youtu.be/eK5gPcFjQps?si=HXpSxqGU7sA5Hsk4")

        elif "hit the phonk" in command:
            talk("Playing the song", self)
            pywhatkit.playonyt("https://youtu.be/ZU3Tj82gya8?si=jqS5BrLZg9mjmNBw")

        elif "my github account" in command or "my github" in command:
            url = f"Your accoutn url"
            webbrowser.open(url)
            talk("Here is your github account", self)

        elif "facebook account" in command or "my facebook account" in command:
            url1 = f"Your accoutn url"
            webbrowser.open(url1)
            talk("Here's your facebook account", self)

        elif "my linkedin" in command or "my linkedin account" in command:
            url2 = f"Your accoutn url"
            webbrowser.open(url2)
            talk("Here is your linkedIn account", self)

        elif "time" in command:
            if "time in" in command:
                location = command.replace("time in", "").strip()
                get_time_in_location(location)
            else:
                get_time_in_location("Bangladesh")

        elif "screenshot" in command or "take screenshot" in command:
            take_screenshot()

        elif "new tab" in command or "another code" in command:
            open_vs_code_new_tab()

        elif "date" in command:
            current_date = date.today()
            talk(str(current_date), self)

        elif "close" in command or "terminate" in command:
            app = command.replace("close", "").replace("terminate", "").strip()
            close_application(app)

        elif "who" in command:
            anything = command.replace("how", "").replace("who", "").replace("what", "").strip()
            try:
                info = wikipedia.summary(anything, sentences=3)
                talk(info, self)
            except Exception as e:
                talk("Sorry, I couldn't fetch that information.", self)

        elif "hello" in command or "hi" in command or "how are you" in command:
            talk("I am fine! How can I help you sir?", self)

        elif "explain" in command:
            topic = command.replace("explain", "").strip()
            try:
                info = wikipedia.summary(topic, sentences=5)
                talk(info, self) 
            except:
                talk("Sorry, I couldn't fetch that information.", self)

        elif "increase volume" in command or "volume up" in command or "increase the volume" in command:
            change_volume(increase=True)

        elif "decrease volume" in command or "volume down" in command:
            change_volume(increase=False)

        elif "google" in command or "search" in command:
            quest = command.replace("google", "").replace("search", "").strip()
            talk(f"Searching {quest}", self)
            search_google(quest)

        elif "open voicemod" in command or "run voice" in command or "voicemod" in command:
            talk("Opening Voicemod", self)
            subprocess.Popen(r"C:\Program Files\Voicemod V3\Voicemod.exe")
        
        elif "open cursor" in command or "open the cursor" in command:
            talk("Opening Cursor", self)
            subprocess.Popen(r"C:\Users\Naeem\AppData\Local\Programs\cursor\Cursor.exe")
        
        elif "open file explorer" in command or "open explorer" in command or "open this pc" in command:
            talk("Opening File Explorer", self)
            os.startfile("explorer")

        elif "telegram" in command:
            talk("Opening Telegram", self)
            subprocess.Popen(r"C:\Users\Naeem\AppData\Roaming\Telegram Desktop\Telegram.exe")

        elif "chrome" in command:
            talk("Opening Chrome", self)
            subprocess.Popen(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

        elif "word" in command or "wordpad" in command:
            talk("Opening WordPad", self)
            os.startfile("write")

        elif "open settings" in command or "pc settings" in command:
            talk("Opening Windows Settings", self)
            subprocess.Popen("start ms-settings:", shell=True)

        elif "dp settings" in command:
            talk("Opening Display Settings", self)
            subprocess.Popen("start ms-settings:display", shell=True)

        elif "cmd" in command:
            talk("Opening CMD", self)
            subprocess.Popen("cmd", shell=True)

        elif "open cap" in command or "run cap" in command or "launch cap" in command:
            talk("Opening Capcut", self)
            subprocess.Popen(r"C:\Users\Naeem\AppData\Local\CapCut\Apps\CapCut.exe --src3")

        elif "store" in command or "microsoft store" in command or "ms store" in command:
            talk("Opening Microsoft Store", self)
            subprocess.Popen("start ms-windows-store:", shell=True)

        elif "open steam" in command or "steam" in command or "run steam" in command:
            talk("Opening Steam", self)
            subprocess.Popen(r"C:\Program Files (x86)\Steam\steam.exe")

        elif "calculator" in command:
            talk("Opening Calculator", self)
            subprocess.Popen("calc", shell=True)
        
        
        elif command == "help":
            show_help()

        else:
            try:
                response = chat_with_gpt(command)
                talk(response, self)
            except:
                talk("I don't understand, please say that again", self)
        
        
def get_greeting():
    hour = int(time.strftime("%H"))
    if hour < 12:
        return "Good Morning Sir!"
    elif hour < 15:
        return "It's Noon Sir! You should rest"
    elif hour < 17:
        return "Good Afternoon Sir!"
    elif hour < 19:
        return "Good Evening Sir!"
    elif hour > 21:
        return "It's late night sir! You should sleep"
    else:
        return "It's Night sir!"
    
def open_linkedin_in_chrome():
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        url = "https://bd.linkedin.com/"
        subprocess.Popen([chrome_path, "--new-window", url])
        talk("Opening LinkedIn in Chrome", gui)
    except Exception as e:
        talk(f"Failed to open LinkedIn: {str(e)}", gui)

def open_github_in_chrome():
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        url = "https://github.com/"
        subprocess.Popen([chrome_path, "--new-window", url])
        talk("Opening GitHub in Chrome", gui)
    except Exception as e:
        talk(f"Failed to open GitHub: {str(e)}", gui)

def open_messenger_in_chrome():
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        url = "https://www.messenger.com"
        subprocess.Popen([chrome_path, "--new-window", url])
        talk("Opening Messenger in Chrome", gui)
    except Exception as e:
        talk(f"Failed to open Messenger: {str(e)}", gui)

def open_facebook_in_chrome():
    try:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        url = "https://www.facebook.com/"
        subprocess.Popen([chrome_path, "--new-window", url])
        talk("Opening Facebook in Chrome", gui)
    except Exception as e:
        talk(f"Failed to open Facebook: {str(e)}", gui)


def get_time_in_location(location="Bangladesh"):
    geolocator = Nominatim(user_agent="geoapi")
    try:
        location_data = geolocator.geocode(location)
        if not location_data:
            talk("Sorry, I couldn't find that location.", gui)
            return
        lat, lon = location_data.latitude, location_data.longitude
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=lon, lat=lat)
        if timezone_str is None:
            talk("Sorry, I couldn't determine the timezone.", gui)
            return
        timezone = pytz.timezone(timezone_str)
        local_time = datetime.datetime.now(timezone).strftime("%I:%M %p")
        talk(f"The current time in {location} is {local_time}", gui)
    except Exception as e:
        talk(f"An error occurred: {e}", gui)

def change_volume(increase=True):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    current_volume = volume.GetMasterVolumeLevelScalar()
    step = 0.1
    if increase:
        new_volume = min(current_volume + step, 1.0)
    else:
        new_volume = max(current_volume - step, 0.0)
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    talk(f"Volume set to {int(new_volume * 100)} percent", gui)

def open_vs_code_new_tab():
    vscode_path = r"E:\VS Code\Microsoft VS Code\Code.exe"
    subprocess.Popen([vscode_path, "--new-window"])
    talk("Opening a new tab in VS Code", gui)

def control_pc(command):
    if "shutdown" in command:
        talk("Shutting down your PC.", gui)
        os.system("shutdown /s /t 5")
        return True
    elif "restart" in command:
        talk("Restarting your PC.", gui)
        os.system("shutdown /r /t 5")
        return True
    elif "open notepad" in command:
        talk("Opening Notepad", gui)
        os.system("notepad")
        return True
    return False

def take_screenshot():
    screenshot_folder = os.path.join(os.getcwd(), "Screenshots")
    os.makedirs(screenshot_folder, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        talk("Screenshot taken and saved successfully", gui)
    except Exception as e:
        talk(f"Error taking screenshot: {e}", gui)

def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    talk(f"Here are the results for {query}", gui)

def search_google_results(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        answer = soup.find("div", class_="BNeawe")
        if not answer:
            answer = soup.find("span", class_="hgKElc")
        talk(answer.text if answer else "No concise answer found.", gui)
    except Exception as e:
        talk("I couldn't fetch the search results.", gui)

def close_application(app_name):
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if app_name.lower() in process.info['name'].lower():
            talk(f"Closing {process.info['name']}", gui)
            os.kill(process.info['pid'], 9)
            return
    talk(f"No running application found with name {app_name}", gui)

def show_help():
    help_text = [
        "Here’s a list of commands I can understand:",
        "1. 'switch to voice' - Switch to voice input mode.",
        "2. 'switch to text' - Switch to text input mode.",
        "3. 'quit' - Exit the assistant.",
        "4. 'time' - Show current time in Bangladesh (or 'time in [location]').",
        "5. 'google [query]' - Search Google.",
        "6. 'play [song name]' - Play a song on YouTube.",
        "7. 'screenshot' - Take and save a screenshot.",
        "8. 'volume up' - Increase system volume.",
        "9. 'volume down' - Decrease system volume.",
        "10. 'explain [topic]' - Get a detailed explanation from Wikipedia.",
        "11. 'chat [topic]' - Talk to me about anything!",
        "12. 'open chrome' - Open Google Chrome.",
        "13. 'shutdown' - Shut down your PC.",
        "14. 'help' - Show this help menu."
    ]
    for line in help_text:
        talk(line, gui)

def chat_with_gpt(prompt):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o-mini",
            temperature=0.6,
            max_tokens=300,
            top_p=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't process that request: {e}"

gui = None

def main():
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 10, 10))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))  
    app.setPalette(palette)

    global gui
    gui = HoloGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
