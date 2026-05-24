#!/usr/bin/env python3
"""Full syntax audit for Neural Chan codebase."""
import ast, os, sys, re

src_dir = os.path.dirname(os.path.abspath(__file__))
issues = []
files_checked = []

files_to_check = [
    'main.py', 'neural_window.py', 'neural_conversation_v2.py',
    'neural_canvas.py', 'neural_bridge.py', 'system_monitor.py',
    'web_learner.py', 'memory_exporter.py', 'vocab_ingest.py',
    'domain_ingest.py', 'kaomoji_widget.py', 'brain_thread.py',
    'neural_web.html'
]

for fname in files_to_check:
    fpath = os.path.join(src_dir, fname)
    if not os.path.exists(fpath):
        issues.append(f"[MISSING] {fname}")
        continue
    
    files_checked.append(fname)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Syntax check for .py files
    if fname.endswith('.py'):
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append(f"[SYNTAX] {fname}:{e.lineno} — {e.msg}")
        except Exception as e:
            issues.append(f"[PARSE] {fname} — {e}")
    
    # v1 contamination check
    if fname == 'neural_window.py':
        if 'from neural_conversation import NeuralConversation' in content:
            issues.append(f"[V1-IMPORT] {fname} imports v1 NeuralConversation")
        if 'self.conversation = NeuralConversation()' in content:
            issues.append(f"[V1-INIT] {fname} instantiates v1 NeuralConversation")
        if 'vocab["total_conversations"]' in content:
            issues.append(f"[V1-KEY] {fname} uses total_conversations")
        if 'vocab["user_preferences"]' in content:
            issues.append(f"[V1-KEY] {fname} uses user_preferences")
    
    # neural_canvas slot check
    if fname == 'neural_canvas.py':
        if "'_x2d'" not in content or "'_y2d'" not in content or "'_scale'" not in content:
            issues.append(f"[CANVAS-SLOT] {fname} missing _x2d/_y2d/_scale in __slots__")
    
    # neural_conversation_v2 check
    if fname == 'neural_conversation_v2.py':
        if 'def _generate_natural_response' not in content:
            issues.append(f"[CONV-MISSING] {fname} missing _generate_natural_response")
        if 'COMMON_WORDS' not in content:
            issues.append(f"[CONV-MISSING] {fname} missing COMMON_WORDS filter")
    
    # bridge check — look for 5757 anywhere in the file
    if fname == 'neural_bridge.py':
        if '5757' not in content:
            issues.append(f"[BRIDGE-PORT] {fname} not using port 5757")

print("=" * 60)
print(f"AUDIT COMPLETE — {len(files_checked)} files checked")
if issues:
    print(f"FOUND {len(issues)} ISSUES:")
    for i in issues:
        print(f"  {i}")
    sys.exit(1)
else:
    print("ALL CLEAN — no issues found")
    sys.exit(0)
