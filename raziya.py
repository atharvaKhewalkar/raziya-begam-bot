import speech_recognition as sr
import re
import json
from datetime import datetime, timedelta

def recognize_speech(prompt="Listening...", timeout=10, phrase_time_limit=15):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(prompt)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return None
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return None

def save_memory(memory):
    with open("memory.json", "w") as f:
        json.dump(memory, f)

def load_memory():
    try:
        with open("memory.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def process_command(command, memory):
    remember_pattern = re.compile(r"remember (?:that )?(.+)")
    recall_patterns = [
        re.compile(r"what is on (\d{1,2} [a-zA-Z]+ \d{4})"),
        re.compile(r"what is (.+)")
    ]

    # Check if the command is to remember something
    remember_match = remember_pattern.search(command.lower())
    if remember_match:
        key_value = remember_match.group(1)
        
        # Handle relative date first
        if ' is ' in key_value:
            key, value = key_value.split(" is ")
            value = parse_date(value.strip())  # Parse the date
            if value:
                memory[key.strip()] = value.strftime("%Y-%m-%d")
                save_memory(memory)  # Save memory after updating
                return f"Got it, I will remember that {key.strip()} is on {value.strftime('%Y-%m-%d')}."
            else:
                return f"Sorry, I didn't understand the date format for '{value}'. Please try again."
        else:
            return "I didn't get that. Please say 'Remember [key] is [value]'."

    # Check if the command is to recall something
    for pattern in recall_patterns:
        match = pattern.search(command.lower())
        if match:
            if len(match.groups()) == 1:
                key = match.group(1).strip()
                if key in memory:
                    return f"{key} is on {memory[key]}."
                else:
                    return f"I don't have any information about {key}."
            elif len(match.groups()) == 2:
                query = match.group(1).strip()
                date = parse_date(query)
                if date:
                    for key, value in memory.items():
                        if value == date.strftime("%Y-%m-%d"):
                            return f"{key} is on {date.strftime('%Y-%m-%d')}."
                    return f"I don't have any specific information about {query}."
                else:
                    return f"Sorry, I didn't understand the date format for '{query}'. Please try again."

    return "I am not sure how to respond to that."

def parse_date(value):
    today = datetime.now().date()
    if value.lower() == "tomorrow":
        return today + timedelta(days=1)
    elif value.lower() == "day after tomorrow":
        return today + timedelta(days=2)
    elif value.lower() == "next week":
        return today + timedelta(days=7)
    else:
        try:
            return datetime.strptime(value, "%d %B %Y").date()
        except ValueError:
            return None

def main():
    memory = load_memory()  # Load memory from file
    assistant_name = "kt"
    greeted = False
    
    while True:
        command = recognize_speech("Listening...", timeout=20, phrase_time_limit=20)
        if command and assistant_name in command.lower():
            if not greeted:
                print("Hello, Atharva! How may I help you?")
                greeted = True
            else:
                print("How can I help you?")
                
            while True:
                command = recognize_speech("I'm listening...", timeout=20, phrase_time_limit=20)
                if command:
                    response = process_command(command, memory)
                    print(response)

if __name__ == "__main__":
    main()
