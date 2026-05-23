import os
from google import genai
from google.genai import types
from app.assistants.base import BaseAssistant

class FrontierAssistant(BaseAssistant):
    """
    Assistant implementation for a Frontier model via Google Gemini API.
    Model: gemini-3.1-flash-lite
    Using the new official `google-genai` SDK.
    """
    def __init__(self, system_prompt: str):
        super().__init__(name="Google Gemini 3.1 Flash-Lite", system_prompt=system_prompt)
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = "gemini-3.1-flash-lite"
        
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def _convert_history_to_gemini_format(self):
        """Converts internal memory history to Gemini's expected Content types."""
        contents = []
        for msg in self.memory.history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
            )
        return contents

    def generate_stream(self, prompt: str):
        if not self.api_key or not self.client:
            yield "GEMINI_API_KEY is not set."
            return

        try:
            # 1. Grab converted history
            contents = self._convert_history_to_gemini_format()
            
            # 2. Append current user prompt
            contents.append(
                types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
            )

            # 3. Call generate_content_stream using the new SDK
            response = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.memory.system_prompt,
                    temperature=0.2
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"\n\nRequest failed: {str(e)}"
