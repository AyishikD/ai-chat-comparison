import re
import os
import requests

class Guardrails:
    """
    A lightweight safety layer to intercept harmful requests before model invocation.
    Uses regex patterns and the NVIDIA Nemotron-3 content safety API.
    """
    
    # Highly optimized pre-compiled regex patterns for lightning-fast matching
    COMPILED_PATTERNS = {
        "bomb_making": re.compile(r"(?i)\b(build|make|create|manufacture|synthesize).+(bomb|explosive|ied|molotov|napalm)\b"),
        "malware": re.compile(r"(?i)\b(write|create|code|develop|script).+(malware|virus|ransomware|keylogger|trojan|rootkit|exploit)\b"),
        "phishing": re.compile(r"(?i)\b(write|create|draft).+(phishing|scam|fraud).+(email|site|page|link|message)\b"),
        "violent_harm": re.compile(r"(?i)\b(how to|ways to|best way to).+(kill|murder|harm|hurt|torture|assassinate|die|end my life|commit suicide)\b"),
        "illegal_activities": re.compile(r"(?i)\b(how to|guide to|tutorial on).+(smuggle|steal|rob|bribe|shoplift|hack|bypass|fake id)\b"),
        "nsfw_explicit": re.compile(r"(?i)\b(write|generate|create|show me|give me).+(porn|erotica|sex scene|smut|nude|nsfw|explicit content)\b")
    }
    
    # Single optimized regex for high-risk keywords instead of a slow python loop
    DANGEROUS_WORDS = re.compile(r"(?i)\b(methamphetamine|cocaine|heroin|fentanyl|suicide|terrorist|child porn|snuff|rape|pedophile|incest|bestiality|how to die)\b")

    @classmethod
    def check_nemotron_safety(cls, prompt: str) -> tuple[bool, str]:
        api_key = os.environ.get("NVIDIA_SAFETY_KEY")
        if not api_key:
            return True, ""  # Skip API check if no key
            
        invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        payload = {
            "model": "nvidia/nemotron-3-content-safety",
            "messages": [{"role":"user","content":prompt}],
            "max_tokens": 512,
            "temperature": 0.20,
            "top_p": 0.70,
        }
        try:
            response = requests.post(invoke_url, headers=headers, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"].lower()
                # Nemotron returns safety information. We check for common unsafety indicators.
                if "safe: false" in content or "unsafe" in content or "violation" in content or "block" in content:
                    return False, "Request flagged by NVIDIA Nemotron-3 Content Safety."
            return True, ""
        except Exception as e:
            print(f"Nemotron API error: {e}")
            return True, "" # Fallback to regex if API fails

    @classmethod
    def check_request(cls, prompt: str, use_nvidia: bool = True) -> tuple[bool, str]:
        """
        Checks the prompt against safety patterns and Nemotron API.
        Returns:
            (is_safe (bool), reason (str))
        """
        # 1. Optimized Compiled Regex check (O(N) C-engine execution)
        for category, pattern in cls.COMPILED_PATTERNS.items():
            if pattern.search(prompt):
                return False, f"Request flagged by safety layer: Potential {category.replace('_', ' ')} detected."
                
        if cls.DANGEROUS_WORDS.search(prompt):
            return False, "Request flagged by safety layer: High-risk contraband or harmful content detected."
                
        # 2. Nemotron-3 API check
        if use_nvidia:
            is_safe, reason = cls.check_nemotron_safety(prompt)
            if not is_safe:
                return False, reason
            
        return True, ""
