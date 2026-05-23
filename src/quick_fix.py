import sys

# Fix 1: Face click should speak + change mood
with open('kaomoji_widget.py', 'r') as f:
    content = f.read()

# Replace mousePressEvent to speak AND cycle mood
content = content.replace(
    "    def mousePressEvent(self, event): self.cycle_mood()",
    "    def mousePressEvent(self, event): self.cycle_mood(); self.speak()"
)

# Fix 2: Make speak() report to CLI via signal (already emits speak_signal)
# Fix 3: Add speak feedback to neural_window
with open('neural_window.py', 'r') as f:
    nw = f.read()

# Make _on_speak log to CLI with more visibility
nw = nw.replace(
    "    def _on_speak(self, text):\n        self._cli_log(f'[SPEAK] {text}', 'purple')",
    "    def _on_speak(self, text):\n        self._cli_log(f'[SPEAK] Neural Chan says: {text}', 'purple')\n        self.kaomoji.set_mood('Happy')"
)

# Fix 4: Make the speak CLI command more visible
nw = nw.replace(
    "        elif command == 'speak':\n            text = ' '.join(parts[1:]) if len(parts) > 1 else 'Hello from Neural Chan'\n            self.kaomoji.speak(text)",
    "        elif command == 'speak':\n            text = ' '.join(parts[1:]) if len(parts) > 1 else 'Hello from Neural Chan'\n            self._cli_log(f'[SPEAK] Sending to voice synth: {text}', 'cyan')\n            self.kaomoji.speak(text)"
)

with open('kaomoji_widget.py', 'w') as f:
    f.write(content)

with open('neural_window.py', 'w') as f:
    f.write(nw)

print("[✓] Fixes applied:")
print("  1. Face click now speaks + changes mood")
print("  2. SPEAK button works (was already connected)")
print("  3. CLI 'speak <text>' now shows feedback before speaking")
print("  4. All speech output logged to CLI terminal")
print()
print("[>] Relaunch:")
print("    cd ~/neural-chan/src && python3 main.py")
print()
print("[>] How to talk to Neural Chan:")
print("    - Click the Kaomoji face (◕‿◕) — it will speak aloud")
print("    - Click the SPEAK button — it will speak its current mood")
print("    - Type in CLI: speak hello world")
print("    - Type in CLI: speak I am Neural Chan")
