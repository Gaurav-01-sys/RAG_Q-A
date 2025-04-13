
import streamlit as st
import json
import os
import sys

# Import your enhanced chatbot backend
# Assuming the integrated code is saved as chatbot_backend.py
sys.path.append(".")  # Ensure the current directory is in the path
import chatbot_backend as chatbot  # Import your enhanced backend

# Constants
JSON_FILE = "chat_history.json"
SERVER_ID = "server_1234"

# Function to load chat history from JSON file
def load_chat_history():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                # Return the last 3 conversations if available
                if SERVER_ID in data and isinstance(data[SERVER_ID], list):
                    # Get all conversation pairs (question/response)
                    all_conversations = data[SERVER_ID]
                    return all_conversations[-6:]  # Get last 6 entries (3 Q&A pairs)
            except json.JSONDecodeError:
                pass
    return []

# Function to save chat history to a JSON file
def save_chat_to_json():
    # Load existing data if file exists
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # Start fresh if file is empty or corrupted
    else:
        data = {}

    # Ensure the server_id entry exists
    if SERVER_ID not in data:
        data[SERVER_ID] = []

    # Append the chat history under the server ID
    data[SERVER_ID] = st.session_state.chat_history

    # Save back to JSON
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Function to convert past history format to session state format
def format_past_history(past_history):
    formatted_history = []
    for entry in past_history:
        if "question" in entry:
            # Add user question
            formatted_history.append({
                "role": "user",
                "text": entry["question"]
            })
            
            # Add assistant response
            formatted_history.append({
                "role": "assistant",
                "text": entry["response"],
                "sources": entry.get("sources", [])
            })
    return formatted_history

# Set Chatbot Title
st.title("Hi, This is Feat Bot")

# Sidebar for configuration
st.sidebar.title("Bot Settings")
use_knowledge_base = st.sidebar.checkbox("Use Knowledge Base", value=True, 
                                        help="Enable to retrieve information from Amazon Knowledge Base")

# Initialize session state
if 'memory' not in st.session_state:
    st.session_state.memory = chatbot.create_memory()  # Initialize memory
    
    # Load past history (at least 3 most recent conversations)
    past_history = load_chat_history()
    st.session_state.chat_history = format_past_history(past_history)
    
    # If history was loaded, update the memory with past conversations
    if past_history:
        for entry in past_history:
            if "question" in entry and "response" in entry:
                # You may want to add this to memory as well
                # This depends on how your memory implementation works
                pass  # Implement if needed
                
# Show history header if there are past conversations
if st.session_state.chat_history:
    st.subheader("Recent Conversations")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])
        
        # Display sources if available
        if message.get("sources") and len(message["sources"]) > 0:
            with st.expander("View Sources"):
                for i, source in enumerate(message["sources"]):
                    st.write(f"Source {i+1}:", source)

# User Input Box
input_text = st.chat_input("Powered by Bedrock and Claude")

if input_text:
    # Display User Message
    with st.chat_message("user"):
        st.markdown(input_text)
    
    # Append User Message to Chat History
    st.session_state.chat_history.append({"role": "user", "text": input_text})
    
    # Call Enhanced Backend for Chat Response
    with st.spinner("Thinking..."):
        result = chatbot.enhanced_conversation(input_text, use_knowledge_base=use_knowledge_base)
    
    chat_response = result["response"]
    sources = result.get("sources")
    
    # Display Assistant Response
    with st.chat_message("assistant"):
        st.markdown(chat_response)
        
        # Display sources if available
        if sources and len(sources) > 0:
            with st.expander("View Sources"):
                for i, source in enumerate(sources):
                    st.write(f"Source {i+1}:", source)
    
    # Append Assistant Response to Chat History with sources
    st.session_state.chat_history.append({
        "role": "assistant", 
        "text": chat_response,
        "sources": sources
    })

    # Save chat history to JSON file
    save_chat_to_json()

# Add a history management section to the sidebar
st.sidebar.subheader("History Management")

# Add a button to test connections
if st.sidebar.button("Test Connections"):
    with st.sidebar:
        with st.spinner("Testing connections..."):
            st.write("Testing connections to Bedrock and Knowledge Base...")
            chatbot.test_connections()
            st.success("Connection test complete!")

# Add a button to clear current chat history
if st.sidebar.button("Clear Current Chat"):
    st.session_state.chat_history = []
    save_chat_to_json()
    st.success("Chat history cleared!")
    st.rerun()

# Add a button to load more history
if st.sidebar.button("Load More History"):
    # Load all history
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if SERVER_ID in data and isinstance(data[SERVER_ID], list):
                    st.session_state.chat_history = format_past_history(data[SERVER_ID])
                    st.success("Full history loaded!")
                    st.rerun()
            except json.JSONDecodeError:
                st.error("Failed to load history file.")
    else:
        st.warning("No history file found.")


