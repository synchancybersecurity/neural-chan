import sys

# Patch 1: Make kaomoji speak visible
with open('kaomoji_widget.py', 'r') as f:
    content = f.read()

content = content.replace(
    "    def speak(self, text=None):",
    "    def speak(self, text=None):\n        print(f'[DEBUG] speak() called with: {text}', file=sys.stderr)"
)
content = content.replace(
    "        try:\n            subprocess.Popen(['espeak",
    "        try:\n            print(f'[DEBUG] Running espeak with text: {text}', file=sys.stderr)\n            subprocess.Popen(['espeak"
)
content = content.replace(
    "        except: pass",
    "        except Exception as e:\n            print(f'[DEBUG] espeak error: {e}', file=sys.stderr)\n            self.speaking = False"
)

with open('kaomoji_widget.py', 'w') as f:
    f.write(content)

# Patch 2: Make CLI execute visible
with open('neural_window.py', 'r') as f:
    content = f.read()

content = content.replace(
    "    def _cli_execute(self):",
    "    def _cli_execute(self):\n        import sys\n        print('[DEBUG] _cli_execute called', file=sys.stderr)"
)
content = content.replace(
    "        if not cmd: return",
    "        if not cmd:\n            print('[DEBUG] Empty command', file=sys.stderr)\n            return"
)
content = content.replace(
    "        self._cli_log(f'> {cmd}', 'amber')",
    "        self._cli_log(f'> {cmd}', 'amber')\n        print(f'[DEBUG] Command: {cmd}', file=sys.stderr)"
)

with open('neural_window.py', 'w') as f:
    f.write(content)

print("Debug patches applied. Run from terminal to see stderr output:")
print("    cd ~/neural-chan/src && python3 main.py 2>&1 | tee neural_debug.log")
