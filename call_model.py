from dotenv import load_dotenv
import os
import boto3
import json

# Load environment variables
load_dotenv()

# Create a session with the profile
session = boto3.Session(profile_name='Hackathon20')
client = session.client('bedrock-runtime', region_name='us-west-2')

def call_bedrock_model(message: str):
    # Use the client from the session created above
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": message}],
    }

    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(payload)
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]

def call_bedrock_model_with_streaming(message: str):
    # Use the client from the session created above
    payload = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ]
    })

    response = client.invoke_model_with_response_stream(
        modelId='anthropic.claude-3-5-haiku-20241022-v1:0',
        body=payload
    )

    stream = response.get('body')
    for event in stream:
        chunk = event.get('chunk')
        if not chunk:
            continue
        chunk_data = json.loads(chunk.get('bytes').decode())
        if chunk_data.get("type") == "content_block_delta":
            delta = chunk_data.get("delta", {})
            text = delta.get("text")
            if text:
                print(text, end='', flush=True)

def main():
   # print(call_bedrock_model("explain what 16 personalities framework is?"))
    call_bedrock_model_with_streaming('\n\nmy interests are analytical, and creative what occupations should i do?')

if __name__ == "__main__":
    main()
