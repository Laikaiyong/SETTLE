from fireworks.client import Fireworks
import streamlit as st

FIREWORKS_API = st.secrets["fireworks"]["api_key"]
fw_client = Fireworks(api_key=FIREWORKS_API)
model = "accounts/fireworks/models/llama-v3-8b-instruct"

def generate_answer(user_query):
    """
    Generate an answer to the user query.

    Args:
        user_query (str): The user's query string.
    """
    # Use the `create_prompt` function above to create a chat prompt
    prompt = user_query

    # Use the `prompt` created above to populate the `content` field in the chat message
    response = fw_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    # Print the final answer
    return response.choices[0].message.content