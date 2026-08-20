# ============================================
# 1. Imports
# ============================================

import os
from typing import TypedDict, List

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, END

from langgraph.checkpoint.sqlite import SqliteSaver


# ============================================
# 2. Load .env
# ============================================

# .env file से environment variables load करेंगे
load_dotenv()


# OpenAI API key प्राप्त करें
api_key = os.getenv("OPENAI_API_KEY")


# API key नहीं मिली तो error दें
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY .env file me nahi mili."
    )


# ============================================
# 3. OpenAI Model
# ============================================

# OpenAI chat model initialize करें
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=api_key
)


# ============================================
# 4. LangGraph State
# ============================================

# ChatState हमारी conversation state है
#
# messages में user और AI के messages रहेंगे.
#
# Example:
#
# HumanMessage
# AIMessage
# HumanMessage
# AIMessage

class ChatState(TypedDict):
    messages: List


# ============================================
# 5. Chatbot Node
# ============================================

def chatbot_node(state: ChatState):

    # पूरी conversation OpenAI model को भेजें
    response = llm.invoke(
        state["messages"]
    )

    # पुराने messages + नया AI response
    # वापस state में store करें
    return {
        "messages": state["messages"] + [response]
    }


# ============================================
# 6. Create Graph
# ============================================

# StateGraph create करें
graph = StateGraph(ChatState)


# Chatbot node add करें
graph.add_node(
    "chatbot",
    chatbot_node
)


# Graph की शुरुआत chatbot से होगी
graph.set_entry_point(
    "chatbot"
)


# Chatbot के बाद graph समाप्त होगा
graph.add_edge(
    "chatbot",
    END
)


# ============================================
# 7. SQLite Checkpointer
# ============================================

# Development के लिए SQLite database use कर रहे हैं.
#
# Database file:
#
# checkpoints.db
#
# IMPORTANT:
# हमारे installed version में
# from_conn_string() एक context manager देता है.
#
# इसलिए पहले context manager create करेंगे.

sqlite_context = SqliteSaver.from_conn_string(
    "checkpoints.db"
)


# Context manager के अंदर से actual
# SqliteSaver object प्राप्त करें.
checkpointer = sqlite_context.__enter__()


# ============================================
# 8. Compile Graph
# ============================================

# Graph को SQLite checkpointer के साथ compile करें
app = graph.compile(
    checkpointer=checkpointer
)


# ============================================
# 9. Chat Function
# ============================================

def chat(
    message: str,
    thread_id: str
):
    """
    एक message को specified thread में भेजता है.

    Same thread_id:
        पुरानी conversation continue होगी.

    New thread_id:
        नई conversation शुरू होगी.
    """

    # Thread configuration
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }


    # User message create करें
    human_message = HumanMessage(
        content=message
    )


    # Message graph को भेजें
    result = app.invoke(
        {
            "messages": [
                human_message
            ]
        },
        config=config
    )


    # Last message AI का response है
    return result["messages"][-1].content


# ============================================
# 10. Direct Testing
# ============================================

# यह code तभी चलेगा जब हम:
#
# python chat.py
#
# चलाएँगे.
#
# Streamlit से import करने पर यह section
# automatically execute नहीं होगा.

if __name__ == "__main__":

    # Test conversation का thread ID
    thread_id = "test_chat_1"


    # ----------------------------------------
    # First message
    # ----------------------------------------

    response = chat(
        "Mera naam Rahul hai.",
        thread_id
    )

    print("\nAI:", response)


    # ----------------------------------------
    # Second message
    # ----------------------------------------

    # Same thread_id use कर रहे हैं.
    #
    # इसलिए SQLite से previous state
    # automatically load होगी.

    response = chat(
        "Mera naam kya hai?",
        thread_id
    )

    print("\nAI:", response)