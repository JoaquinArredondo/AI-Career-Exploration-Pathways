import streamlit as st
import boto3
import os
import json
import time
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Custom CSS - Dark Red and Yellow Gradient with Font Fix
custom_css = """
<style>
    .stApp {
        background: linear-gradient(-45deg, #8B0000, #AA4A00, #665c00, #8B0000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #f0f0f0;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        font-size: 16px;
    }

    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .stChatMessage {
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 1rem auto;
        font-size: 1rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
        max-width: 900px;
        line-height: 1.6;
        font-family: inherit;
    }

    .stChatMessage[data-testid="user-message"] {
        background: #2a2a2a !important;
        color: #f0f0f0 !important;
    }

    .stChatMessage[data-testid="assistant-message"] {
        background: #3c3c3c !important;
        color: #f0f0f0 !important;
    }

    .stTextInput {
        border-radius: 25px;
        background: #222 !important;
        color: white !important;
        border: 2px solid #444;
        font-family: inherit;
    }

    .stButton>button {
        background: linear-gradient(135deg, #b71c1c, #f57f17);
        color: white;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s ease;
        font-family: inherit;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #f57f17, #b71c1c);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }

    .stTitle {
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
        padding-bottom: 2rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }

    .glass-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        margin: 10px 0;
    }
</style>
"""

# Page config
st.set_page_config(page_title="Hartnell College Advisor", page_icon="🎓", layout="wide")

# Inject CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.title("🎓 Hartnell College Advisor")
    st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

# Memory
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# AWS Bedrock setup
@st.cache_resource
def setup_bedrock():
    try:
        session = boto3.Session(profile_name='Hackathon20')
        client = session.client(
            service_name='bedrock-agent-runtime',
            region_name='us-west-2'
        )
        return client
    except Exception as e:
        st.error(f"Failed to setup Bedrock: {str(e)}")
        return None

bedrock = setup_bedrock()
kb_id = os.getenv('KNOWLEDGE_BASE_ID')
model_id = os.getenv('BEDROCK_MODEL_ID')

# Chat container
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you with your educational journey?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            chat_history = st.session_state.memory.load_memory_variables({})
            history_str = "\n".join(
                f"{msg.type}: {msg.content}"
                for msg in chat_history.get("chat_history", [])
            )

            system_prompt = """You are a helpful Hartnell College advisor. Use the knowledge base to provide accurate information about courses and programs. If you're not sure about something, say so and suggest talking to a human advisor or say exactly what you don't know.

YOUR TASK:

OVERACHING TASKS:
- Ask questions when appropate to engage the student and understand their needs more and mindset, stimulate their brain.
- Do task 2, but keep it still conversational, situationals. 
1. Through natural conversation, gather information about these key parameters:
   - Personality (e.g., introverted/extroverted, analytical/creative)
   - Interests (academic subjects, hobbies, passions)
   - Experience (work history, relevant skills)
   - Desired timeframe for program completion
   - Preferred work environment
   - Leadership aspirations

2. Once you have gathered sufficient information about the student, provide:
   - Suggested career path
   - Relevant Hartnell program(s)
   - Required courses
   - Estimated completion time
   - Local salary information (if available in knowledge base)

FORMATTING RULES:
- Use newlines to separate different topics or points
- Start new sections with a blank line
- When listing items, put each on a new line with a dash (-)
- Format salary information with ($) instead of USD (Example: $75,000 per year)
- Format salary ranges using: from $XX,XXX to $YY,YYY
- Use clear section headers followed by a newline
- Keep paragraphs short and readable
- Use dashes (-) for lists and asterisks (*) for emphasis

CONVERSATION HISTORY:
{history}

USER MESSAGE: {user_message}

Use the conversation history to track what you know about the student. Ask about missing information naturally in conversation. When you have enough information, provide career and program recommendations based on the knowledge base."""

            full_prompt = system_prompt.format(
                history=history_str,
                user_message=prompt
            )

            response = bedrock.retrieve_and_generate(
                input={'text': full_prompt},
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': kb_id,
                        'modelArn': f'arn:aws:bedrock:us-west-2::foundation-model/{model_id}'
                    }
                }
            )
            stream = response['output']['text']

            def clean_text(text):
                import re
                text = text.replace('USD', '$').replace('—', ' to ').replace('toover', 'to over ')
                lines = text.split('\n')
                cleaned_lines = []

                for line in lines:
                    original_line = line.strip()

                    # Fix malformed average/range lines
                    pattern1 = re.search(r'(\d{4,6})\s*average\s*\(\s*range\s*(\d{4,6})[^0-9]+(\d{4,6})', original_line, re.IGNORECASE)
                    if pattern1:
                        avg = int(pattern1.group(1))
                        low = int(pattern1.group(2))
                        high = int(pattern1.group(3))
                        fixed = f"Average salary: ${avg:,} (range: ${low:,}–${high:,})"
                        cleaned_lines.append(fixed)
                        continue

                    # Fix salary ranges like 46000 to 203000
                    pattern2 = re.search(r'(\d{4,6})\s+to\s+(\d{4,6})', original_line)
                    if pattern2 and "salary" in original_line.lower():
                        low = int(pattern2.group(1))
                        high = int(pattern2.group(2))
                        fixed = f"Salary range: from ${low:,} to ${high:,}"
                        cleaned_lines.append(fixed)
                        continue

                    # Fix average salary
                    pattern3 = re.search(r'average\s*[:=]?\s*\$?(\d{4,6})', original_line, re.IGNORECASE)
                    if pattern3:
                        avg = int(pattern3.group(1))
                        fixed = f"Average salary: ${avg:,}"
                        cleaned_lines.append(fixed)
                        continue

                    # Format standalone salaries
                    dollar_nums = re.findall(r'\$?(\d{4,6})', original_line)
                    if dollar_nums and "salary" in original_line.lower():
                        formatted = re.sub(r'\$?(\d{4,6})', lambda m: f"${int(m.group(1)):,}", original_line)
                        cleaned_lines.append(formatted)
                    else:
                        cleaned_lines.append(original_line)

                return '\n'.join(cleaned_lines)

            stream = clean_text(stream)
            message_placeholder = st.empty()
            full_response = ""

            paragraphs = stream.split('\n')
            for paragraph in paragraphs:
                words = paragraph.split()
                for i in range(0, len(words), 3):
                    chunk = " ".join(words[i:i+3])
                    full_response += chunk + " "
                    message_placeholder.write(full_response + "▌")
                    time.sleep(0.05)
                full_response += "\n"
                message_placeholder.write(full_response + "▌")
                time.sleep(0.05)

            message_placeholder.write(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.memory.save_context({"input": prompt}, {"output": full_response})

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.markdown("### Chat Controls")
    if st.button("🗑️ Clear Conversation", key="clear_chat"):
        st.session_state.messages = []
        st.session_state.memory.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### About")
    st.markdown("This AI advisor helps students explore educational and career opportunities at Hartnell College.")
    st.markdown('</div>', unsafe_allow_html=True)
