# Conversational AI with AWS Bedrock and LangChain

A Conversational AI system that combines the power of **AWS Bedrock's Claude models** and **LangChain** to deliver contextually aware, knowledge-augmented responses. This project leverages **Retrieval-Augmented Generation (RAG)** to enhance AI conversations using an integrated knowledge base.

---

## 🚀 Project Goal

To create a conversational AI system that uses **Claude 3 Haiku** for natural language interaction and **Claude v2** for knowledge retrieval. The system is designed to:

- Maintain conversation context  
- Retrieve relevant knowledge base content  
- Generate informed, real-time responses  
- Persist conversation history for review and audits  

---

## 🧠 Key Features

### ✅ Conversation Management
Uses `ConversationChain` with memory to maintain context across user interactions.

### ✅ Knowledge Base Integration
Retrieves relevant information using `AmazonKnowledgeBasesRetriever` from an AWS-hosted knowledge base.

### ✅ Response Generation
Enhances AI responses with content retrieved from the knowledge base (when enabled).

### ✅ Persistence
Saves each session's questions, responses, and source documents into a `JSON` file for traceability.

### ✅ Connection Testing
Includes diagnostic tools to validate connectivity with AWS Bedrock services and the knowledge base.

---

## 🔄 Workflow Overview

1. **Input Processing**  
   The user submits a query or statement.

2. **Knowledge Base Retrieval (Optional)**  
   If enabled, the system queries the knowledge base and retrieves relevant metadata.

3. **Response Generation**  
   The conversational model uses historical context and optional KB content to craft a response.

4. **Persistence**  
   The conversation (Q&A + sources) is saved to a JSON file under a unique session ID.

5. **Output Delivery**  
   Returns the AI response along with any retrieved documents/sources.

---

## 🧱 Code Structure

### 🔧 Core Backend Functions

| Function | Description |
|---------|-------------|
| `save_conversation_to_json` | Saves conversations under session/server ID (e.g., `server_1234`). |
| `create_chat_llm` / `create_retrieval_llm` | Initialize Claude models with custom parameters (e.g., `temperature=0.1`). |
| `create_retriever` | Configures vector-based retriever for the AWS Knowledge Base. |
| `enhanced_conversation` | Main RAG logic: retrieves data, generates response, and logs results. |
| `test_connections` | Validates AWS Bedrock and Knowledge Base connectivity. |

### ⚠️ Error Handling

- **Fallback Mode**: If the KB fails, the system uses chat-only mode.
- **Corrupted JSON**: Initializes clean data if `chat_history.json` is unreadable.
- **Connectivity Checks**: `test_connections()` ensures both systems are functional before use.

---

## 🖥️ Streamlit Frontend

Provides a clean, interactive UI for real-time chatbot interactions.

### ✨ Features

- Live chat with AI assistant  
- Toggle KB integration on/off  
- View conversation history with source links  
- Clear or reload chat history  
- Run diagnostic connection tests  

### 🔁 Frontend Workflow

1. **Initialization**
   - Loads previous chat history on startup.
   - Sets up session state and Bedrock memory.

2. **User Interaction**
   - Queries sent to backend via `enhanced_conversation`.
   - Responses displayed with source documents and saved to history.

3. **History Management**
   - Option to clear or extend conversation view.

### 🧩 Frontend Functions

| Function | Description |
|---------|-------------|
| `load_chat_history` | Loads last 3 Q&A pairs from `chat_history.json`. |
| `save_chat_to_json` | Saves current session to history file. |
| `format_past_history` | Formats backend data for Streamlit's chat display. |

### 📚 UI Components

- **Chat Window**: Alternating user/assistant messages with source toggles.  
- **Sidebar**:
  - Enable/disable KB integration  
  - Test Bedrock and KB connections  
  - Manage chat history (clear, load more)  

---

## 📦 Ideal Use Cases

- Demo environments  
- Lightweight knowledge-based assistants  
- Enterprise chatbot prototypes with audit capabilities  

---

## 🔧 Requirements

- Python 3.8+  
- Streamlit  
- AWS SDK (boto3)  
- LangChain  
- Streamlit Chat Components  

---

## ✅ Getting Started

1. Clone the repo  
2. Set up AWS credentials  
3. Run the Streamlit app:

```bash
streamlit run app.py
