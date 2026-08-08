import streamlit as st

from chatbot import app

from langchain_core.messages import HumanMessage, AIMessage


st.set_page_config(page_title="Chatbot", page_icon="🤖")

st.title("🤖 My ChatGPT Clone")


# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Show old messages
for msg in st.session_state.messages:

    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)

    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)


# Input
user_input = st.chat_input("Type your message...")


if user_input:

    human_msg = HumanMessage(content=user_input)
    st.session_state.messages.append(human_msg)

    result = app.invoke({
        "messages": st.session_state.messages
    })

    ai_msg = result["messages"][-1]
    st.session_state.messages.append(ai_msg)

    with st.chat_message("assistant"):
        st.write(ai_msg.content)