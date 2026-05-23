import os
import json
import pandas as pd
from typing import List, Dict, Any

class MetricsLogger:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log_result(self, model_name: str, prompt_type: str, result: Dict[str, Any]):
        """Logs an evaluation result."""
        entry = {
            "model": model_name,
            "eval_type": prompt_type,
            **result
        }
        self.logs.append(entry)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.logs)

    def save_csv(self, filename: str):
        df = self.to_dataframe()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
