import hashlib

class PatternMemory:
    def __init__(self):
        self.memory = {}

    def signature(self, text: str):
        return hashlib.sha256(text.encode()).hexdigest()[:12]

    def record(self, text: str):
        sig = self.signature(text)
        self.memory[sig] = self.memory.get(sig, 0) + 1
        return sig, self.memory[sig]

    def detect(self, text: str):
        sig = self.signature(text)
        if sig in self.memory:
            return True, self.memory[sig]
        return False, 0

pattern_memory = PatternMemory()
