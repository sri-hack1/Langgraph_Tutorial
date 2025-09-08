# Importing lib
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages #It's recommended when working with BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage #BaseMessage is somewhat which rep that list can have all type of message
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

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

# Creating graph
checkpointer = MemorySaver()
graph = StateGraph(ChatState)

# Creating node
graph.add_node("chat_node", chat_node)

# Graph edge
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# We can perfom streaming using below code (Streaming means we can get response in chunks)

# for message_chunk, metadata in chatbot.stream(
#     {"message" : [HumanMessage(content="What is Langgraph")]},
#     config =  {'configurable': {'thread_id': '1'}},
#     stream_mode= 'messages'
#     ):
#     if message_chunk.content:
#         print(message_chunk.content, end='', flush=True)

