import os
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
def get_llm_response(context: str, query: str) -> str:
    """
    send a user query and context to google gemini and return the assistant's response,
    Args:
        context (str): Background information delimited by triple backticks.
        query (str): The user's question to be answered based on context.
    Returns:
        str: The assistant's generated text response.
    Raises:
        ValueError: if the GEMINI_API_KEY environment veriable is not set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "Gemini_api_key environment variable is not set."
            "Please set it to your Google Gemini API key."
        )
    client = genai.Client(api_key=api_key)
    model = "gemini-3.6-flash"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text=(
                    "You are a helpful assistant that can answer questions based on the provided context delimited "
                    "with triple backticks.\n\n"
                    "You will be given a context and a user query. your tast is to generate a response that is "
                    "relevent to the query based on the context provided. if the context does not contain enough"
                    "information to answer the query, you should indicate that you do not have enough information "
                    "to provide a complete answer.\n\n"
                    "if the context is empty, you should respond with a message indicating that you do not have "
                    "enough information to answer the query.\n\n"
                    "you should always respond in a friendly and helpful manner. you should not include any "
                    "personal opinions or information in your responses.\n\n"
                    f"Context:\n'''{context}'''"
                )
            )
        ]
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text

    return response_text