import streamlit as st
from langgraph_backend import chatbot

# Making thread for remembering chat history
CONFIG = {'configurable': {'thread_id': '1'}}

# Create chat input for user query
user_input = st.chat_input("Enter your message:")

# st.session_state is a dictionary-like object that allows you to store and retrieve values across multiple runs of your Streamlit app.
# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
if user_input:

    # Appending user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Displaying user message
    with st.chat_message("user"):
        st.write(user_input)
        
    # Displaying response
    with st.chat_message("assistant"):
        response = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'message': user_input},
                config=CONFIG,
                stream_mode='messages'
            )
        )
    # Appending response to chat history 
    st.session_state.messages.append({"role": "assistant", "content": response})