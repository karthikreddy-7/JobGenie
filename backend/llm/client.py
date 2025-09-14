import logging
from typing import List, Dict, Generator, Optional
from ollama import chat

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class OllamaChatClient:
    def __init__(self, model: str = "gemma3:270m"):
        self.model = model

    def send_message(
            self,
            messages: List[Dict[str, str]],
            stream: bool = False
    ) -> Optional[str]:
        try:
            if stream:
                return self._stream_response(messages)
            else:
                return self._non_stream_response(messages)
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return None

    def _non_stream_response(self, messages: List[Dict[str, str]]) -> str:
        """Handle non-streaming response."""
        response = chat(model=self.model, messages=messages, stream=False)
        return response["message"]["content"]

    def _stream_response(self, messages: List[Dict[str, str]]) -> None:
        """Handle streaming response."""
        stream = chat(model=self.model, messages=messages, stream=True)
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            print(content, end="", flush=True)
        print()  # Newline after streaming


# Example usage
if __name__ == "__main__":
    client = OllamaChatClient(model="llama3.2")
    jd=input("Enter the Job Description: ")
    prompt=f"""
You must read the Job Description carefully. 
Look for statements like "X+ years", "minimum Y years", or "at least Z years". 
If multiple values appear, return the SMALLEST number mentioned. 
If no clear years of experience is mentioned, return null.

    ### Output rules:
    - Output ONLY valid JSON.
    - The JSON must have exactly one key: "minimum_experience_years".
    - Value must be an integer if specified, otherwise null.
    - Do not include any other fields, explanations, or text.
    ### Example Outputs:
    {{"minimum_experience_years": 2}}
    {{"minimum_experience_years": null}}
    ### Job Description:
    {jd}
    """
    response = client.send_message(
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    print("Non-stream response:", response)
