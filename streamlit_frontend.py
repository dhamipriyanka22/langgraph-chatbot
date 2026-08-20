import uuid

import streamlit as st

from chatbot import app

from langchain_core.messages import HumanMessage, AIMessage


# ============================================
# 1. Page configuration
# ============================================

st.set_page_config(
    page_title="Chatbot",
    page_icon="🤖"
)


# ============================================
# 2. Page title
# ============================================

st.title("🤖 My ChatGPT Clone")


# ============================================
# 3. Session state initialization
# ============================================

# Current conversation का thread_id
#
# हर conversation का अपना unique thread_id होगा.
#
# Example:
# chat_abc123
# chat_xyz789

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"chat_{uuid.uuid4().hex[:8]}"


# Current screen पर दिखाने वाली messages
if "messages" not in st.session_state:
    st.session_state.messages = []


# Previous conversations की list
#
# अभी development के लिए हम इन्हें
# Streamlit session में रख रहे हैं.
#
# बाद में इन्हें database से dynamically
# निकाल सकते हैं.

if "conversations" not in st.session_state:
    st.session_state.conversations = []


# ============================================
# 4. Sidebar
# ============================================

with st.sidebar:

    st.header("💬 Conversations")


    # ----------------------------------------
    # New Chat button
    # ----------------------------------------

    if st.button(
        "🆕 New Chat",
        use_container_width=True
    ):

        # नया unique thread_id generate करें
        new_thread_id = f"chat_{uuid.uuid4().hex[:8]}"

        st.session_state.thread_id = new_thread_id

        # Current screen की messages clear करें
        st.session_state.messages = []

        # Page को refresh करें
        st.rerun()


    st.divider()


    # ----------------------------------------
    # Previous Conversations
    # ----------------------------------------

    st.subheader("Previous Conversations")


    if not st.session_state.conversations:

        st.caption("No previous conversations")


    else:

        for conversation in st.session_state.conversations:

            thread_id = conversation["thread_id"]
            title = conversation["title"]


            # Conversation select करने के लिए button
            if st.button(
                title,
                key=f"conversation_{thread_id}",
                use_container_width=True
            ):

                # Selected thread को current thread बनाएं
                st.session_state.thread_id = thread_id


                # SQLite से उस thread की latest state निकालें
                state = app.get_state(
                    {
                        "configurable": {
                            "thread_id": thread_id
                        }
                    }
                )


                # अगर state available है
                if state and state.values:

                    # Database से messages load करें
                    st.session_state.messages = (
                        state.values.get("messages", [])
                    )

                else:

                    # अगर कोई messages नहीं हैं
                    st.session_state.messages = []


                st.rerun()


# ============================================
# 5. Show current conversation
# ============================================

for msg in st.session_state.messages:

    # User message
    if isinstance(msg, HumanMessage):

        with st.chat_message("user"):
            st.write(msg.content)


    # AI message
    elif isinstance(msg, AIMessage):

        with st.chat_message("assistant"):
            st.write(msg.content)


# ============================================
# 6. Chat input
# ============================================

user_input = st.chat_input(
    "Type your message..."
)


# ============================================
# 7. Process user message
# ============================================

if user_input:

    # ----------------------------------------
    # Create HumanMessage
    # ----------------------------------------

    human_msg = HumanMessage(
        content=user_input
    )


    # Screen की messages में add करें
    st.session_state.messages.append(
        human_msg
    )


    # ----------------------------------------
    # Show user message immediately
    # ----------------------------------------

    with st.chat_message("user"):
        st.write(user_input)


    # ----------------------------------------
    # Thread configuration
    # ----------------------------------------

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }


    # ----------------------------------------
    # Send message to LangGraph
    # ----------------------------------------

    result = app.invoke(
        {
            "messages": [
                human_msg
            ]
        },
        config=config
    )


    # ----------------------------------------
    # Get AI response
    # ----------------------------------------

    ai_msg = result["messages"][-1]


    # Screen की messages में AI response add करें
    st.session_state.messages.append(
        ai_msg
    )


    # ----------------------------------------
    # Show AI response
    # ----------------------------------------

    with st.chat_message("assistant"):
        st.write(ai_msg.content)


    # ========================================
    # 8. Add conversation to sidebar
    # ========================================

    thread_id = st.session_state.thread_id


    # Check करें कि conversation पहले से
    # sidebar में मौजूद है या नहीं

    existing_conversation = None

    for conversation in st.session_state.conversations:

        if conversation["thread_id"] == thread_id:

            existing_conversation = conversation
            break


    # अगर यह नई conversation है
    if existing_conversation is None:

        # पहले user message को title बनाएं
        title = user_input[:30]

        if len(user_input) > 30:
            title += "..."


        st.session_state.conversations.append(
            {
                "thread_id": thread_id,
                "title": title
            }
        )