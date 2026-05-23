import sys

with open('neural_window.py', 'r') as f:
    nw = f.read()

# Add import
if 'from memory_exporter import MemoryExporter' not in nw:
    nw = nw.replace(
        'from neural_conversation_v2 import NeuralConversationV2',
        'from neural_conversation_v2 import NeuralConversationV2\nfrom memory_exporter import MemoryExporter'
    )

# Add init
if 'self.memory_exporter = MemoryExporter()' not in nw:
    nw = nw.replace(
        '        self.conversation = NeuralConversationV2(',
        '        self.memory_exporter = MemoryExporter()\n        self.conversation = NeuralConversationV2('
    )

# Add auto-save export to _auto_save_tick
old_save = """    def _auto_save_tick(self):
        try:
            self.conversation._save()
            self.system_monitor._save()
            if self.web_learner:
                self.web_learner._save()
        except:
            pass"""

new_save = """    def _auto_save_tick(self):
        try:
            self.conversation._save()
            self.system_monitor._save()
            if self.web_learner:
                self.web_learner._save()
            if self.memory_exporter:
                self.memory_exporter.export_all()
        except:
            pass"""

nw = nw.replace(old_save, new_save)

# Add CLI command 'memory' or 'export' handler
old_stats = """        elif command == 'stats':
            stats = self.conversation.get_stats()"""

new_stats = """        elif command == 'stats':
            stats = self.conversation.get_stats()
            self._cli_log(f'[STATS] Proficiency: {stats.get("proficiency",0)}% | Words: {stats.get("words_learned",0)} | Chats: {stats.get("conversations",0)} | Facts: {stats.get("facts",0)} | Mood: {stats.get("mood","?")}', 'green')
        elif command == 'export' or command == 'memory':
            if self.memory_exporter:
                files = self.memory_exporter.export_all()
                for f in files:
                    self._cli_log(f'[MEMORY] {f}', 'green')
                self._cli_log(f'[MEMORY] {len(files)} files saved to ~/neural-chan/memory/', 'green')
            else:
                self._cli_log('[MEMORY] Exporter not loaded', 'red')
            return"""

nw = nw.replace(old_stats, new_stats)

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] Auto-export integrated into neural_window.py')
