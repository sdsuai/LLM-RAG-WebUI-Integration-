import streamlit as st
import requests
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

# Fetch conversation messages from server
conversation_messages = fetch_messages('get_messages')

# Display conversation messages
if conversation_messages:
    st.header("Conversation Messages:")
    for message in conversation_messages:
        role = message['role']
        content = message['content']
        if role == 'user':
            st.markdown(f"User: {content}")
        elif role == 'assistant':
            st.markdown(f"Assistant: {content}")
else:
    st.markdown("No conversation messages available.")

# Fetch RAG messages from server
rag_messages = fetch_messages('rag_messages')

# Display RAG messages
if rag_messages:
    st.header("RAG Messages:")
    for message in rag_messages:
        role = message['role']
        content = message['content']
        if role == 'user':
            st.markdown(f"User (RAG): {content}")
        elif role == 'assistant':
            st.markdown(f"Assistant (RAG): {content}")
else:
    st.markdown("No RAG messages available.")
