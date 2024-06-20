**Code Explanation**

**Flask App**

**Functions**

1. download_pdf(pdf_url):
Downloads a PDF from a given URL. Raises an exception if the download fails. Returns the PDF content as bytes.

2. extract_text_from_pdf(pdf_content):
Extracts text from the provided PDF content. Uses PyMuPDF (fitz) to read the PDF. Returns the extracted text as a string. Raises an exception if text extraction fails.

3. handle_rag(query, context_text):
Handles a query using Retrieval-Augmented Generation (RAG). Encodes the query and context text using T5 tokenizer. Generates a response using the T5 model. Updates the RAG history with the query and response.
Returns the generated response. Raises an exception if any error occurs during processing.

4. chat_with_ollama(query):
Handles a conversational query using the Ollama chat API. Constructs a message history with system prompt and previous conversation history. Sends the query to the Ollama chat API and gets the response.
Updates the conversation history with the query and response. Returns the response text. Returns an error message if any error occurs during communication with Ollama.

5. speak_text(text):
Uses pyttsx3 to convert text to speech. Speaks the provided text. Prints an error message if text-to-speech conversion fails.

**Routes:**

@app.route("/conversation_query", methods=["POST"]):
Endpoint: /conversation_query
Method: POST
Handles conversational queries.
Extracts the query from the POST request JSON payload.
Uses chat_with_ollama to get the response.
Returns the response as JSON.

@app.route("/querypdf", methods=["POST"]):
Endpoint: /querypdf
Method: POST
Handles queries related to a PDF document.
Extracts the query from the POST request JSON payload.
Downloads and extracts text from a PDF if not already done.
Uses handle_rag to process the query using the extracted text.
Returns the response as JSON.
Returns an error message if any error occurs during processing.

@app.route('/get_messages', methods=['GET']):
Endpoint: /get_messages
Method: GET
Retrieves the conversation history.
Returns the conversation history as JSON.

@app.route('/rag_messages', methods=['GET']):
Endpoint: /rag_messages
Method: GET
Retrieves the RAG history.
Returns the RAG history as JSON.


**Streamlit App**

**Functions**

fetch_messages(endpoint)
Sends a GET request to the Flask server at the specified endpoint. Checks the response status code: If the status code is 200 (OK), it extracts the messages from the JSON response and returns them. If the status code is not 200, it displays an error message using Streamlit's st.error function and returns an empty list. Handles request exceptions and displays an error message if an exception occurs, returning an empty list.

**CLI**

**Functions**

1. update_mode(mode):
Sends a POST request to update the mode to a Flask server running locally. Handles exceptions and prints appropriate messages if the request fails.

2. print_menu():
Prints a menu with options to start a conversation, switch to RAG mode, or exit. Also informs about using audio query and output features.

3. start_conversation():
Initiates a conversation with the LLM (Language Learning Model). Handles user input to switch modes, exit the conversation, or enable audio features.
Calls handle_conversation_input(user_input) to process user queries.

4. start_rag_mode():
Switches to RAG mode. Downloads a PDF file, extracts text from it, and initializes extracted_text. Handles user input to switch modes, exit RAG mode, or enable audio features. Calls handle_rag_input(user_input, extracted_text) to process RAG mode queries.

5. handle_conversation_input(user_input):
Processes user input in conversation mode. Sends a POST request to Flask server (conversation_query endpoint) with user's query.
Updates conversation history and handles audio output if enabled.

6. handle_rag_input(user_input, extracted_text):
Processes user input in RAG mode. Uses handle_rag function from flask_app to handle RAG queries with the extracted text from PDF. Updates RAG history and handles audio output if enabled.

7. handle_audio_query():
Captures audio input using a microphone. Recognizes the speech using Google's speech recognition API. Sends the recognized query to Flask server based on the current mode. Updates conversation or RAG history and handles audio output if enabled.

8. handle_audio_output(response_text):
Initializes text-to-speech engine (pyttsx3) to speak the provided response text. Updates conversation or RAG history based on the current mode.

9. speech_to_text():
Sets up a recognizer to capture audio input. Adjusts for ambient noise and listens to the input.
Uses Google's speech recognition API to recognize and return the spoken query.

10. main():
Entry point of the script. Displays a CLI menu to interact with different functionalities (start conversation, start RAG mode, or exit). Calls respective functions based on user input.

