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

# Setup
st.set_page_config(page_title="Hartnell College Advisor", page_icon="🎓")
st.title("Hartnell College Advisor")

# Initialize session state for memory and messages only
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# AWS Setup
@st.cache_resource
def setup_bedrock():
    try:
        session = boto3.Session(
            profile_name='Hackathon20'
        )
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

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.text(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you with your educational journey?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.text(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        try:
            # Get chat history from LangChain memory
            chat_history = st.session_state.memory.load_memory_variables({})
            history_str = ""
            if chat_history.get("chat_history"):
                history_str = "\n".join([
                    f"{msg.type}: {msg.content}" 
                    for msg in chat_history["chat_history"]
                ])

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
- Format salary information with ($) instead of USD (Example: $75000 per year)
- Use clear section headers followed by a newline
- Keep paragraphs short and readable
- Use dashes (-) for lists and asterisks (*) for emphasis
- when talking about salary of careers, use ($) instead of USD

CONVERSATION HISTORY:
{history}

USER MESSAGE: {user_message}

Use the conversation history to track what you know about the student. Ask about missing information naturally in conversation. When you have enough information, provide career and program recommendations based on the knowledge base."""

            full_prompt = system_prompt.format(
                history=history_str,
                user_message=prompt
            )

            # Call Bedrock Knowledge Base
            response = bedrock.retrieve_and_generate(
                input={
                    'text': full_prompt
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': kb_id,
                        'modelArn': f'arn:aws:bedrock:us-west-2::foundation-model/{model_id}'
                    }
                }
            )
            
            # Get the response stream
            stream = response['output']['text']
            
            def clean_text(text):
                # Replace USD with $ and handle formatting
                text = text.replace('USD ', '$')  # Replace USD with $
                text = text.replace(',', '')      # Remove commas from numbers
                
                # Preserve or enhance formatting
                lines = text.split('\n')
                formatted_lines = []
                
                for line in lines:
                    # Preserve empty lines for spacing
                    if not line.strip():
                        formatted_lines.append('')
                        continue
                    
                    # Clean up the line while preserving dashes and asterisks
                    cleaned_line = ' '.join(line.split())
                    formatted_lines.append(cleaned_line)
                
                # Join with newlines to preserve formatting
                return '\n'.join(formatted_lines)
            
            # Clean the stream text
            stream = clean_text(stream)
            
            # Process the stream with streaming effect
            message_placeholder = st.empty()
            full_response = ""
            
            # Split by newlines and words to maintain formatting during streaming
            paragraphs = stream.split('\n')
            for paragraph in paragraphs:
                words = paragraph.split()
                for i in range(0, len(words), 3):
                    chunk = " ".join(words[i:i+3])
                    full_response += chunk + " "
                    try:
                        message_placeholder.text(full_response + "▌")
                    except Exception:
                        message_placeholder.text(full_response)
                    time.sleep(0.1)
                full_response += "\n"  # Add newline after each paragraph
                try:
                    message_placeholder.text(full_response + "▌")
                except Exception:
                    message_placeholder.text(full_response)
                time.sleep(0.1)
            
            # Display final response without cursor
            message_placeholder.text(full_response)
            
            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Update LangChain memory
            st.session_state.memory.save_context(
                {"input": prompt},
                {"output": full_response}
            )
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.error("Please check your AWS credentials and knowledge base configuration")

# Clear conversation button
if st.sidebar.button("Clear Conversation"):
    st.session_state.messages = []
    st.session_state.memory.clear()
    st.rerun()
