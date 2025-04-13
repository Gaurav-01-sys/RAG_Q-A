# #1 https://python.langchain.com/v0.1/docs/integrations/llms/bedrock/
# #pip install -U langchain-aws
# #pip install anthropic

import json
import os
from langchain.chains import RetrievalQA, ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_community.llms import Bedrock
from langchain_aws import ChatBedrock
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from botocore.client import Config

# Constants
JSON_FILE = "chat_history.json"
SERVER_ID = "server_1234"
KNOWLEDGE_BASE_ID = "JOLJ0BNXVX"

# Function to save question and response under a common server ID
def save_conversation_to_json(question, response, sources=None):
    # Load existing data if file exists
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # Start fresh if file is empty/corrupted
    else:
        data = {}

    # Ensure the server_id entry exists
    if SERVER_ID not in data:
        data[SERVER_ID] = []

    # Create entry with question, response and optional sources
    entry = {"question": question, "response": response}
    if sources:
        entry["sources"] = sources

    # Append both the question and the response under the server ID
    data[SERVER_ID].append(entry)

    # Save back to JSON
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Function to create a Bedrock LLM connection for chat
def create_chat_llm():
    chat_llm = ChatBedrock(
        credentials_profile_name="default",
        region_name="us-east-1",  # Specify your region here
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        model_kwargs={
            "max_tokens": 300,
            "temperature": 0.1,
            "top_p": 0.9,
            "stop_sequences": ["\n\nHuman:"]
        }
    )
    return chat_llm

# Function to create a Bedrock LLM connection for knowledge retrieval
def create_retrieval_llm():
    retrieval_llm = Bedrock(
        model_id="anthropic.claude-v2:1", 
        model_kwargs={
            "temperature": 0.1, 
            "top_k": 3, 
            "max_tokens_to_sample": 3000
        }
    )
    return retrieval_llm

# Function to create a knowledge base retriever
def create_retriever():
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=KNOWLEDGE_BASE_ID,
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
    )
    return retriever

# Function to create conversation memory
def create_memory():
    llm = create_chat_llm()
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=300)
    return memory

# Create a persistent memory object
memory = create_memory()

# Function to handle conversation with knowledge retrieval
def enhanced_conversation(input_text, use_knowledge_base=True):
    # First, try to get information from the knowledge base if flag is set
    sources = None
    kb_response = None
    
    if use_knowledge_base:
        try:
            retrieval_llm = create_retrieval_llm()
            retriever = create_retriever()
            
            # Create a RetrievalQA chain
            qa = RetrievalQA.from_chain_type(
                llm=retrieval_llm, 
                retriever=retriever, 
                return_source_documents=True
            )
            
            # Get response from knowledge base
            result = qa({"query": input_text})
            kb_response = result["result"]
            
            # Extract sources for reference
            sources = [doc.metadata for doc in result["source_documents"]] if "source_documents" in result else None
            
        except Exception as e:
            print(f"Knowledge base retrieval error: {str(e)}")
            kb_response = None
    
    # Use the regular conversation chain with memory
    chat_llm = create_chat_llm()
    conversation = ConversationChain(llm=chat_llm, memory=memory, verbose=True)
    
    # If we have a KB response, include it in the context
    if kb_response:
        augmented_prompt = f"Question: {input_text}\n\nRelevant information from knowledge base: {kb_response}\n\nPlease provide a complete answer."
        chat_result = conversation.invoke(augmented_prompt)
    else:
        chat_result = conversation.invoke(input_text)
    
    response = chat_result["response"]
    
    # Save conversation with optional sources to JSON
    save_conversation_to_json(input_text, response, sources)
    
    return {
        "response": response,
        "kb_response": kb_response,
        "sources": sources
    }

def test_connections():
    print("Testing chat connection...")
    try:
        llm = create_chat_llm()
        response = llm.invoke("Hello, can you hear me?")
        print("Chat connection successful!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Chat connection failed: {str(e)}")
    
    print("\nTesting knowledge base connection...")
    try:
        retriever = create_retriever()
        retrieval_llm = create_retrieval_llm()
        qa = RetrievalQA.from_chain_type(llm=retrieval_llm, retriever=retriever, return_source_documents=True)
        result = qa({"query": "Test query"})
        print("Knowledge base connection successful!")
        print(f"Response: {result['result'][:100]}...")  # Print first 100 chars
    except Exception as e:
        print(f"Knowledge base connection failed: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Run connection tests
    test_connections()
    
    # # Example conversation with knowledge base augmentation
    # query = "What are the the types of feature engineering?"
    # result = enhanced_conversation(query)
    
    # print("\n--- RESPONSE ---")
    # print(result["response"])
    
    # if result["kb_response"]:
    #     print("\n--- KNOWLEDGE BASE INFO ---")
    #     print(result["kb_response"][:200] + "..." if len(result["kb_response"]) > 200 else result["kb_response"])
    
    # if result["sources"]:
    #     print("\n--- SOURCES ---")
    #     for i, source in enumerate(result["sources"]):
    #         print(f"Source {i+1}: {source}")


