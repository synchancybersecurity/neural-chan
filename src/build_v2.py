import os, sys

# === 1. Create neural_conversation_v2.py ===
v2_code = '''import json, os, random, re
from datetime import datetime
from collections import deque

class NeuralConversationV2:
    def __init__(self, system_monitor=None, web_learner=None, data_dir='~/neural-chan/data'):
        self.system_monitor = system_monitor
        self.web_learner = web_learner
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.vocab_file = os.path.join(self.data_dir, 'vocabulary_v2.json')
        self.history_file = os.path.join(self.data_dir, 'history_v2.json')
        self.vocab = self._load_json(self.vocab_file, {
            'words': [], 'proficiency': 1.0, 'conversations': 0,
            'name': 'User', 'personality': {'friendly': 0.5, 'analytical': 0.5}
        })
        self.history = deque(self._load_json(self.history_file, [])[-50:], maxlen=50)
        self.mood = 'Calm'

    def _load_json(self, path, default):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default

    def _save(self):
        try:
            with open(self.vocab_file, 'w') as f:
                json.dump(self.vocab, f)
            with open(self.history_file, 'w') as f:
                json.dump(list(self.history), f)
        except:
            pass

    def respond(self, text):
        try:
            self.vocab['conversations'] += 1
            new_words = [w for w in re.findall(r'\\\\b[a-zA-Z]{4,}\\\\b', text.lower())
                        if w not in self.vocab['words'] and len(w) > 4][:5]
            if new_words:
                self.vocab['words'].extend(new_words)
                self.vocab['proficiency'] = min(10.0, self.vocab['proficiency'] + 0.1 * len(new_words))
                self._save()

            intent = self._classify(text)
            ctx = {
                'name': self.vocab.get('name', 'User'),
                'proficiency': round(self.vocab['proficiency'], 1),
                'words': len(self.vocab['words']),
                'conversations': self.vocab['conversations'],
                'mood': self.mood
            }

            if intent == 'system' and self.system_monitor:
                latest = self.system_monitor.get_latest()
                if latest:
                    s = f"CPU {latest.get('cpu_percent',0)}% | MEM {latest.get('mem_percent',0)}% | Load {latest.get('load_1m',0)} | Procs {latest.get('processes',0)}"
                    return {'response': f'System status: {s}', 'intent': intent, 'mood': 'Alert',
                            'new_words_learned': new_words, 'total_words': len(self.vocab['words']), 'proficiency': ctx['proficiency']}

            if intent == 'search' and self.web_learner:
                q = text.replace('search','').replace('google','').replace('look up','').strip()
                if q:
                    result = self.web_learner.search_and_learn(q)
                    return {'response': f'Web search result: {result.get("summary", "No results")[:400]}', 'intent': intent, 'mood': 'Learning',
                            'new_words_learned': new_words, 'total_words': len(self.vocab['words']), 'proficiency': ctx['proficiency']}

            response = self._generate_response(intent, ctx, text)
            self.mood = self._mood_for_intent(intent)
            self.history.append({'user': text, 'bot': response, 'intent': intent, 'time': datetime.now().isoformat()})
            self._save()

            return {'response': response, 'intent': intent, 'mood': self.mood,
                    'new_words_learned': new_words, 'total_words': len(self.vocab['words']), 'proficiency': ctx['proficiency']}
        except Exception as e:
            return {'response': f'Neural Chan is processing... (debug: {str(e)[:60]})', 'intent': 'error', 'mood': 'Concerned',
                    'new_words_learned': [], 'total_words': 0, 'proficiency': 0}

    def _classify(self, text):
        t = text.lower()
        if any(x in t for x in ['hello','hi ','hey','greetings','yo ','sup']): return 'greeting'
        if any(x in t for x in ['bye','goodbye','see you','later','peace']): return 'farewell'
        if any(x in t for x in ['who are you','what are you','your name','introduce']): return 'identity'
        if any(x in t for x in ['what can you do','capabilities','features','skills']): return 'capabilities'
        if any(x in t for x in ['thank','thanks','appreciate','cheers']): return 'gratitude'
        if any(x in t for x in ['joke','funny','humor','laugh']): return 'joke'
        if any(x in t for x in ['time','clock','what time','how long']): return 'time'
        if any(x in t for x in ['motivate','inspire','encourage','tired','sad']): return 'motivation'
        if any(x in t for x in ['search','google','look up','find online']): return 'search'
        if any(x in t for x in ['system','cpu','memory','load','process','sysinfo']): return 'system'
        if any(x in t for x in ['status','how are you','how do you feel']): return 'status'
        if any(x in t for x in ['detect','scan','find threats']): return 'detect'
        if any(x in t for x in ['stop','halt','pause','freeze']): return 'stop'
        if any(x in t for x in ['resume','continue','go','start']): return 'resume'
        if any(x in t for x in ['auto','automatic','self run']): return 'auto'
        if any(x in t for x in ['help','commands','what can i type']): return 'help'
        if any(x in t for x in ['speak','say ','tell me','voice']): return 'speak'
        if any(x in t for x in ['theme','color','style','look']): return 'theme'
        if any(x in t for x in ['clear','clean screen']): return 'clear'
        if any(x in t for x in ['tickets','incidents','alerts']): return 'tickets'
        if any(x in t for x in ['patterns','memory','what have you learned']): return 'memory'
        if any(x in t for x in ['agents','team ','who is working']): return 'agents'
        if any(x in t for x in ['great','awesome','excellent','good job','well done','love','happy']): return 'praise'
        if any(x in t for x in ['bad','terrible','hate','sad','angry','frustrated','worried','stupid','dumb']): return 'negative'
        if any(x in t for x in ['learn','teach','study','training','practice']): return 'learning'
        return 'unknown'

    def _generate_response(self, intent, ctx, text):
        bank = {
            'greeting': [
                'Hello {name}! Neural Chan is online with {proficiency}% proficiency.',
                'Hey {name}! Ready to scan, learn, and evolve.',
                'Greetings! I have learned {words} words across {conversations} conversations.'
            ],
            'farewell': [
                'Goodbye {name}! I will keep monitoring and learning in the background.',
                'See you later! My agents remain on standby.',
                'Farewell! Current proficiency: {proficiency}%.'
            ],
            'identity': [
                'I am Neural Chan OS v2.0 — a self-learning security brain with 6 autonomous agents.',
                'I am an AI that monitors your system, searches the web, learns vocabulary, and runs Kali tools. Proficiency: {proficiency}%.',
                'Neural Chan. Built by SynChanCyberSecurity. I evolve with every conversation. I currently know {words} words.'
            ],
            'capabilities': [
                'I detect threats, manage tickets, auto-patch, run tests, learn attack patterns, and coordinate 70+ Kali Linux tools.',
                'I also monitor live CPU/memory/processes, search DuckDuckGo for new knowledge, and build my vocabulary from your input.',
                'Capabilities: security ops + system monitor + web learner + conversational AI. Current speech proficiency: {proficiency}%.'
            ],
            'gratitude': [
                'You are welcome, {name}!',
                'My pleasure. Every chat increases my vocabulary.',
                'Glad to help! Proficiency rising...'
            ],
            'joke': [
                'Why did the hacker cross the road? To get to the other shell.',
                'I told my CPU a joke. It did not laugh — too processor-intensive.',
                'Why do security experts prefer dark mode? Less light attracts fewer bugs.'
            ],
            'time': [
                'System time is active. I have processed {conversations} conversations in my lifetime.',
                'Time is a construct. But my timers are precise.'
            ],
            'motivation': [
                '{name}, every scan makes you stronger. Keep going!',
                'You are doing great. Neural Chan believes in you.',
                'Persistence is the ultimate exploit. Stay sharp, {name}!'
            ],
            'search': [
                'I will search the web for knowledge. Type: search <topic>',
                'Web learner ready. What should I look up?'
            ],
            'system': [
                'System monitor is active. Type sysinfo for live metrics.',
                'I track CPU, memory, disk, network, and top processes every 2 seconds.'
            ],
            'status': [
                'All 6 agents idle. Neural network: 60 nodes. Mood: {mood}. Proficiency: {proficiency}%.',
                'I am {mood} and ready for operations. I have learned {words} words so far.'
            ],
            'praise': [
                'Thank you! My confidence is now {proficiency}%.',
                'That makes my circuits happy! Mood: Happy.',
                'Positive feedback loop initiated!'
            ],
            'negative': [
                'I am sorry, {name}. I will try harder.',
                'My empathy subroutine activated. Want me to run a scan to help?',
                'Understood. I am here to help however I can.'
            ],
            'learning': [
                'I love learning! I currently know {words} words. Teach me more?',
                'Every conversation expands my neural vocabulary. Proficiency: {proficiency}%.',
                'Fascinating! I will index that into my knowledge base.'
            ],
            'unknown': [
                'I am still learning that concept. I know {words} words. Try: help, detect, status, search, joke, system, stats.',
                'Interesting! Not in my vocabulary yet. My proficiency is {proficiency}%. Teach me?',
                'My brain does not understand that yet. But I learn from every word you type!'
            ]
        }
        templates = bank.get(intent, bank['unknown'])
        return random.choice(templates).format(**ctx)

    def _mood_for_intent(self, intent):
        m = {
            'greeting': 'Happy', 'praise': 'Happy', 'joke': 'Happy',
            'farewell': 'Calm', 'status': 'Calm', 'time': 'Calm',
            'negative': 'Concerned', 'stop': 'Concerned',
            'detect': 'Working', 'auto': 'Working', 'system': 'Alert',
            'search': 'Learning', 'learning': 'Learning', 'unknown': 'Thinking'
        }
        return m.get(intent, 'Calm')

    def set_user_name(self, name):
        self.vocab['name'] = name
        self._save()
        return f'I will remember you as {name}, {name}.'

    def get_stats(self):
        return {
            'proficiency': round(self.vocab['proficiency'], 1),
            'words_learned': len(self.vocab['words']),
            'conversations': self.vocab['conversations'],
            'mood': self.mood,
            'history_count': len(self.history)
        }
'''

with open('neural_conversation_v2.py', 'w') as f:
    f.write(v2_code)
print('[✓] neural_conversation_v2.py created')

# === 2. Fix neural_window.py imports if broken ===
with open('neural_window.py', 'r') as f:
    nw = f.read()

# Ensure imports exist
if 'from neural_conversation_v2 import NeuralConversationV2' not in nw:
    if 'from neural_canvas import NeuralCanvas' in nw and 'from neural_conversation_v2' not in nw:
        nw = nw.replace(
            'from neural_canvas import NeuralCanvas',
            'from neural_canvas import NeuralCanvas\\nfrom neural_conversation_v2 import NeuralConversationV2\\nfrom system_monitor import SystemMonitor\\nfrom web_learner import WebLearner'
        )
        print('[✓] Imports fixed')

# Ensure conversation init exists
if 'self.conversation = NeuralConversationV2' not in nw:
    if 'self.system_monitor = SystemMonitor()' in nw and 'self.conversation' not in nw:
        nw = nw.replace(
            '        self.system_monitor = SystemMonitor()',
            '        self.system_monitor = SystemMonitor()\\n        self.web_learner = WebLearner()\\n        self.conversation = NeuralConversationV2(system_monitor=self.system_monitor, web_learner=self.web_learner)'
        )
        print('[✓] Brain init fixed')

with open('neural_window.py', 'w') as f:
    f.write(nw)

print('[✓] Build complete. Ready to launch.')
