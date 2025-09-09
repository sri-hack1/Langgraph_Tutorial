import streamlit as st
from langgraph_backend_database import chatbot, retrive_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ***************************** Utility functions *****************************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['messages'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values["message"]   # This is already a list of HumanMessage / AIMessage


    
# ************************ Session State Initialization ************************
# ''' **session_state is a dict 
#     now, {'messages': [
#         {'role': 'user', 'content': 'Hello!'},
#         {{'role': 'assistant', 'content': 'Hey there!!'},}
#     ]}
    
#     So session_state['messages'] is a list of dicts
# '''
if 'messages' not in st.session_state:
    st.session_state['messages'] = []  # Initialize messages if not present

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrive_all_threads()

add_thread(st.session_state['thread_id'])

# ************************************* Sidebar UI **********************************

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()
    
st.sidebar.header("My Conversations")

#   # Display current thread ID

for thread_id in st.session_state['chat_threads'][::-1]:  # Display in reverse order (latest first)
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
    
        temp_message = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_message.append({"role": role, "content": msg.content})

        st.session_state['messages'] = temp_message


# *********************************** Main UI ************************************
# Display chat messages from history on app rerun
for message in st.session_state['messages']:
    # Here message is a dict with keys 'role' and 'content'
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Enter your message:")

if user_input:
    # Making thread for remembering chat history
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    
    # Appending user message to chat history
    st.session_state['messages'].append({"role": "user", "content": user_input})
    
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
