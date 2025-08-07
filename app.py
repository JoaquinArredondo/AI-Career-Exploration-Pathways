import streamlit as st
import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get and validate knowledge base ID
KNOWLEDGE_BASE_ID = os.getenv('AWS_KNOWLEDGE_BASE_ID')
if not KNOWLEDGE_BASE_ID:
    raise ValueError("AWS_KNOWLEDGE_BASE_ID not found in .env file")

# Setup
st.set_page_config(page_title="Hartnell College AI Advisor", page_icon="🎓")
st.title("Hartnell College AI Advisor")
st.write("Ask me about Hartnell courses and programs!")

# AWS Setup
@st.cache_resource
def setup_bedrock():
    session = boto3.Session(profile_name='Hackathon20')
    return session.client(
        'bedrock-agent-runtime',
        region_name='us-west-2'
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

try:
    bedrock = setup_bedrock()
except Exception as e:
    st.error(f"Error setting up AWS client: {str(e)}")
    st.info("Please ensure you're logged in with 'aws sso login --profile Hackathon20'")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask about Hartnell courses and programs..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                # Call Bedrock Knowledge Base
                response = bedrock.retrieve_and_generate(
                    knowledgeBaseId=KNOWLEDGE_BASE_ID,
                    retrieveAndGenerateConfiguration={
                        'type': 'KNOWLEDGE_BASE',
                        'knowledgeBaseConfiguration': {
                            'modelArn': 'anthropic.claude-3-sonnet-20240229-v1:0',
                            'modelParameters': {
                                'temperature': 0.7,
                                'maxTokens': 2048,
                            }
                        }
                    },
                    prompt=(
                        "You are a helpful Hartnell College advisor. "
                        "Use the knowledge base to provide accurate information about courses and programs. "
                        "If you're not sure about something, say so and suggest talking to a human advisor.\n\n"
                        f"User question: {prompt}"
                    )
                )
                
                answer = response['output']['text']
                st.write(answer)
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("If this persists, please verify your AWS credentials and knowledge base ID")

# Add a reset button in the sidebar
with st.sidebar:
    st.header("Options")
    if st.button("Start New Conversation"):
        st.session_state.messages = []
        st.rerun()
