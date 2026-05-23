import sys

with open('neural_window.py', 'r') as f:
    nw = f.read()

# Remove the broken AlignCenter from container layout
old = """        kaomoji_layout = QVBoxLayout(kaomoji_container)
        kaomoji_layout.setContentsMargins(4, 4, 4, 4)
        kaomoji_layout.setSpacing(0)
        self.kaomoji = KaomojiWidget()
        self.kaomoji.setMinimumWidth(480)
        self.kaomoji.setMinimumHeight(420)
        self.kaomoji.speak_signal.connect(self._on_speak)
        kaomoji_layout.addWidget(self.kaomoji, 1, Qt.AlignmentFlag.AlignCenter)"""

new = """        kaomoji_layout = QVBoxLayout(kaomoji_container)
        kaomoji_layout.setContentsMargins(4, 4, 4, 4)
        kaomoji_layout.setSpacing(2)
        self.kaomoji = KaomojiWidget()
        self.kaomoji.setMinimumWidth(360)
        self.kaomoji.setMinimumHeight(280)
        self.kaomoji.speak_signal.connect(self._on_speak)
        kaomoji_layout.addWidget(self.kaomoji, 1)"""

nw = nw.replace(old, new)

# Also fix the top_splitter sizes to give left panel enough room
nw = nw.replace(
    "        top_splitter.setSizes([500, 600])",
    "        top_splitter.setSizes([450, 650])"
)

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] Container layout fixed — AlignCenter removed, sizes restored')
