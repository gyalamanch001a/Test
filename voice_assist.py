import speech_recognition as sr
import pyttsx3
import os

# Initialize the recognizer and TTS engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen_command():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"Command: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            return ""

def execute_command(command):
    if "search" in command:
        query = command.replace("search", "")
        os.system(f"start chrome https://www.google.com/search?q={query}")
        speak(f"Searching for {query}")
    elif "open" in command:
        app = command.replace("open", "").strip()
        os.system(f"start {app}")
        speak(f"Opening {app}")
    elif "create file" in command:
        filename = command.replace("create file", "").strip()
        with open(filename, 'w') as file:
            file.write("This is a test file.")
        speak(f"File {filename} created.")
    elif "read file" in command:
        filename = command.replace("read file", "").strip()
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                content = file.read()
                speak(f"Content of {filename}: {content}")
        else:
            speak(f"File {filename} does not exist.")
    elif "execute" in command:
        program = command.replace("execute", "").strip()
        os.system(program)
        speak(f"Executing {program}")
    else:
        speak("Sorry, I don't know that command.")

if __name__ == "__main__":
    speak("How can I help you today?")
    while True:
        command = listen_command()
        if command:
            execute_command(command)