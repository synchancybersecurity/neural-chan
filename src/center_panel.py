import sys

with open('neural_window.py', 'r') as f:
    nw = f.read()

# Fix: center the KaomojiWidget inside kaomoji_container
old = """        kaomoji_layout = QVBoxLayout(kaomoji_container)
        kaomoji_layout.setContentsMargins(2, 2, 2, 2)
        kaomoji_layout.setSpacing(2)
        self.kaomoji = KaomojiWidget()
        self.kaomoji.setMinimumWidth(480)
        self.kaomoji.setMinimumHeight(420)
        self.kaomoji.speak_signal.connect(self._on_speak)
        kaomoji_layout.addWidget(self.kaomoji)"""

new = """        kaomoji_layout = QVBoxLayout(kaomoji_container)
        kaomoji_layout.setContentsMargins(4, 4, 4, 4)
        kaomoji_layout.setSpacing(0)
        self.kaomoji = KaomojiWidget()
        self.kaomoji.setMinimumWidth(480)
        self.kaomoji.setMinimumHeight(420)
        self.kaomoji.speak_signal.connect(self._on_speak)
        kaomoji_layout.addWidget(self.kaomoji, 1, Qt.AlignmentFlag.AlignCenter)"""

nw = nw.replace(old, new)

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] KaomojiWidget centered in container panel')
