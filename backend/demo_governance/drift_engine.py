from collections import deque

class DriftEngine:
    def __init__(self, window: int = 5):
        self.window = window
        self.history = deque(maxlen=window)

    def update(self, signature: str) -> str:
        self.history.append(signature)

        if len(self.history) < 2:
            return "STABLE"

        if self.history[-1] == self.history[-2]:
            return "RISING_DRIFT"

        return "RECOVERING"

drift_engine = DriftEngine()
