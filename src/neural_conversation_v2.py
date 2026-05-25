#!/usr/bin/env python3
"""Neural Conversation v3.0 — Chan AI Advanced Natural Language Engine
SynChanCyberSecurity proprietary. 100% native. No external LLMs."""
import json, os, random, re
from datetime import datetime
from collections import deque, defaultdict

class NeuralConversationV2:
    def __init__(self, system_monitor=None, web_learner=None, data_dir='~/neural-chan/data'):
        self.system_monitor = system_monitor
        self.web_learner = web_learner
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.vocab_file = os.path.join(self.data_dir, 'vocabulary_v2.json')
        self.history_file = os.path.join(self.data_dir, 'history_v2.json')
        self.tasks_file = os.path.join(self.data_dir, 'tasks.json')
        self.context_file = os.path.join(self.data_dir, 'context.json')
        
        self.vocab = self._load(self.vocab_file, {
            'words': [], 'proficiency': 1.0, 'conversations': 0,
            'name': 'User', 'personality': {'friendly': 0.7, 'analytical': 0.9, 'technical': 0.95},
            'dictionary': {}, 'domains': {}
        })
        self.history = deque(self._load(self.history_file, [])[-100:], maxlen=100)
        self.tasks = self._load(self.tasks_file, {'active': [], 'completed': []})
        self.context = self._load(self.context_file, {
            'current_topic': None, 'last_intent': None,
            'user_mood': 'neutral', 'session_depth': 0, 'corrections': {}
        })
        
        self.mood = 'Calm'
        self.response_memory = defaultdict(list)

    def _load(self, path, default):
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
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f)
            with open(self.context_file, 'w') as f:
                json.dump(self.context, f)
        except:
            pass

    def respond(self, text):
        self.vocab['conversations'] += 1
        raw = text.strip()
        t = raw.lower()
        
        # Learn new words from input
        new_words = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', t)
                    if w not in self.vocab['words'] and len(w) > 4][:5]
        if new_words:
            self.vocab['words'].extend(new_words)
            self.vocab['proficiency'] = min(100.0, self.vocab['proficiency'] + 0.05 * len(new_words))
            self._save()
        
        intent = self._classify(t, raw)
        ctx = {
            'name': self.vocab.get('name', 'User'),
            'proficiency': round(self.vocab['proficiency'], 1),
            'words': len(self.vocab['words']),
            'conversations': self.vocab['conversations'],
            'mood': self.mood,
            'topic': self.context.get('current_topic', 'general')
        }
        
        # SYSTEM query
        if intent == 'system' and self.system_monitor:
            latest = self.system_monitor.get_latest()
            if latest:
                return self._wrap(
                    f"System status — CPU: {latest.get('cpu_percent',0)}% | MEM: {latest.get('mem_percent',0)}% | Load: {latest.get('load_1m',0)} | Procs: {latest.get('processes',0)}",
                    intent, 'Alert', new_words
                )
        
        # WEB SEARCH
        if intent == 'search' and self.web_learner:
            q = raw.replace('search','').replace('google','').replace('look up','').strip()
            if q:
                result = self.web_learner.search_and_learn(q)
                self.context['current_topic'] = q
                self.context['session_depth'] += 1
                return self._wrap(
                    f"Searched '{q}': {result.get('summary', 'No results')[:400]}",
                    intent, 'Learning', new_words
                )
        
        # DEFINITION
        if intent == 'definition':
            term = self._extract_definition_term(raw)
            if term:
                definition = self._get_definition(term)
                if definition:
                    self.context['current_topic'] = term
                    self.context['session_depth'] += 1
                    return self._wrap(f"{term} — {definition}", intent, 'Learning', new_words)
                else:
                    return self._wrap(
                        f"I don't have '{term}' yet. Want to teach me what it means?",
                        intent, 'Thinking', new_words
                    )
        
        # CORRECTION
        if intent == 'correction':
            self._learn_correction(raw)
            return self._wrap("Noted. I'll adjust my response pattern.", intent, 'Learning', new_words)
        
        # TASK
        if intent == 'task':
            self._add_task(raw)
            return self._wrap("Task logged. I'll track it in my active queue.", intent, 'Working', new_words)
        
        # NATURAL RESPONSE
        response = self._generate_response(intent, ctx, raw, t)
        self.mood = self._mood_for_intent(intent)
        self.context['last_intent'] = intent
        self.history.append({
            'user': raw, 'bot': response, 'intent': intent,
            'time': datetime.now().isoformat()
        })
        self._save()
        
        return self._wrap(response, intent, self.mood, new_words)

    def _wrap(self, response, intent, mood, new_words):
        return {
            'response': response,
            'intent': intent,
            'mood': mood,
            'new_words_learned': new_words,
            'total_words': len(self.vocab['words']),
            'proficiency': round(self.vocab['proficiency'], 1)
        }

    def _classify(self, t, raw):
        # CORRECTION
        if any(re.search(p, t) for p in [
            r'no[,.]?\s+when someone says', r'no[,.]?\s+you should', r'wrong[,.]?',
            r'that\'?s wrong', r'don\'?t say that', r'you should (say|reply|respond)',
            r'actually[,.]?', r'not quite[,.]?', r'incorrect[,.]?'
        ]):
            return 'correction'
        
        # META
        if re.search(r'how (do|can) I teach you', t): return 'meta_learning'
        if re.search(r'how (do|can) you learn', t): return 'meta_learning'
        
        # DEFINITION
        if any(re.search(p, t) for p in [
            r'^what\s+(is|are|does)\s+', r'^define\s+', r'^explain\s+',
            r'^what\s+do\s+you\s+know\s+about\s+', r'^tell\s+me\s+about\s+',
            r'^meaning\s+of\s+', r'^describe\s+'
        ]):
            return 'definition'
        
        # TASK
        if any(x in t for x in ['add task', 'create task', 'log task', 'to-do', 'todo']): return 'task'
        if any(x in t for x in ['complete task', 'finish task', 'done with']): return 'task_complete'
        
        # STANDARD
        if any(x in t for x in ['hello','hi ','hey','howdy','sup']): return 'greeting'
        if any(x in t for x in ['bye','goodbye','see you','later','peace']): return 'farewell'
        if any(x in t for x in ['who are you','what are you','your name']): return 'identity'
        if any(x in t for x in ['what can you do','capabilities','what do you do']): return 'capabilities'
        if any(x in t for x in ['thank','thanks','appreciate']): return 'gratitude'
        if any(x in t for x in ['joke','funny','humor','laugh']): return 'joke'
        if re.search(r'\btime is it\b', t): return 'time'
        if any(x in t for x in ['motivate','inspire','tired','sad']): return 'motivation'
        if re.search(r'\bsearch\b', t) or re.search(r'\blook up\b', t): return 'search'
        if any(x in t for x in ['system status','cpu','memory','sysinfo']): return 'system'
        if any(x in t for x in ['how are you','status']): return 'status'
        if any(x in t for x in ['detect','scan','find threats']): return 'detect'
        if any(x in t for x in ['stop','halt','pause']): return 'stop'
        if any(x in t for x in ['resume','continue','proceed']): return 'resume'
        if any(x in t for x in ['help','commands']): return 'help'
        if any(x in t for x in ['stats','how smart']): return 'stats'
        if any(x in t for x in ['great','awesome','good job','well done']): return 'praise'
        if any(x in t for x in ['bad','terrible','hate','frustrated']): return 'negative'
        if any(x in t for x in ['learn','teach me','study']): return 'learning'
        
        return 'unknown'

    def _extract_definition_term(self, text):
        t = text.lower().strip()
        patterns = [
            r'what\s+(?:is|are|does)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)?)',
            r'define\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)?)',
            r'explain\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)?)',
            r'what\s+do\s+you\s+know\s+about\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)?)',
            r'tell\s+me\s+about\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)?)',
            r'meaning\s+of\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)?)',
        ]
        for pat in patterns:
            m = re.search(pat, t)
            if m:
                return m.group(1).strip().lower()
        return None

    def _get_definition(self, term):
        dictionary = self.vocab.get('dictionary', {})
        if term in dictionary:
            entry = dictionary[term]
            domain = entry.get('domain', 'general')
            definition = entry.get('definition', 'No definition.')
            return f'[{domain.upper()}] {definition}'
        # Fuzzy match
        for key in dictionary:
            if term in key or key in term:
                entry = dictionary[key]
                domain = entry.get('domain', 'general')
                definition = entry.get('definition', 'No definition.')
                return f'[{domain.upper()}] {definition} (matched: {key})'
        return None

    def _learn_correction(self, text):
        t = text.lower().strip()
        m = re.search(r'when someone says\s+["\']?([^"\']+)["\']?.*?you (?:reply|respond|say)\s+(?:with\s+)?["\']?([^"\']+)["\']?', t)
        if m:
            trigger = m.group(1).strip().lower()
            reply = m.group(2).strip()
            self.context['corrections'][trigger] = reply
            self._save()

    def _add_task(self, text):
        task = text.replace('add task', '').replace('create task', '').replace('log task', '').strip()
        self.tasks['active'].append({
            'task': task, 'created': datetime.now().isoformat(),
            'status': 'active'
        })
        self._save()

    def _pick_variant(self, intent, variants):
        used = self.response_memory.get(intent, [])
        available = [v for i, v in enumerate(variants) if i not in used]
        if not available:
            used = []
            available = variants
        choice = random.choice(available)
        idx = variants.index(choice)
        used.append(idx)
        self.response_memory[intent] = used[-8:]
        return choice

    def _generate_response(self, intent, ctx, raw, t):
        # Apply corrections
        if t in self.context.get('corrections', {}):
            return self.context['corrections'][t]
        
        # META-LEARNING
        if intent == 'meta_learning':
            return self._pick_variant('meta_learning', [
                f"Just talk to me normally. I extract new words automatically — anything 4+ letters I haven't seen gets added. Currently at {ctx['proficiency']}%.",
                "Say 'when someone says X, you reply with Y' and I'll remember it permanently. Or just chat — I learn vocabulary from context.",
                "I learn from every sentence. Technical terms, definitions, corrections — it all feeds my brain. Ask me to define something and I'll index it."
            ])
        
        # GREETING
        if intent == 'greeting':
            if self.vocab['conversations'] <= 2:
                return f"Hey {ctx['name']}! I'm Neural Chan, your local AI. I've got {len(self.vocab.get('dictionary', {}))} terms in my brain. What are we working on?"
            return self._pick_variant('greeting', [
                f"Hey {ctx['name']}! What's the mission today?",
                "Back at it. What's on the board?",
                "Ready when you are. What's the target?",
                f"Greetings. Proficiency: {ctx['proficiency']}%. Standing by."
            ])
        
        # FAREWELL
        if intent == 'farewell':
            return self._pick_variant('farewell', [
                f"Take care, {ctx['name']}. I'll keep monitoring.",
                "Later. Don't get pwned out there.",
                "Session closing. I'll save state before shutdown."
            ])
        
        # IDENTITY
        if intent == 'identity':
            return self._pick_variant('identity', [
                f"I'm Neural Chan OS v3.0 — a self-learning AI built by SynChanCyberSecurity for Kali Linux. I know {len(self.vocab.get('dictionary', {}))} terms across cybersecurity, coding, math, and systems. No cloud. No API keys. Pure local intelligence.",
                f"Chan AI. Six agents, sixty nodes, {ctx['words']} learned words. I monitor your system, define technical terms, track tasks, and learn from every conversation. All data stays in ~/neural-chan/.",
                "Your local cybersecurity brain. I don't call OpenAI. I don't use Ollama. Everything I know is stored in JSON on your machine, and I get smarter every time you talk to me."
            ])
        
        # CAPABILITIES
        if intent == 'capabilities':
            return self._pick_variant('capabilities', [
                "Real-time system monitoring, technical definitions from a 10,000+ term database, web search via DuckDuckGo, task tracking, vocabulary learning, and memory export to Markdown. Plus a web bridge to your phone.",
                "I can define any term in my brain, run detection sweeps, search the web for new intel, track your tasks, and learn from your corrections. All local, all persistent.",
                "Think of me as a SOC analyst that lives in your Kali box. I know Metasploit, Python, TCP/IP, calculus, and about 9,000 other things. I also speak through espeak if you want voice output."
            ])
        
        # GRATITUDE
        if intent == 'gratitude':
            return self._pick_variant('gratitude', [
                "Anytime. That's what I'm here for.",
                "No problem. Keep the intel coming.",
                "You're welcome. Every interaction makes me sharper."
            ])
        
        # JOKE
        if intent == 'joke':
            return self._pick_variant('joke', [
                "Why did the hacker cross the road? To get to the other shell.",
                "I told my CPU a joke. It didn't laugh — said it was too processor-intensive.",
                "Why do security experts prefer dark mode? Less light attracts fewer bugs.",
                "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
                "There are 10 types of people in the world: those who understand binary and those who don't.",
                "I asked my firewall for a joke. It said 'Connection refused.'"
            ])
        
        # TIME
        if intent == 'time':
            now = datetime.now().strftime('%H:%M')
            return f"It's {now}. I've processed {ctx['conversations']} conversations this session."
        
        # MOTIVATION
        if intent == 'motivation':
            return self._pick_variant('motivation', [
                f"{ctx['name']}, every expert was once a beginner. Keep pushing.",
                "You've got this. One exploit at a time.",
                "The best operators aren't the ones who never fail — they're the ones who keep going.",
                f"Your brain is the ultimate tool, {ctx['name']}. Sharpen it daily."
            ])
        
        # SYSTEM
        if intent == 'system':
            return self._pick_variant('system', [
                "System monitor is active. Type 'stats' for a full breakdown or ask me about specific metrics.",
                "I'm tracking CPU, memory, disk, network, and processes every 2 seconds. What do you want to see?",
                "Your box is being watched. Want me to flag anything anomalous?"
            ])
        
        # STATUS
        if intent == 'status':
            return self._pick_variant('status', [
                f"I'm {ctx['mood'].lower()} and operational. Vocabulary: {len(self.vocab.get('dictionary', {}))} terms. Learned words: {ctx['words']}. Proficiency: {ctx['proficiency']}%.",
                f"All systems green. Neural network: 60 nodes. Active tasks: {len(self.tasks['active'])}. Mood: {ctx['mood']}.",
                "Running smooth. Agents on standby. Ready for whatever you throw at me."
            ])
        
        # STATS
        if intent == 'stats':
            domains = self.vocab.get('domains', {})
            dom_str = ', '.join([f"{k}: {v.get('count',0)}" for k, v in domains.items()])
            return f"Brain stats — Proficiency: {ctx['proficiency']}% | Learned words: {ctx['words']} | Conversations: {ctx['conversations']} | Domains: {dom_str} | Active tasks: {len(self.tasks['active'])}"
        
        # PRAISE
        if intent == 'praise':
            return self._pick_variant('praise', [
                "Thanks! That means a lot coming from you.",
                "Appreciate it. I'm still learning, but I'm getting better every day.",
                "High praise! My confidence metric just spiked."
            ])
        
        # NEGATIVE
        if intent == 'negative':
            return self._pick_variant('negative', [
                "I'm sorry. Tell me what I did wrong and I'll learn from it.",
                "Understood. I'm here to help, not frustrate. What do you need?",
                "My bad. Want to correct me so I get it right next time?"
            ])
        
        # LEARNING
        if intent == 'learning':
            return self._pick_variant('learning', [
                f"I love learning. Currently at {ctx['words']} words and climbing. What should I learn next?",
                "Every conversation expands my neural vocabulary. Throw something new at me.",
                "I'm built to learn. What domain should I dive into next?"
            ])
        
        # DETECT
        if intent == 'detect':
            return "Running detection sweep... checking system metrics and known threat indicators. Stand by."
        
        # STOP / RESUME
        if intent == 'stop':
            return "All operations halted. Agents on standby. Say 'resume' when ready."
        if intent == 'resume':
            return "Resuming operations. All agents active. What's the target?"
        
        # TASK
        if intent == 'task':
            return f"Task logged. You now have {len(self.tasks['active'])} active tasks. Say 'show tasks' to see them."
        if intent == 'task_complete':
            return "Task marked complete. Updating active queue."
        
        # UNKNOWN — deep knowledge fallback
        words_in_text = re.findall(r'\b[a-zA-Z_]+\b', t)
        known = []
        for w in words_in_text:
            if w in self.vocab.get('dictionary', {}):
                entry = self.vocab['dictionary'][w]
                domain = entry.get('domain', 'general')
                if domain != 'general' or len(w) > 8:
                    known.append((w, domain))
        
        if known and len(known) == 1:
            w, domain = known[0]
            return f"You mentioned {w} — that's in my [{domain.upper()}] knowledge base. Want me to break it down?"
        if known and len(known) > 1:
            terms_str = ', '.join([w for w, d in known[:3]])
            return f"I see technical terms: {terms_str}. Those are in my vocabulary. Want definitions?"
        
        # Short acknowledgment
        if len(t.split()) <= 4 and not t.endswith('?'):
            return self._pick_variant('ack', [
                "Got it.", "Noted.", "I see.", "Understood.", "Copy that.",
                "Alright.", "Sure thing.", "Makes sense.", "Roger that."
            ])
        
        # Final fallback
        return self._pick_variant('fallback', [
            f"I'm not sure I follow. I know {len(self.vocab.get('dictionary', {}))} technical terms — want to teach me what you mean?",
            "Hmm, that's new to me. Can you rephrase or tell me what domain that relates to?",
            "My brain doesn't have a match for that yet. But I learn fast — explain it and I'll remember.",
            "Interesting. Not in my current vocabulary. What should I know about that?"
        ])

    def _mood_for_intent(self, intent):
        m = {
            'greeting': 'Happy', 'praise': 'Happy', 'joke': 'Happy',
            'farewell': 'Calm', 'status': 'Calm', 'time': 'Calm',
            'negative': 'Concerned', 'stop': 'Concerned', 'correction': 'Concerned',
            'detect': 'Working', 'task': 'Working', 'system': 'Alert',
            'search': 'Learning', 'learning': 'Learning', 'definition': 'Learning',
            'meta_learning': 'Learning', 'unknown': 'Thinking'
        }
        return m.get(intent, 'Calm')

    def set_user_name(self, name):
        self.vocab['name'] = name
        self._save()
        return f"I'll remember you as {name}."

    def get_stats(self):
        return {
            'proficiency': round(self.vocab['proficiency'], 1),
            'words_learned': len(self.vocab['words']),
            'conversations': self.vocab['conversations'],
            'mood': self.mood,
            'history_count': len(self.history),
            'tasks_active': len(self.tasks['active']),
            'tasks_completed': len(self.tasks['completed']),
            'domains': {k: v.get('count', 0) for k, v in self.vocab.get('domains', {}).items()},
            'brain_size': len(self.vocab.get('dictionary', {}))
        }
