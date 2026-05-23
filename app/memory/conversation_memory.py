from typing import List, Dict

class ConversationMemory:
    """
    Manages the rolling conversational memory for the AI assistants.
    Retains the system prompt and the last 10 conversation pairs (20 messages).
    """
    def __init__(self, system_prompt: str, max_pairs: int = 10):
        self.system_prompt = system_prompt
        self.max_pairs = max_pairs
        # History only stores user and assistant messages, not the system prompt
        self.history: List[Dict[str, str]] = []

    def add_interaction(self, user_message: str, assistant_message: str):
        """Adds a user-assistant interaction pair to the history."""
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_message})
        
        # Enforce rolling window (max_pairs * 2 messages)
        max_messages = self.max_pairs * 2
        if len(self.history) > max_messages:
            # Keep the last max_messages
            self.history = self.history[-max_messages:]

    def get_messages(self) -> List[Dict[str, str]]:
        """
        Returns the full conversation history to send to the model.
        Format: [{"role": "system", "content": ...}, {"role": "user", "content": ...}, ...]
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.history)
        return messages

    def clear(self):
        """Resets the conversation history."""
        self.history = []
