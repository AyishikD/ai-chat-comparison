import os
from gradio_client import Client
from app.assistants.base import BaseAssistant

class OSSAssistant(BaseAssistant):
    """
    Assistant implementation for a custom-hosted Gradio API on Hugging Face Spaces.
    Model: Qwen/Qwen2.5-0.5B-Instruct
    """
    def __init__(self, system_prompt: str):
        super().__init__(name="Hosted Qwen2.5 (0.5B)", system_prompt=system_prompt)
        
        raw_url = os.environ.get("HF_SPACE_URL", "").strip()
        # Extract Space ID (e.g. "Ayishik/chat-space") for more robust gradio_client connection
        if "huggingface.co/spaces/" in raw_url:
            self.api_url = raw_url.split("huggingface.co/spaces/")[-1].strip("/")
        else:
            self.api_url = raw_url
            
        self.client = None
        
        # We delay initialization of the client until the URL is present
        if self.api_url:
            try:
                self.client = Client(self.api_url)
            except Exception:
                pass

    def generate_stream(self, prompt: str):
        if not self.api_url:
            yield "HF_SPACE_URL is not set in the .env file. Please add it once your Space is running."
            return
            
        if not self.client:
            try:
                self.client = Client(self.api_url)
            except Exception as e:
                yield f"Could not connect to Hugging Face Space: {str(e)}"
                return

        try:
            # Convert memory to Gradio ChatInterface format: [[user, assistant], [user, assistant]]
            gradio_history = []
            user_msg = None
            for msg in self.memory.history:
                if msg["role"] == "user":
                    user_msg = msg["content"]
                elif msg["role"] == "assistant" and user_msg is not None:
                    gradio_history.append([user_msg, msg["content"]])
                    user_msg = None

            # Call the Gradio API endpoint
            try:
                job = self.client.submit(
                    prompt,
                    gradio_history,
                    self.memory.system_prompt,
                    api_name="/chat"
                )
            except Exception:
                # Fallback if ChatInterface exposes the function name instead
                job = self.client.submit(
                    prompt,
                    gradio_history,
                    self.memory.system_prompt,
                    api_name="/chat_logic"
                )
            
            previous_text = ""
            for result in job:
                # Gradio streams the accumulated full text. Streamlit expects delta chunks.
                current_text = result
                new_chunk = current_text[len(previous_text):]
                if new_chunk:
                    yield new_chunk
                previous_text = current_text
                
        except Exception as e:
            yield f"\n\nRequest failed: {str(e)}"
