import requests
from PyPDF2 import PdfFileReader
from transformers import T5ForConditionalGeneration, T5Tokenizer
import speech_recognition as sr
import pyttsx3  # For text-to-speech
from flask_app import download_pdf, extract_text_from_pdf, handle_rag, speak_text

# Initialize global variables
mode = "conversation"  # Default mode
conversation_history = []  # Conversation history for conversation mode
rag_history = []  # Conversation history for RAG mode

# Load T5 model and tokenizer
model = T5ForConditionalGeneration.from_pretrained('t5-small')
tokenizer = T5Tokenizer.from_pretrained('t5-small')

# Flags to control audio features
use_audio_query = False
use_audio_output = False
def update_mode(mode):
    try:
        response = requests.post('http://localhost:5000/update_mode', json={'mode': mode})
        if response.status_code == 200:
            print(f"Mode updated to {mode}")
        else:
            print(f"Failed to update mode. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error updating mode: {e}")
        
def print_menu():
    print("\nMenu:")
    print("1. Start Conversation with LLM")
    print("2. Start RAG Mode with Hardcoded PDF")
    print("3. Exit")
    print("\n Use audio query and audio output in both modes for audio input and audio output feature")
def start_conversation():
    global mode, use_audio_query, use_audio_output
    print("\nStarting conversation with LLM. Type 'rag' to switch to RAG mode or 'menu' to return to main menu.")
    print("LLM will respond to each message.")

    while True:
        user_input = input("You: ").strip().lower()

        if user_input == "menu":
            return
        elif user_input == "rag":
            mode = "rag"
            start_rag_mode()
            print("\nSwitched back to conversation mode. Type 'rag' to switch to RAG mode or 'menu' to return to main menu.")
        elif user_input == "exit":
            print("Exiting conversation mode.")
            return
        elif user_input == "audio query":
            use_audio_query = True
        elif user_input == "audio output":
            use_audio_output = True
        else:
            # Handle conversation input
            handle_conversation_input(user_input)

def start_rag_mode():
    global mode, use_audio_query, use_audio_output
    mode = "rag"
    print("\nSwitched to RAG mode. Type 'conversation' to switch back to conversation mode or 'menu' to return to main menu.")

    pdf_url = 'https://d18rn0p25nwr6d.cloudfront.net/CIK-0001813756/975b3e9b-268e-4798-a9e4-2a9a7c92dc10.pdf'
    pdf_content = download_pdf(pdf_url)
    extracted_text = extract_text_from_pdf(pdf_content)

    while True:
        user_input = input("Query: ").strip().lower()

        if user_input == "menu":
            return
        elif user_input == "conversation":
            mode = "conversation"
            start_conversation()
            print("\nSwitched back to RAG mode. Type 'conversation' to switch back to conversation mode or 'menu' to return to main menu.")
        elif user_input == "exit":
            print("Exiting RAG mode.")
            return
        elif user_input == "audio query":
            use_audio_query = True
        elif user_input == "audio output":
            use_audio_output = True
        else:
            # Handle RAG mode input
            handle_rag_input(user_input, extracted_text)

def handle_conversation_input(user_input):
    global use_audio_query, use_audio_output

    if use_audio_query:
        handle_audio_query()
        use_audio_query = False  # Reset audio query flag after use

    # Continue with normal conversation handling
    data = {"query": user_input}
    try:
        response = requests.post(f"http://localhost:5000/conversation_query", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Assistant: {result['response']}")
            conversation_history.append({'role': 'user', 'content': user_input})
            conversation_history.append({'role': 'assistant', 'content': result['response']})
            if use_audio_output:
                handle_audio_output(result['response'])
                use_audio_output = False  # Reset audio output flag after use
        else:
            print(f"Failed to fetch response from server. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Flask server: {e}")

def handle_rag_input(user_input, extracted_text):
    global use_audio_query, use_audio_output

    if use_audio_query:
        handle_audio_query()
        use_audio_query = False  # Reset audio query flag after use

    # Continue with normal RAG mode handling
    try:
        response = handle_rag(user_input, extracted_text)
        print(f"Assistant: {response}")
        rag_history.append({'role': 'user', 'content': user_input})
        rag_history.append({'role': 'assistant', 'content': response})
        if use_audio_output:
            handle_audio_output(response)
            use_audio_output = False  # Reset audio output flag after use
    except Exception as e:
        print(f"Error processing RAG query: {str(e)}")

def handle_audio_query():
    global mode
    try:
        # Capture audio input
        query = speech_to_text()

        if query:
            data = {"query": query}
            if mode == "conversation":
                # Send the query to Flask server for conversation mode
                response = requests.post(f"http://localhost:5000/conversation_query", json=data)
            else:
                # Send the query to Flask server for RAG mode
                response = requests.post(f"http://localhost:5000/querypdf", json=data)

            if response.status_code == 200:
                result = response.json()
                print(f"Assistant: {result['response']}")
                speak_text(result['response'])
                if mode == "conversation":
                    conversation_history.append({'role': 'user', 'content': query})
                    conversation_history.append({'role': 'assistant', 'content': result['response']})
                else:
                    rag_history.append({'role': 'user', 'content': query})
                    rag_history.append({'role': 'assistant', 'content': result['response']})
            else:
                print(f"Failed to fetch response from server. Status code: {response.status_code}")
        else:
            print("No audio input detected.")

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Flask server: {e}")

def handle_audio_output(response_text):
    global mode
    try:
        # Initialize text-to-speech engine
        tts_engine = pyttsx3.init()
        tts_engine.say(response_text)
        tts_engine.runAndWait()

        # Update conversation history based on mode
        if mode == "conversation":
            conversation_history.append({'role': 'assistant', 'content': response_text})
        elif mode == "rag":
            rag_history.append({'role': 'assistant', 'content': response_text})

    except Exception as e:
        print(f"Error during text-to-speech: {str(e)}")

def speech_to_text():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio)
        print(f"Recognized: {query}")
        return query
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Error fetching results; {e}")
        return ""
    

HOST = 'localhost'
PORT = 12345

def main():
    global mode
    print("Welcome to the LLM CLI Menu!")

    
    while True:
        print_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            
            start_conversation()
        elif choice == '2':
            
            start_rag_mode()
        elif choice == '3':
            print("Exiting CLI Menu.")
            break
        else:
            print("Invalid choice. Please choose again.")



if __name__ == '__main__':
    main()
