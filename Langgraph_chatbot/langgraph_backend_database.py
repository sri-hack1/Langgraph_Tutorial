# Importing lib
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages #It's recommended when working with BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage #BaseMessage is somewhat which rep that list can have all type of message
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import sqlite3

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Creating state
class ChatState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]
    
def chat_node(state: ChatState):
    # take user query from state
    message = state['message']
    # Send it to llm
    response = llm.invoke(message)
    # response store to state
    return {"message": [response]}

# Create a SQLite-based saver for persisting chat history
conn = sqlite3.connect('chatbot.db', check_same_thread=False)
# Creating graph
checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(ChatState)

# Creating node
graph.add_node("chat_node", chat_node)

# Graph edge
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# Checkpointer.list() gives all the checkpoints stored in the database
# We can use it to get all the thread ids
# Hence that is a generator, so we have to iterate over it
# and storing in set to avoid duplicate thread ids
def retrive_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        
    return list(all_threads)

