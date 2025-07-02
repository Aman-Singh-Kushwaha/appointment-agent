import streamlit as st
import uuid
from app.agent import get_agent_response


st.set_page_config(page_title="Appointment Agent", page_icon="💬")
st.title("💬 Receptionist Agent - Book appointments easily")

# =====Initiate chat session=====
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ===== Streamlit Chat UI =====
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Check availability or book appointments?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        with st.spinner("Thinking..."):
            agent_response = get_agent_response(prompt, st.session_state.session_id)

        with st.chat_message("assistant"):
            st.markdown(agent_response)
        st.session_state.messages.append({"role": "assistant", "content": agent_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")

# ===== setting in-memory history uppercap =====
st.session_state.messages = st.session_state.messages[-100:]  # Keeps only last 100 messages  
