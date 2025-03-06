import streamlit as st
import random
import time

st.set_page_config(page_title="Simple Chat", page_icon="💬")
st.title("💬 Hult GPT v1.2 — Simple")

# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello CM3CS! How can I assist you today?",
            "Hi, Hultians! Is there anything I can help you with?",
            "What's shakin', Hultian?", 
            "How are you??"
        ]
    )
    # make the respponse seem like typing
    for word in response.split():
        yield word + " "
        time.sleep(0.1)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Say something!"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})