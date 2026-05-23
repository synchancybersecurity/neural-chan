import sys, os, re

with open('neural_window.py', 'r') as f:
    nw = f.read()

# Fix stats command to show domain breakdown
old_stats = """        elif command == 'stats':
            stats = self.conversation.get_stats()"""

new_stats = """        elif command == 'stats':
            stats = self.conversation.get_stats()
            self._cli_log(f'[STATS] Proficiency: {stats.get(\"proficiency\",0)}% | Words: {stats.get(\"words_learned\",0)} | Chats: {stats.get(\"conversations\",0)} | Mood: {stats.get(\"mood\",\"?\")}', 'green')
            try:
                import json
                with open(os.path.expanduser('~/neural-chan/data/vocabulary_v2.json')) as f:
                    v = json.load(f)
                for d, info in v.get('domains', {}).items():
                    self._cli_log(f'[DOMAIN] {d}: {info.get(\"count\",0)} terms', 'purple')
                self._cli_log(f'[BRAIN] Total dictionary entries: {len(v.get(\"dictionary\", {}))}', 'cyan')
            except Exception as e:
                self._cli_log(f'[WARN] Could not load domain stats: {e}', 'yellow')
            return"""

nw = nw.replace(old_stats, new_stats)

# Ensure export command exists
if "command == 'export'" not in nw:
    # Add after the new stats block
    old_after_stats = """            return"""
    new_after_stats = """            return
        elif command == 'export' or command == 'memory':
            try:
                from memory_exporter import MemoryExporter
                exporter = MemoryExporter()
                files = exporter.export_all()
                for f in files:
                    self._cli_log(f'[MEMORY] {f}', 'green')
                self._cli_log(f'[MEMORY] {len(files)} files saved to ~/neural-chan/memory/', 'green')
            except Exception as e:
                self._cli_log(f'[MEMORY] Export error: {e}', 'red')
            return"""
    # Only replace the first occurrence after stats
    parts = nw.split(old_after_stats, 1)
    if len(parts) == 2:
        nw = parts[0] + new_after_stats + parts[1]

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] neural_window.py patched — domain stats + export command')
