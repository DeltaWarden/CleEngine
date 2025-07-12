from typing import Callable

class HotkeyManager:
    def __init__(self):
        self.handlers = {}

    def register(self, key: str, action: Callable):
        self.handlers[key.lower()] = action

    def handle(self, key: str):
        key = key.lower()
        if key in self.handlers:
            self.handlers[key]() 