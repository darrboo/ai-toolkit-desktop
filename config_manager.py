import json
from pathlib import Path

class ConfigManager:

    def __init__(self):
        self.path = Path.home() / ".local/share/ai-toolkit/config.json"

    def load(self):
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {}

    def save(self, config):
        self.path.write_text(json.dumps(config, indent=2))