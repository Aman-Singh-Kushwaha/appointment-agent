
import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Backend URL (assuming it's running locally on port 8000)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/chat") 

st.set_page_config(page_title="TailorTalk", page_icon="💬")
st.title("💬 TailorTalk - Your Appointment Assistant")

# Initialize session state for conversation history and session_id
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I help you today?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send message to backend
    try:
        with st.spinner("Thinking..."):
            response = requests.post(
                BACKEND_URL,
                json={
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                },
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            agent_response = response.json()["response"]

        # Display agent response in chat message container
        with st.chat_message("assistant"):
            st.markdown(agent_response)
        # Add agent response to chat history
        st.session_state.messages.append({"role": "assistant", "content": agent_response})

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend. Please ensure the backend server is running.")
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
