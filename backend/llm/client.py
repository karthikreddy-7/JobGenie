import logging
from typing import List, Dict, Generator, Optional
from ollama import chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaChatClient:
    def __init__(self, model: str = "gemma3:1b"):
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
    client = OllamaChatClient(model="gemma3:1b")
    response = client.send_message(
        messages=[{"role": "user", "content": "Can you return karthik email"}],
        stream=False
    )
    print("Non-stream response:", response)
    print("\nStream response:")
    client.send_message(
        messages=[{"role": "user", "content": "Tell me a short story about Karthik"}],
        stream=True
    )
