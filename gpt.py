import streamlit as st
from openai import OpenAI
import os
import time
import random
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set Streamlit page config
st.set_page_config(page_title="GPT Chat", page_icon="💬")
st.title("💬 Hult GPT v1.3 — ChatGPT Clone")

# Define retry decorator for OpenAI API calls
@retry(
    stop=stop_after_attempt(5),  # Max 5 attempts
    wait=wait_exponential(multiplier=1, min=4, max=60),  # Wait between 4-60 seconds, increasing exponentially
    retry=retry_if_exception_type(Exception),  # Retry on all exceptions
    before_sleep=lambda retry_state: st.info(f"API error occurred. Waiting {retry_state.next_action.sleep} seconds before retrying...")
)
def create_chat_completion(messages, model):
    """Create a chat completion with retry logic"""
    try:
        return client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
    except Exception as e:
        # Check if it's a rate limit error by looking at the string representation
        error_message = str(e).lower()
        if "rate limit" in error_message or "quota" in error_message:
            logger.error(f"Rate limit error: {e}")
            st.error("You've reached the API rate limit. The app will automatically retry after waiting.")
        else:
            logger.error(f"API error: {e}")
            st.error(f"An error occurred: {e}")
        raise  # Re-raise to trigger retry

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Model selector in sidebar
st.sidebar.title("Settings")
selected_model = st.sidebar.selectbox(
    "Choose a model",
    ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo"],
    index=0
)
st.session_state["openai_model"] = selected_model

# API status indicator in sidebar
with st.sidebar.expander("API Status"):
    if st.button("Check API Status"):
        try:
            # Simple API call to check status
            client.models.list()
            st.sidebar.success("✅ API connection successful")
        except Exception as e:
            st.sidebar.error(f"❌ API Error: {str(e)}")

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Use our retry-enabled function
            stream = create_chat_completion(
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                model=st.session_state["openai_model"],
            )
            
            response = st.write_stream(stream)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Failed after multiple retries: {str(e)}")
            st.info("Please try again later or contact support if the issue persists.")