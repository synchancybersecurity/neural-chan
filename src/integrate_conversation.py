import sys, re

with open('neural_window.py', 'r') as f:
    nw = f.read()

# Add import
if 'from neural_conversation import NeuralConversation' not in nw:
    nw = nw.replace(
        'from neural_canvas import NeuralCanvas',
        'from neural_canvas import NeuralCanvas\nfrom neural_conversation import NeuralConversation'
    )

# Add conversation brain init
if 'self.conversation' not in nw:
    nw = nw.replace(
        "        self.brain = None",
        "        self.brain = None\n        self.conversation = NeuralConversation()"
    )

# Replace _cli_execute
old_start = "    def _cli_execute(self):"
old_end = "        else: self._cli_log(f'Unknown: {command}', 'red')"

new_method = """    def _cli_execute(self):
        cmd = self.cli_input.text().strip()
        if not cmd: return
        self._cli_log(f'> {cmd}', 'amber')
        self.cli_input.clear()
        parts = cmd.split()
        command = parts[0].lower()
        
        # Route through conversational brain FIRST
        result = self.conversation.respond(cmd)
        
        # Always show the conversational response
        self._cli_log(f'[NEURAL] {result["response"]}', 'cyan')
        
        # Update Kaomoji mood based on conversation
        self.kaomoji.set_mood(result['mood'])
        
        # Show learning feedback if new words were learned
        if result['new_words_learned']:
            words_str = ', '.join(result['new_words_learned'])
            self._cli_log(f'[LEARN] New words: {words_str} (+{len(result["new_words_learned"])} | Total: {result["total_words"]})', 'purple')
        
        # Show proficiency progress occasionally
        if self.conversation.vocab['total_conversations'] % 5 == 0:
            self._cli_log(f'[PROFICIENCY] {result["proficiency"]}% | Chats: {self.conversation.vocab["total_conversations"]}', 'green')
        
        # Now handle specific commands
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
            self._cli_log('Chat: hello who are you what can you do joke time motivate me', 'cyan')
        elif command.startswith('name '):
            name = cmd[5:].strip()
            msg = self.conversation.set_user_name(name)
            self._cli_log(f'[NEURAL] {msg}', 'green')
        elif command == 'stats':
            stats = self.conversation.get_stats()
            self._cli_log(f'[STATS] Proficiency: {stats["proficiency"]}% | Words: {stats["words_learned"]} | Chats: {stats["conversations"]} | Mood: {stats["mood"]}', 'green')"""

start_idx = nw.find(old_start)
end_idx = nw.find(old_end)
if start_idx != -1 and end_idx != -1:
    end_idx += len(old_end)
    nw = nw[:start_idx] + new_method + nw[end_idx:]
    print('[✓] _cli_execute replaced')
else:
    print('[!] Could not find old method')

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] Integration complete')
