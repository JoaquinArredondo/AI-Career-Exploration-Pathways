# chatbot.py
import streamlit as st
from logic import generate_response

# --- Page Config ---
st.set_page_config(page_title="Hartnell Career Chatbot", layout="wide")

# --- Branding: Hartnell Header Bar ---
st.markdown(
    """
    <style>
        .header-bar {
            background-color: #48002e;
            padding: 10px 30px;
            color: white;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        .header-bar img {
            max-height: 48px;
            height: auto;
            width: auto;
        }

        .header-bar h1 {
            font-size: 22px;
            font-weight: 600;
            margin: 0;
            flex-grow: 1;
            white-space: normal;
            overflow-wrap: break-word;
        }

        .reset-btn {
            background-color:#fdb913;
            color:#231f20;
            font-size:16px;
            padding:10px 20px;
            border:none;
            border-radius:8px;
            cursor:pointer;
            position: fixed;
            bottom: 20px;
            right: 30px;
            z-index: 1000;
        }
    </style>

    <div class="header-bar">
        <img src="https://www.hartnell.edu/sites/default/files/styles/large/public/Hartnell_Horizontal_Color.png" alt="Hartnell College Logo">
        <h1>Career Exploration Assistant</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Reset Button Fixed to Bottom Right ---
st.markdown(
    """
    <form action="">
        <button class="reset-btn" type="submit">🔄 Start Over</button>
    </form>
    """,
    unsafe_allow_html=True
)
if st.query_params:
    st.session_state.chat = []
    st.experimental_rerun()

# --- Chat Session State ---
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- Display Chat History ---
for entry in st.session_state.chat:
    with st.chat_message(entry["role"]):
        if entry["role"] == "assistant":
            st.markdown(
                f"<div style='background-color:#d0d3d9; padding:10px; border-radius:8px;'>{entry['text']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(entry["text"])

# --- Chat Input (moved up visually by reducing padding) ---
if user_input := st.chat_input("What are you interested in?"):
    st.session_state.chat.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = generate_response(user_input, st.session_state.chat)
    st.session_state.chat.append({"role": "assistant", "text": response})
    with st.chat_message("assistant"):
        st.markdown(
            f"<div style='background-color:#d0d3d9; padding:10px; border-radius:8px;'>{response}</div>",
            unsafe_allow_html=True
        )

# --- Choice Buttons: Only After Prompt ---
if (
    st.session_state.chat
    and st.session_state.chat[-1]["role"] == "assistant"
    and "Would you like to see matching programs now or keep exploring?" in st.session_state.chat[-1]["text"]
):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Keep Exploring"):
            st.session_state.chat.append({"role": "user", "text": "I want to keep exploring."})
            response = generate_response("keep exploring", st.session_state.chat)
            st.session_state.chat.append({"role": "assistant", "text": response})
            st.experimental_rerun()
    with col2:
        if st.button("📚 Show Matching Programs"):
            st.session_state.chat.append({"role": "user", "text": "Show me matching programs."})
            response = generate_response("show programs", st.session_state.chat)
            st.session_state.chat.append({"role": "assistant", "text": response})
            st.experimental_rerun()
