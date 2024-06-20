import streamlit as st
import requests
import time

# Function to fetch messages from Flask server
def fetch_messages(endpoint):
    try:
        response = requests.get(f'http://localhost:5000/{endpoint}')
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            return messages
        else:
            st.error(f"Failed to fetch messages. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching messages: {e}")
        return []

# Streamlit app title
st.title("LLM Interaction")

# Function to display messages with specified role and color
def display_messages(messages, header, user_color, assistant_color):
    if messages:
        st.header(header)
        for message in messages:
            role = message['role']
            content = message['content']
            
            if role == 'user':
                st.markdown(f"<span style='color: {user_color};'>{content}</span>", unsafe_allow_html=True)
            elif role == 'assistant':
                st.markdown(f"<span style='color: {assistant_color};'>{content}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"No {header} available.")

# Fetch and display conversation messages
conversation_messages = fetch_messages('get_messages')
display_messages(conversation_messages, "Conversation Messages:", "blue", "green")

# Fetch and display RAG messages
rag_messages = fetch_messages('rag_messages')
display_messages(rag_messages, "RAG Messages:", "yellow", "red")

# Add a timer to refresh the app every 5 seconds
time.sleep(5)
st.experimental_rerun()
