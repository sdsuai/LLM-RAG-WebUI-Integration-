import threading
import ollama
import requests
from flask import Flask, jsonify, request
from transformers import T5ForConditionalGeneration, T5Tokenizer
import fitz  # PyMuPDF
import pyttsx3

app = Flask(__name__)
conversation_history = []
rag_history = []
rag_history_lock = threading.Lock()
system_prompt = "You are an AI assistant. Engage in a friendly and helpful conversation with the user."
system_prompt1 = "You are an AI assistant connected to a RAG. Answer the QUESTION below using the DOCUMENT below as context."
mode = "conversation"

# Initialize T5 model and tokenizer
model = T5ForConditionalGeneration.from_pretrained('t5-small')
tokenizer = T5Tokenizer.from_pretrained('t5-small', legacy=False)

# Global variable to store extracted PDF text
extracted_text = ""

def download_pdf(pdf_url):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download PDF from URL: {str(e)}")

def extract_text_from_pdf(pdf_content):
    try:
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        pdf_document.close()
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def handle_rag(query, context_text):
    global rag_history
    messages = [{'role': 'system', 'content': system_prompt1}]
    messages.extend(rag_history)
    messages.append({'role': 'user', 'content': query})
    
    try:
        # Generate response using T5 based on the retrieved context
        inputs = tokenizer.batch_encode_plus(
            [(f"question: {query} context: {context_text}")],
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )
        outputs = model.generate(inputs['input_ids'], max_length=250)
        
        responses = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        
        # Select the best response based on relevance or other criteria
        best_response = responses[0]  # For simplicity, selecting the first response
        
        print(f"Best response: {best_response}")  # Ensure this gets printed
        app.logger.info(f"Best response: {best_response}")
        
        # Update rag_history with thread-safe access
        with rag_history_lock:
            rag_history.append({'role': 'user', 'content': query})
            rag_history.append({'role': 'assistant', 'content': best_response})
            app.logger.info(f"Updated rag_history: {rag_history}")
            print(f"Updated rag_history: {rag_history}")  
        
        return best_response

    except Exception as e:
        raise Exception(f"Error processing RAG: {str(e)}")

def chat_with_ollama(query):
    global conversation_history
    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(conversation_history)
    messages.append({'role': 'user', 'content': query})
    
    try:
        response = ollama.chat(model='mistral', messages=messages)
        response_text = response['message']['content']
        
        # Update conversation history with thread-safe access
        with rag_history_lock:
            conversation_history.append({'role': 'user', 'content': query})
            conversation_history.append({'role': 'assistant', 'content': response_text})
        
        return response_text
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"

# Function to speak text using text-to-speech engine
tts_engine = pyttsx3.init()

def speak_text(text):
    global tts_engine
    try:
        # Use the initialized engine to speak the provided text
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"Error during text-to-speech: {str(e)}")

@app.route("/conversation_query", methods=["POST"])
def conversation_query():
    data = request.json
    user_input = data.get('query')
    response = chat_with_ollama(user_input)  # Use handle_query for conversation mode

    return jsonify({"response": response})

@app.route("/querypdf", methods=["POST"])
def text_query():
    global extracted_text
    data = request.json
    user_input = data.get('query')
    
    try:
        if not extracted_text:  # Only download and extract if not already done
            pdf_url = 'https://d18rn0p25nwr6d.cloudfront.net/CIK-0001813756/975b3e9b-268e-4798-a9e4-2a9a7c92dc10.pdf'
            # Download PDF content
            pdf_content = download_pdf(pdf_url)
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(pdf_content)
        
        # Handle query using the pre-extracted text
        response = handle_rag(user_input, extracted_text)
        
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": conversation_history})

@app.route('/rag_messages', methods=['GET'])
def get_rag_messages():
    with rag_history_lock:
        app.logger.info(f"Fetching rag messages: {rag_history}")
        print(f"Fetching rag messages: {rag_history}")  # Added print statement for immediate feedback
        return jsonify({"messages": rag_history})


if __name__ == "__main__":
    app.run(debug=True)