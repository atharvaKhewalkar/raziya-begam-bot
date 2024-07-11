import speech_recognition as sr

def test_microphone():
    recognizer = sr.Recognizer()
    print("Setting up the microphone...")
    try:
        with sr.Microphone() as source:
            print("Say something!")
            audio = recognizer.listen(source)
            print("Audio captured, processing...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
            except sr.RequestError:
                print("Could not request results; check your network connection.")
    except Exception as e:
        print(f"Error accessing microphone: {e}")

if __name__ == "__main__":
    test_microphone()
