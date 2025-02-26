# MysticAi-update-0.1

Feature added 
1.Overall gui design improvement
2. Custom button design (toggle, and stop talking bar)
3. Can now open some social platform directly like facebook, linkedin and github (command = open facebook)

Requirements 
Ensure you have the following installed before running MysticAI: 
2.Python 3.7+ 
3.pip (Python package manager) 
4.The required dependencies (listed below)

Installation 
Clone the repository 
1.git clone https://github.com/Naeem-360/mysticai.git 
2.cd mysticai

Install dependencies Run the following command to install the required libraries: 
1.pip install -r requirements.txt 
2.pip install pyttsx3 speechrecognition pywhatkit wikipedia requests beautifulsoup4 noisereduce pyautogui pytz geopy fuzzywuzzy openai dotenv PyQt5

Set up the API key Create a .env file in the project directory and add: 
1.GITHUB_TOKEN=your_openai_api_key_here (Replace your_openai_api_key_here with your actual API key.)

Running MysticAI Run the following command: 
1.python ai_1.py This will launch the GUI for MysticAI.

Usage 
1.Type or speak a command (e.g., "open Chrome", "play a song", "what's the time"). 
2.Use "switch to voice" or "switch to text" to change modes. 
3.Say "help" to see the list of available commands.

Troubleshooting 
1.If you encounter missing dependencies, run pip install -r requirements.txt again. 
2.Ensure your microphone is working for voice commands. 
3.Check if your API key is correctly set in .env.

Contributing Feel free to fork the repository, make improvements, and submit pull requests! 😄

License This project is open-source under the MIT License.
