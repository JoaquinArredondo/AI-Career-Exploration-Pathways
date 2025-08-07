
import streamlit as st

st.set_page_config(page_title="Ask Oscar the Panther", page_icon="🐾", layout="centered")

# === Styles for UI ===
st.markdown("""
    <style>
        .chat-header {
            background-color: #800000;
            color: white;
            padding: 1rem;
            font-size: 20px;
            font-weight: bold;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-body {
            border: 1px solid #ccc;
            border-top: none;
            padding: 1.5rem;
            background-color: #fff;
            min-height: 200px;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        }
        .chat-footer {
            margin-top: 1rem;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: none;
            border-bottom: 2px solid #800000;
            font-size: 16px;
            outline: none;
        }
        .send-button {
            background-color: transparent;
            border: none;
            font-size: 24px;
            color: #800000;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

# === Chat Interface ===
st.markdown('<div class="chat-header">Ask Oscar the Panther 🌐</div>', unsafe_allow_html=True)

st.markdown("""
<div class="chat-body">
    <div style="display: flex; align-items: flex-start; gap: 10px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/64/Emoji_u1f431.svg" width="30">
        <p style="margin: 0;">
            Hi, my name is <strong>Oscar the Panther</strong>! 🐾<br><br>
            I'm here to help you discover your perfect <strong>major</strong> or <strong>career path</strong> at <strong>Hartnell College</strong> 🎓.<br><br>
            I can chat with you in <strong>English</strong>, <strong>Spanish</strong>, and <strong>Chinese</strong>. 🌎<br><br>
            Ready to find your passion? 💬 Ask me anything!
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# === Chat Input Field ===
st.markdown("""
<div class="chat-footer">
    <input type="text" placeholder="Ask a question..." />
    <button class="send-button">➤</button>
</div>
""", unsafe_allow_html=True)
