import sys, re

with open('neural_window.py', 'r') as f:
    nw = f.read()

# Replace imports
old_imports = """from neural_canvas import NeuralCanvas
from kaomoji_widget import KaomojiWidget"""
new_imports = """from neural_canvas import NeuralCanvas
from kaomoji_widget import KaomojiWidget
from neural_conversation_v2 import NeuralConversationV2
from system_monitor import SystemMonitor
from web_learner import WebLearner"""
nw = nw.replace(old_imports, new_imports)

# Add brain initialization
old_init = "        self.brain = None"
new_init = """        self.brain = None
        self.system_monitor = SystemMonitor()
        self.web_learner = WebLearner()
        self.conversation = NeuralConversationV2(
            system_monitor=self.system_monitor,
            web_learner=self.web_learner
        )"""
nw = nw.replace(old_init, new_init)

# Add setup calls
old_setup = "        self._setup_global_timer()"
new_setup = """        self._setup_global_timer()
        self._setup_system_monitor()
        self._setup_auto_save()"""
nw = nw.replace(old_setup, new_setup)

# Add new setup methods
old_global = "    def _setup_global_timer(self):"
new_methods = """    def _setup_system_monitor(self):
        self.system_monitor.start()
        self._cli_log('[SYSTEM] Monitor active: CPU, memory, processes, network', 'green')
    
    def _setup_auto_save(self):
        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self._auto_save_tick)
        self.save_timer.start(30000)
    
    def _auto_save_tick(self):
        try:
            self.conversation._save()
            self.system_monitor._save()
            if self.web_learner:
                self.web_learner._save()
        except:
            pass
    
    def _setup_global_timer(self):"""
nw = nw.replace(old_global, new_methods)

# Replace _cli_execute
old_cli = "    def _cli_execute(self):"
new_cli = """    def _cli_execute(self):
        cmd = self.cli_input.text().strip()
        if not cmd: return
        self._cli_log(f'> {cmd}', 'amber')
        self.cli_input.clear()
        parts = cmd.split()
        command = parts[0].lower()
        
        try:
            result = self.conversation.respond(cmd)
        except Exception as e:
            self._cli_log(f'[ERROR] Brain crash: {str(e)[:100]}', 'red')
            self.kaomoji.set_mood('Concerned')
            return
        
        self._cli_log(f'[NEURAL] {result["response"]}', 'cyan')
        self.kaomoji.set_mood(result['mood'])
        
        if result.get('new_words_learned'):
            words_str = ', '.join(result['new_words_learned'])
            self._cli_log(f'[LEARN] New words: {words_str} (+{len(result["new_words_learned"])} | Total: {result["total_words"]})', 'purple')
        
        if self.conversation.vocab['total_conversations'] % 5 == 0:
            self._cli_log(f'[PROFICIENCY] {result["proficiency"]}% | Chats: {self.conversation.vocab["total_conversations"]}', 'green')
        
        intent = result['intent']
        
        if intent == 'detect' or command == 'detect':
            self._detect_now()
        elif intent == 'status' or command == 'status':
            if self.brain:
                s = self.brain.get_status()
                self._cli_log(f'[STATUS] Auto={s["auto"]} Tix={s["tickets"]} Pat={s["patterns"]}', 'cyan')
        elif intent == 'agents' or command == 'agents':
            if self.brain:
                for name, info in self.brain.agents.items(): 
                    self._cli_log(f'  {name}: {info["status"]}', 'cyan')
        elif intent == 'tickets' or command == 'tickets':
            self._show_tickets()
        elif intent == 'memory' or command == 'memory':
            self._show_memory()
        elif intent == 'patterns' or command == 'patterns':
            if self.brain:
                for p in self.brain.patterns: self._cli_log(f'  {p}', 'purple')
        elif intent == 'stop' or command == 'stop':
            self._emergency_stop()
        elif intent == 'resume' or command == 'resume':
            self._resume()
        elif command == 'clear':
            self.cli_output.clear()
        elif intent == 'speak' or command == 'speak':
            text = ' '.join(parts[1:]) if len(parts) > 1 else result['response']
            self.kaomoji.speak(text)
        elif command == 'theme':
            color = parts[1] if len(parts) > 1 else 'crimson'
            self._cli_log(f'Theme: {color}', 'cyan')
        elif command == 'help':
            self._cli_log('Commands: detect status agents tickets memory patterns stop resume clear speak theme', 'cyan')
            self._cli_log('Chat: hello who are you what can you do joke time motivate me search <topic> system', 'cyan')
        elif command.startswith('name '):
            name = cmd[5:].strip()
            msg = self.conversation.set_user_name(name)
            self._cli_log(f'[NEURAL] {msg}', 'green')
        elif command == 'stats':
            stats = self.conversation.get_stats()
            self._cli_log(f'[STATS] Proficiency: {stats.get("proficiency",0)}% | Words: {stats.get("words_learned",0)} | Chats: {stats.get("conversations",0)} | Facts: {stats.get("facts",0)} | Mood: {stats.get("mood","?")}', 'green')
        elif command == 'webstats':
            if self.web_learner:
                ws = self.web_learner.get_stats()
                self._cli_log(f'[WEB] Cached: {ws["cached_topics"]} | Hits: {ws["cache_hits"]} | Misses: {ws["cache_misses"]} | Hit rate: {ws["hit_rate"]}%', 'cyan')
        elif command == 'sysinfo':
            if self.system_monitor:
                latest = self.system_monitor.get_latest()
                if latest:
                    self._cli_log(f'[SYS] CPU: {latest.get("cpu_percent",0)}% | MEM: {latest.get("mem_percent",0)}% | Procs: {latest.get("processes",0)} | Load: {latest.get("load_1m",0)}', 'cyan')
                    if latest.get('top_processes'):
                        for p in latest['top_processes']:
                            self._cli_log(f'  {p["name"]} (PID {p["pid"]}): {p["cpu"]}% CPU', 'cyan')"""

start_idx = nw.find(old_cli)
if start_idx != -1:
    end_idx = nw.find("    def set_brain(self, brain):", start_idx)
    if end_idx == -1:
        end_idx = len(nw)
    nw = nw[:start_idx] + new_cli + "\n" + nw[end_idx:]
    print('[✓] _cli_execute replaced')
else:
    print('[!] Could not find _cli_execute')

# Update status bar
old_status = "    def _setup_statusbar(self):\n        self.statusbar = QStatusBar()\n        self.setStatusBar(self.statusbar)\n        self.statusbar.showMessage('Neural Chan OS v1.5.1 | Ready | Agents: 6/6 Idle | Demo')"
new_status = """    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('Neural Chan OS v2.0 | Ready | Agents: 6/6 Idle | CPU: -- | MEM: --')
        self._update_statusbar()
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_statusbar)
        self.status_timer.start(3000)
    
    def _update_statusbar(self):
        try:
            if self.system_monitor and self.system_monitor.history:
                latest = self.system_monitor.get_latest()
                cpu = latest.get('cpu_percent', 0) if latest else 0
                mem = latest.get('mem_percent', 0) if latest else 0
                procs = latest.get('processes', 0) if latest else 0
                msg = f'Neural Chan v2.0 | Ready | Agents: 6/6 | CPU: {cpu}% | MEM: {mem}% | Procs: {procs}'
            else:
                msg = 'Neural Chan v2.0 | Ready | Agents: 6/6 | Monitor: offline'
            self.statusbar.showMessage(msg)
        except:
            pass"""
nw = nw.replace(old_status, new_status)

# Update title
nw = nw.replace("Neural Chan OS v1.5.1 — DEBUGGED", "Neural Chan OS v2.0 — SELF-LEARNING")

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] Neural Chan v2.0 integration complete')
