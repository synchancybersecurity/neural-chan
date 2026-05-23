import sys

with open('neural_window.py', 'r') as f:
    nw = f.read()

# Fix 1: Larger Kaomoji minimum sizes
nw = nw.replace(
    "        self.kaomoji.setMinimumWidth(300)\n        self.kaomoji.setMinimumHeight(250)",
    "        self.kaomoji.setMinimumWidth(450)\n        self.kaomoji.setMinimumHeight(380)"
)

# Fix 2: Larger kaomoji container frame
nw = nw.replace(
    "        kaomoji_container.setStyleSheet('QFrame { border: 1px solid #330000; border-radius: 6px; background: #08080c; }')",
    "        kaomoji_container.setStyleSheet('QFrame { border: 1px solid #330000; border-radius: 8px; background: #08080c; }')"
)

# Fix 3: Safe _on_speak handler (wrap in try/except to prevent signal crash chain)
old_on_speak = """    def _on_speak(self, text):
        self._cli_log(f'[SPEAK] Neural Chan says: {text}', 'purple')
        self.kaomoji.set_mood('Happy')"""

new_on_speak = """    def _on_speak(self, text):
        try:
            self._cli_log(f'[SPEAK] Neural Chan says: {text}', 'purple')
            self.kaomoji.set_mood('Happy')
        except Exception as e:
            print(f'[_ON_SPEAK ERROR] {e}', file=sys.stderr)"""

nw = nw.replace(old_on_speak, new_on_speak)

# Fix 4: Safe _on_detection handler
old_on_det = """    def _on_detection(self, det):
        self.canvas.pulse_node('detector')
        self.kaomoji.set_mood('Alert')
        self._cli_log(f'[ALERT] {det["threat"]} | {det["severity"]}', 'red')"""

new_on_det = """    def _on_detection(self, det):
        try:
            self.canvas.pulse_node('detector')
            self.kaomoji.set_mood('Alert')
            self._cli_log(f'[ALERT] {det["threat"]} | {det["severity"]}', 'red')
        except Exception as e:
            print(f'[_ON_DETECTION ERROR] {e}', file=sys.stderr)"""

nw = nw.replace(old_on_det, new_on_det)

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] neural_window.py patched — larger container + safe handlers')
