from typing import TypedDict, List
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END


# Load .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ API key nahi mili")


# LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=api_key
)


# State
class ChatState(TypedDict):
    messages: List


# Node
def chatbot_node(state: ChatState):

    response = llm.invoke(state["messages"])

    return {
        "messages": state["messages"] + [response]
    }


# Graph
graph = StateGraph(ChatState)

graph.add_node("chatbot", chatbot_node)

graph.set_entry_point("chatbot")

graph.add_edge("chatbot", END)

app = graph.compile()