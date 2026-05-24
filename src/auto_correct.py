#!/usr/bin/env python3
"""Auto-correct common Neural Chan issues."""
import os, re

src_dir = os.path.dirname(os.path.abspath(__file__))

def fix_file(fname, patches):
    fpath = os.path.join(src_dir, fname)
    if not os.path.exists(fpath):
        print(f"[SKIP] {fname} not found")
        return
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    original = content
    for old, new in patches:
        if old in content:
            content = content.replace(old, new)
            print(f"[FIX] {fname}: {old[:40]}... → {new[:40]}...")
    if content != original:
        with open(fpath, 'w') as f:
            f.write(content)
        print(f"[SAVED] {fname}")

# Fix neural_window.py v1 contamination
fix_file('neural_window.py', [
    ('from neural_conversation import NeuralConversation', 'from neural_conversation_v2 import NeuralConversationV2'),
    ('self.conversation = NeuralConversation()', 'self.conversation = NeuralConversationV2(system_monitor=self.system_monitor, web_learner=self.web_learner)'),
    ('self.conversation = NeuralConversation(system_monitor=self.system_monitor)', 'self.conversation = NeuralConversationV2(system_monitor=self.system_monitor, web_learner=self.web_learner)'),
    ('vocab["total_conversations"]', 'vocab["conversations"]'),
    ('vocab["user_preferences"]', 'vocab'),
    ('result["total_words"]', 'result["total_words"]'),  # keep if already v2
])

# Fix neural_canvas.py slots
fix_file('neural_canvas.py', [
    ("'x3d','y3d','z3d','vx','vy','vz','radius','pulse','pulse_speed',",
     "'x3d','y3d','z3d','vx','vy','vz','radius','pulse','pulse_speed','_x2d','_y2d','_scale',"),
])

print("[✓] Auto-correction complete")
