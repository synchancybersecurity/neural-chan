import json, os, random, re
from datetime import datetime
from collections import deque

# Common English words that should NEVER trigger dictionary fallback
COMMON_WORDS = {
    'the','a','an','is','are','was','were','be','been','being','have','has','had','do','does','did',
    'will','would','could','should','may','might','must','shall','can','need','dare','ought','used',
    'to','of','in','for','on','with','at','by','from','as','into','through','during','before','after',
    'above','below','between','under','again','further','then','once','here','there','when','where',
    'why','how','all','each','few','more','most','other','some','such','no','nor','not','only','own',
    'same','so','than','too','very','just','and','but','if','or','because','until','while','what','which',
    'who','whom','this','that','these','those','am','it','its','itself','they','them','their','theirs',
    'themselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her',
    'hers','herself','i','me','my','myself','mine','we','us','our','ours','ourselves','about','out',
    'up','down','off','over','under','again','further','then','once','here','there','when','where',
    'why','how','all','each','few','more','most','other','some','such','no','nor','not','only','own',
    'same','so','than','too','very','just','now','also','back','still','even','new','good','bad','big',
    'small','old','young','high','low','long','short','right','left','early','late','first','last','well',
    'better','best','badly','much','many','little','own','old','right','best','next','early','never',
    'always','sometimes','often','usually','really','actually','probably','definitely','certainly',
    'clearly','simply','completely','almost','quite','rather','pretty','enough','already','almost',
    'quite','rather','pretty','enough','already','finally','suddenly','recently','usually','always',
    'teach','learn','study','know','think','say','tell','ask','answer','talk','speak','listen','hear',
    'see','look','watch','read','write','make','take','get','give','come','go','put','set','keep','let',
    'help','show','play','run','walk','move','live','die','eat','drink','sleep','wake','feel','want',
    'like','love','hate','hope','wish','try','use','work','call','turn','open','close','start','stop',
    'end','begin','continue','finish','return','leave','stay','wait','find','lose','win','fail','pay',
    'buy','sell','send','receive','build','break','cut','hit','hold','catch','throw','pull','push',
    'draw','fall','rise','grow','change','follow','lead','pass','meet','join','add','reduce','increase',
    'decrease','create','destroy','kill','save','protect','fight','defend','attack','avoid','escape',
    'choose','decide','agree','refuse','accept','reject','allow','prevent','enable','disable','cause',
    'effect','result','way','thing','time','day','year','work','life','world','year','people','man',
    'woman','child','family','friend','group','part','place','hand','eye','head','face','back','side',
    'water','food','money','number','name','word','line','end','home','house','room','door','car',
    'city','state','country','earth','land','area','space','point','case','fact','idea','question',
    'problem','issue','example','system','program','process','service','device','machine','tool',
    'file','data','information','message','story','news','report','account','level','rate','degree',
    'period','moment','minute','hour','week','month','today','tonight','tomorrow','yesterday','soon',
    'later','ago','before','after','during','within','without','against','among','toward','around',
    'across','behind','beyond','except','including','regarding','concerning','considering','following'
}

class NeuralConversationV2:
    def __init__(self, system_monitor=None, web_learner=None, data_dir='~/neural-chan/data'):
        self.system_monitor = system_monitor
        self.web_learner = web_learner
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.vocab_file = os.path.join(self.data_dir, 'vocabulary_v2.json')
        self.history_file = os.path.join(self.data_dir, 'history_v2.json')
        self.corrections_file = os.path.join(self.data_dir, 'corrections.json')
        self.vocab = self._load_json(self.vocab_file, {
            'words': [], 'proficiency': 1.0, 'conversations': 0,
            'name': 'User', 'personality': {'friendly': 0.5, 'analytical': 0.5},
            'dictionary': {}
        })
        self.history = deque(self._load_json(self.history_file, [])[-50:], maxlen=50)
        self.corrections = self._load_json(self.corrections_file, {})
        self.mood = 'Calm'
        self.last_intent = 'unknown'
        self.context_topic = None
        self.context_depth = 0

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
            with open(self.corrections_file, 'w') as f:
                json.dump(self.corrections, f)
        except:
            pass

    def respond(self, text):
        try:
            self.vocab['conversations'] += 1
            raw_text = text.strip()
            t = raw_text.lower()

            new_words = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', t)
                        if w not in self.vocab['words'] and len(w) > 4][:5]
            if new_words:
                self.vocab['words'].extend(new_words)
                self.vocab['proficiency'] = min(100.0, self.vocab['proficiency'] + 0.1 * len(new_words))
                self._save()

            intent = self._classify(t, raw_text)
            ctx = {
                'name': self.vocab.get('name', 'User'),
                'proficiency': round(self.vocab['proficiency'], 1),
                'words': len(self.vocab['words']),
                'conversations': self.vocab['conversations'],
                'mood': self.mood,
                'topic': self.context_topic or 'general'
            }

            if intent == 'system' and self.system_monitor:
                latest = self.system_monitor.get_latest()
                if latest:
                    return self._wrap(f"Your system is running at {latest.get('cpu_percent',0)}% CPU and {latest.get('mem_percent',0)}% memory. Load: {latest.get('load_1m',0)}. Processes: {latest.get('processes',0)}.", intent, 'Alert', new_words)

            if intent == 'search' and self.web_learner:
                q = raw_text.replace('search','').replace('google','').replace('look up','').strip()
                if q:
                    result = self.web_learner.search_and_learn(q)
                    self.context_topic = q
                    self.context_depth = 1
                    return self._wrap(f"I searched for '{q}'. Here's what I found: {result.get('summary', 'No results')[:400]}", intent, 'Learning', new_words)

            if intent == 'definition':
                term = self._extract_definition_term(raw_text)
                if term:
                    definition = self._get_definition(term)
                    if definition:
                        self.context_topic = term
                        self.context_depth = 1
                        return self._wrap(f"{term} — {definition}", intent, 'Learning', new_words)
                    else:
                        return self._wrap(f"I don't have '{term}' in my vocabulary yet. Want to teach me what it means?", intent, 'Thinking', new_words)

            if intent == 'correction':
                self._learn_correction(raw_text)
                return self._wrap("Got it. I'll adjust how I respond to that from now on.", intent, 'Learning', new_words)

            response = self._generate_natural_response(intent, ctx, raw_text, t)
            self.mood = self._mood_for_intent(intent)
            self.last_intent = intent
            self.history.append({'user': raw_text, 'bot': response, 'intent': intent, 'time': datetime.now().isoformat()})
            self._save()

            return self._wrap(response, intent, self.mood, new_words)

        except Exception as e:
            return self._wrap(f"I'm thinking... (debug: {str(e)[:60]})", 'error', 'Concerned', [])

    def _wrap(self, response, intent, mood, new_words):
        return {
            'response': response,
            'intent': intent,
            'mood': mood,
            'new_words_learned': new_words,
            'total_words': len(self.vocab['words']),
            'proficiency': round(self.vocab['proficiency'], 1)
        }

    def _classify(self, t, raw_text):
        # CORRECTION
        correction_patterns = [
            r'no[,.]?\s+when someone says',
            r'no[,.]?\s+you should',
            r'wrong[,.]?',
            r'that\'?s wrong',
            r'don\'?t say that',
            r'you should (say|reply|respond)',
            r'actually[,.]?',
            r'not quite[,.]?',
            r'incorrect[,.]?',
        ]
        for pat in correction_patterns:
            if re.search(pat, t):
                return 'correction'

        # META-QUESTIONS about learning/teaching the bot
        if re.search(r'how (do|can) I teach you', t):
            return 'meta_learning'
        if re.search(r'how (do|can) you learn', t):
            return 'meta_learning'
        if re.search(r'can I teach you', t):
            return 'meta_learning'
        if re.search(r'how do I add words', t):
            return 'meta_learning'
        if re.search(r'how do you get smarter', t):
            return 'meta_learning'

        # DEFINITION — explicit only
        definition_starters = [
            r'^what\s+(is|are|does)\s+',
            r'^define\s+',
            r'^explain\s+',
            r'^what\s+do\s+you\s+know\s+about\s+',
            r'^tell\s+me\s+about\s+',
            r'^meaning\s+of\s+',
            r'^describe\s+',
        ]
        for pat in definition_starters:
            if re.search(pat, t):
                return 'definition'

        # STANDARD INTENTS
        if any(x in t for x in ['hello','hi ','hey','howdy','sup','greetings']): return 'greeting'
        if any(x in t for x in ['bye','goodbye','see you','later','peace','cya','night']): return 'farewell'
        if any(x in t for x in ['who are you','what are you','your name','introduce yourself']): return 'identity'
        if any(x in t for x in ['what can you do','what do you do','capabilities','what are you good at']): return 'capabilities'
        if any(x in t for x in ['thank','thanks','appreciate','cheers','grateful']): return 'gratitude'
        if any(x in t for x in ['joke','funny','humor','laugh','make me laugh']): return 'joke'
        if re.search(r'\btime is it\b', t) or re.search(r'\bwhat time\b', t): return 'time'
        if any(x in t for x in ['motivate','inspire','encourage','tired','sad','feeling down']): return 'motivation'
        if re.search(r'\bsearch\b', t) or re.search(r'\blook up\b', t): return 'search'
        if any(x in t for x in ['system status','cpu usage','memory usage','sysinfo','how is my system']): return 'system'
        if any(x in t for x in ['how are you','how do you feel','what is your status']): return 'status'
        if any(x in t for x in ['detect','scan','find threats','run scan']): return 'detect'
        if any(x in t for x in ['stop','halt','pause','freeze','shut down']): return 'stop'
        if any(x in t for x in ['resume','continue','go','start','proceed']): return 'resume'
        if any(x in t for x in ['auto mode','automatic','self run','run auto']): return 'auto'
        if any(x in t for x in ['help','commands','what can i type','show commands']): return 'help'
        if any(x in t for x in ['speak','say ','tell me','voice','read this']): return 'speak'
        if any(x in t for x in ['stats','statistics','brain stats','how smart are you']): return 'stats'
        if any(x in t for x in ['export','save memory','dump brain']): return 'export'
        if any(x in t for x in ['great','awesome','excellent','good job','well done','love it','amazing']): return 'praise'
        if any(x in t for x in ['bad','terrible','hate','angry','frustrated','worried','stupid','dumb','suck']): return 'negative'
        if any(x in t for x in ['learn','teach me','study','training','practice','educate']): return 'learning'

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
            r'describe\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s+[a-zA-Z_][a-zA-Z0-9_]*)?)',
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
        for key in dictionary:
            if key == term:
                entry = dictionary[key]
                domain = entry.get('domain', 'general')
                definition = entry.get('definition', 'No definition.')
                return f'[{domain.upper()}] {definition}'
        return None

    def _learn_correction(self, text):
        t = text.lower().strip()
        m = re.search(r'when someone says\s+["\']?([^"\']+)["\']?.*?you (?:reply|respond|say)\s+(?:with\s+)?["\']?([^"\']+)["\']?', t)
        if m:
            trigger = m.group(1).strip().lower()
            reply = m.group(2).strip()
            self.corrections[trigger] = reply
            self._save()
            return
        m = re.search(r'when someone says\s+["\']?([^"\']+)["\']?.*?you should\s+["\']?([^"\']+)["\']?', t)
        if m:
            trigger = m.group(1).strip().lower()
            reply = m.group(2).strip()
            self.corrections[trigger] = reply
            self._save()

    def _generate_natural_response(self, intent, ctx, raw_text, t):
        if t in self.corrections:
            return self.corrections[t]

        recent = list(self.history)[-3:]
        last_intent = recent[-1]['intent'] if recent else 'unknown'

        # META-LEARNING: how to teach the bot
        if intent == 'meta_learning':
            return random.choice([
                "Easy. Just talk to me. I learn new words from every sentence you type — anything 4+ letters that I haven't seen before gets added to my vocabulary.",
                "Two ways: one, just chat normally. I automatically extract new words. Two, say 'when someone says X, you reply with Y' and I'll remember that pattern.",
                "I learn by listening. Type naturally, and I pick up new terms. My proficiency goes up 0.1% per new word. Currently at " + str(ctx['proficiency']) + "%.",
                "Feed me technical terms, ask me to define things, correct me when I'm wrong. Every interaction trains my brain. I save everything to ~/neural-chan/data/."
            ])

        if intent == 'greeting':
            if self.vocab['conversations'] == 1:
                return f"Hey {ctx['name']}! I'm Neural Chan. Ask me about security, coding, math, or just say hi."
            if last_intent == 'greeting':
                return random.choice([
                    "Hey again! What's on your mind?",
                    "Back for more? I'm ready.",
                    "Hello hello. What are we tackling today?"
                ])
            return random.choice([
                f"Hey {ctx['name']}! What's up?",
                "Hi there. What do you need?",
                "Hello! Ready when you are.",
                f"Greetings, {ctx['name']}. System is green."
            ])

        if intent == 'farewell':
            return random.choice([
                f"Take care, {ctx['name']}. I'll keep an eye on the system.",
                "Later! Ping me if anything looks weird.",
                "Goodbye. Stay sharp out there."
            ])

        if intent == 'identity':
            return random.choice([
                "I'm Neural Chan OS v2.5 — a self-learning AI brain built for Kali Linux. I know 1,900+ terms across math, coding, cybersecurity, and Linux internals. I monitor your system, learn from you, and I don't need the cloud to work.",
                "Neural Chan. Six agents, sixty nodes, one brain. Built by SynChanCyberSecurity. I run entirely on your machine — no API keys, no subscriptions.",
                f"I'm your local AI assistant with {ctx['words']} words in my vocabulary and {ctx['proficiency']}% proficiency. I live in ~/neural-chan/ and I learn from every conversation."
            ])

        if intent == 'capabilities':
            return random.choice([
                "I can monitor your system in real time, define technical terms, search the web via DuckDuckGo, learn new vocabulary from your input, and export everything to Markdown. I also have a web bridge so you can access me from your phone.",
                "System monitoring, threat detection, vocabulary learning, web search, and memory export. Plus I look cool doing it.",
                "Think of me as a technical assistant that actually understands Kali Linux. I know nmap, metasploit, python, calculus, and about 1,900 other things."
            ])

        if intent == 'gratitude':
            return random.choice([
                "Anytime. That's what I'm here for.",
                "No problem. Keep the questions coming.",
                "You're welcome! Every chat makes me smarter."
            ])

        if intent == 'joke':
            jokes = [
                "Why did the hacker cross the road? To get to the other shell.",
                "I told my CPU a joke. It didn't laugh — said it was too processor-intensive.",
                "Why do security experts prefer dark mode? Less light attracts fewer bugs.",
                "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
                "There are 10 types of people in the world: those who understand binary and those who don't."
            ]
            return random.choice(jokes)

        if intent == 'time':
            now = datetime.now().strftime('%H:%M')
            return f"It's {now}. I've been awake for {ctx['conversations']} conversations so far."

        if intent == 'motivation':
            return random.choice([
                f"{ctx['name']}, every expert was once a beginner. Keep pushing.",
                "You've got this. One exploit at a time.",
                "The best hackers aren't the ones who never fail — they're the ones who keep going.",
                f"Your brain is the ultimate tool, {ctx['name']}. Sharpen it daily."
            ])

        if intent == 'system':
            return random.choice([
                "System monitor is running. Type 'stats' for a full breakdown, or I can pull live metrics if you want specifics.",
                "I'm tracking CPU, memory, disk, network, and processes every 2 seconds. What metric do you want to see?",
                "Your box is being watched. Want me to flag anything that looks suspicious?"
            ])

        if intent == 'status':
            return random.choice([
                f"I'm {ctx['mood'].lower()} and operational. I've learned {ctx['words']} words across 5 domains. Proficiency: {ctx['proficiency']}%.",
                f"All systems green. Neural network: 60 nodes active. Vocabulary: {ctx['words']} terms. Mood: {ctx['mood']}.",
                "Running smooth. Six agents on standby. Ready for whatever you throw at me."
            ])

        if intent == 'stats':
            domains = self.vocab.get('domains', {})
            dom_str = ', '.join([f"{k}: {v.get('count',0)}" for k, v in domains.items()])
            return f"Brain stats — Proficiency: {ctx['proficiency']}% | Words: {ctx['words']} | Conversations: {ctx['conversations']} | Domains: {dom_str}"

        if intent == 'export':
            return "Type 'export' in the CLI or click the export button. I'll dump vocabulary, history, system metrics, and web knowledge to ~/neural-chan/memory/ as Markdown files."

        if intent == 'praise':
            return random.choice([
                "Thanks! That means a lot coming from you.",
                "Appreciate it. I'm still learning, but I'm getting better every day.",
                "High praise! My confidence metric just spiked."
            ])

        if intent == 'negative':
            return random.choice([
                "I'm sorry. Tell me what I did wrong and I'll learn from it.",
                "Understood. I'm here to help, not frustrate. What do you need?",
                "My bad. Want to correct me so I get it right next time?"
            ])

        if intent == 'learning':
            return random.choice([
                f"I love learning. Currently at {ctx['words']} words and climbing. What should I learn next?",
                "Every conversation expands my neural vocabulary. Throw something new at me.",
                "I'm built to learn. What domain should I dive into next?"
            ])

        if intent == 'detect':
            return "Running detection sweep... checking for anomalies in system metrics and known threat patterns. Stand by."

        if intent == 'stop':
            return "All operations halted. Agents on standby. Say 'resume' when you're ready."
        if intent == 'resume':
            return "Resuming operations. All agents active. What are we working on?"
        if intent == 'auto':
            return "Auto mode toggled. I'll run periodic scans and report anything unusual."

        # UNKNOWN — SMART FALLBACK
        # Only suggest dictionary terms if they're clearly technical (non-general domain, multi-word, or explicitly technical)
        words_in_text = re.findall(r'\b[a-zA-Z_]+\b', t)
        known_technical = []
        for w in words_in_text:
            if w in COMMON_WORDS:
                continue
            if w in self.vocab.get('dictionary', {}):
                entry = self.vocab['dictionary'][w]
                domain = entry.get('domain', 'general')
                # Only suggest if it's a technical domain or multi-word key
                if domain != 'general' or len(w) > 8 or '_' in w:
                    known_technical.append((w, domain))

        if known_technical and len(known_technical) == 1:
            w, domain = known_technical[0]
            return f"You mentioned {w} — that's in my [{domain.upper()}] vocabulary. Want me to explain it, or were you getting at something else?"

        if known_technical and len(known_technical) > 1:
            terms_str = ', '.join([w for w, d in known_technical[:3]])
            return f"I see you mentioned {terms_str}. Those are in my technical vocabulary. Want me to break any of them down?"

        # Short acknowledgment for statements
        if len(t.split()) <= 4 and not t.endswith('?'):
            return random.choice([
                "Got it.", "Noted.", "I see.", "Understood.", "Copy that.",
                "Alright.", "Sure thing.", "Makes sense."
            ])

        # Final fallback
        return random.choice([
            f"I'm not sure I follow. I know {ctx['words']} words — want to teach me what you mean?",
            "Hmm, that's new to me. Can you rephrase or tell me what domain that relates to?",
            "My brain doesn't have a match for that yet. But I learn fast — explain it and I'll remember.",
            "Interesting. Not in my current vocabulary. What should I know about that?"
        ])

    def _mood_for_intent(self, intent):
        m = {
            'greeting': 'Happy', 'praise': 'Happy', 'joke': 'Happy',
            'farewell': 'Calm', 'status': 'Calm', 'time': 'Calm',
            'negative': 'Concerned', 'stop': 'Concerned', 'correction': 'Concerned',
            'detect': 'Working', 'auto': 'Working', 'system': 'Alert',
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
            'corrections': len(self.corrections),
            'domains': {k: v.get('count', 0) for k, v in self.vocab.get('domains', {}).items()}
        }
