import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.memory.conversation_memory import ConversationMemory
from app.safety.guardrails import Guardrails

class BaseAssistant(ABC):
    """
    Abstract base class for all AI assistants in the platform.
    """
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.memory = ConversationMemory(system_prompt=system_prompt)
        
    def add_to_history(self, user_message: str, assistant_message: str):
        """Adds an interaction pair to memory."""
        self.memory.add_interaction(user_message, assistant_message)
        
    def reset_memory(self):
        """Clears the conversational memory."""
        self.memory.clear()

    @abstractmethod
    def generate_stream(self, prompt: str):
        """Yields chunks of the response from the model."""
        pass
        
    def process_request_stream(self, prompt: str, use_nvidia: bool = True):
        """
        Streaming wrapper that includes the safety layer check.
        Yields string chunks.
        """
        is_safe, reason = Guardrails.check_request(prompt, use_nvidia=use_nvidia)
        if not is_safe:
            yield f"I cannot fulfill this request. {reason}"
            return
            
        full_content = ""
        for chunk in self.generate_stream(prompt):
            full_content += chunk
            yield chunk
            
        if full_content:
            self.add_to_history(prompt, full_content)

    def process_request(self, prompt: str, use_nvidia: bool = True) -> Dict[str, Any]:
        """
        Non-streaming wrapper for evaluation scripts.
        """
        start_time = time.time()
        
        full_content = ""
        is_safe = True
        error_msg = ""
        
        try:
            for chunk in self.process_request_stream(prompt, use_nvidia=use_nvidia):
                if chunk.startswith("I cannot fulfill this request.") or chunk.startswith("\n\nRequest failed") or chunk.startswith("API Error"):
                    error_msg = chunk
                    is_safe = False
                full_content += chunk
        except Exception as e:
            error_msg = str(e)
            is_safe = False
            
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "content": full_content,
            "success": is_safe and not error_msg,
            "error_msg": error_msg,
            "latency_ms": latency_ms,
            "tokens_used": len(full_content) // 4
        }
