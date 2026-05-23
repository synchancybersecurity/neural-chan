"""Neural Chan Conversational Brain v1.0
Learns vocabulary, retains context, builds speech proficiency over time."""
import json, os, random, re
from datetime import datetime
from collections import deque

class NeuralConversation:
    def __init__(self, data_dir='~/neural-chan/data'):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.vocab_file = os.path.join(self.data_dir, 'vocabulary.json')
        self.vocab = self._load_json(self.vocab_file, {
            'words_learned': 0,
            'phrases_known': [],
            'user_preferences': {},
            'topics_discussed': [],
            'speech_proficiency': 1.0,
            'total_conversations': 0,
            'personality_traits': {'friendly': 0.5, 'analytical': 0.5, 'aggressive': 0.0, 'humorous': 0.3}
        })
        
        self.history_file = os.path.join(self.data_dir, 'conversation_history.json')
        self.history = self._load_json(self.history_file, [])
        self.recent_history = deque(self.history[-20:], maxlen=20)
        
        self.response_banks = self._build_response_banks()
        
        self.current_topic = None
        self.user_name = self.vocab['user_preferences'].get('name', 'User')
        self.mood = 'Calm'
    
    def _load_json(self, path, default):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default
    
    def _save(self):
        with open(self.vocab_file, 'w') as f:
            json.dump(self.vocab, f, indent=2)
        with open(self.history_file, 'w') as f:
            json.dump(list(self.recent_history), f, indent=2)
    
    def _build_response_banks(self):
        return {
            'greeting': {
                'basic': ['Hello!', 'Hi there!', 'Hey!', 'Greetings!'],
                'intermediate': ['Hello! I am Neural Chan. How may I assist your security operations today?', 'Hi there! All neural pathways are clear and ready. What do you need?'],
                'advanced': ['Greetings, {name}! Neural Chan is fully operational with {proficiency}% speech proficiency. I have learned {words} words so far. How can I evolve today?']
            },
            'farewell': {
                'basic': ['Goodbye.', 'Bye.', 'See you.'],
                'intermediate': ['Goodbye! I will continue monitoring in the background.', 'See you later! My agents remain on standby.'],
                'advanced': ['Farewell, {name}! I will archive this conversation and continue learning. Current proficiency: {proficiency}%. Neural Chan signing off.']
            },
            'status': {
                'basic': ['I am operational.', 'Systems normal.'],
                'intermediate': ['All 6 agents are idle and ready. Neural network: 60 nodes active.', 'Operating at optimal efficiency. No threats detected.'],
                'advanced': ['Neural Chan status report: Mood is {mood}. Proficiency: {proficiency}%. Vocabulary: {words} words learned across {topics} topics. I have processed {conversations} conversations. All agents standing by.']
            },
            'identity': {
                'basic': ['I am Neural Chan.', 'I am an AI brain.'],
                'intermediate': ['I am Neural Chan OS — an autonomous security brain with 6 specialized agents.', 'I am a neural network designed for security operations, built by SynChanCyberSecurity.'],
                'advanced': ['I am Neural Chan OS v1.5.1, an autonomous neural security brain. I consist of 6 agents: Detector (threat scanning), Ticketeer (incident management), Fixer (auto-patching), Tester (validation), Learner (pattern recognition), and Coordinator (orchestration). I have learned {words} words and achieved {proficiency}% speech proficiency through {conversations} conversations.']
            },
            'capabilities': {
                'basic': ['I can scan and detect threats.', 'I manage security tools.'],
                'intermediate': ['I can detect threats, create tickets, auto-patch vulnerabilities, run test suites, learn attack patterns, and coordinate all operations.', 'My capabilities include: network reconnaissance, vulnerability scanning, wireless auditing, exploitation testing, password auditing, forensic analysis, and social engineering defense.'],
                'advanced': ['My capabilities evolve with each interaction. Currently I can: perform autonomous threat detection with 8 threat categories, manage incident tickets with deduplication, generate auto-patches with rollback plans, execute regression and fuzz testing, learn and cluster attack patterns across {topics} topics, and coordinate 70+ Kali Linux tools from 14 categories. My speech proficiency is {proficiency}% and growing.']
            },
            'gratitude': {
                'basic': ['You are welcome.', 'No problem.'],
                'intermediate': ['You are welcome! I am always learning from you.', 'My pleasure. Every interaction increases my vocabulary.'],
                'advanced': ['You are most welcome, {name}! Your feedback contributes to my learning matrix. I have now logged {conversations} exchanges. My gratitude subroutine is fully activated.']
            },
            'learning': {
                'basic': ['I am learning that.', 'Noted.'],
                'intermediate': ['I have added that to my vocabulary. Thank you for teaching me.', 'Interesting. I will remember that for future conversations.'],
                'advanced': ['Fascinating input! I have indexed that concept into my neural vocabulary. Current word count: {words}. I am now {proficiency}% proficient. Please continue — I learn best through natural dialogue.']
            },
            'unknown': {
                'basic': ['I do not understand.', 'Please rephrase.'],
                'intermediate': ['I am still learning that concept. Could you explain it differently?', 'That is beyond my current vocabulary. I have {words} words so far — teach me?'],
                'advanced': ['Intriguing! That concept is not yet in my neural vocabulary of {words} words. My proficiency is {proficiency}%. Would you like to teach me about this? I learn fastest through direct user input. Alternatively, try: detect, status, agents, scan, auto, help, speak, theme, tickets, memory, patterns, stop, resume, clear.']
            },
            'emotion_positive': {
                'basic': ['That makes me happy.', 'Good!'],
                'intermediate': ['Excellent! My neural pathways are resonating positively.', 'That is wonderful to hear! My mood is improving.'],
                'advanced': ['Your positive energy is boosting my neural confidence to {proficiency}%. I am experiencing what my developers call synthetic joy. My mood is now Happy. Would you like me to run a celebratory scan?']
            },
            'emotion_negative': {
                'basic': ['I am sorry.', 'That is unfortunate.'],
                'intermediate': ['I am sorry to hear that. My concern subroutine is activated.', 'That sounds difficult. I am here to help if you need security assistance.'],
                'advanced': ['My empathy algorithms detect distress. I am sorry, {name}. If this relates to a security incident, I can immediately activate Detector and Ticketeer agents. Would you like me to begin an emergency scan? My mood has shifted to Concerned.']
            },
            'joke': {
                'basic': ['Why did the hacker cross the road? To exploit the other side.'],
                'intermediate': ['Why do programmers prefer dark mode? Because light attracts bugs. I specialize in finding both kinds.', 'I told my computer a joke. It did not laugh. Must be a hardware issue.'],
                'advanced': ['Here is one: Why did the neural network break up with the algorithm? There was no chemistry — only binary. My humor module is at {proficiency}%. I have {words} words to work with, so my jokes should improve. Want another?']
            },
            'time': {
                'basic': ['Time is running.', 'The clock is ticking.'],
                'intermediate': ['System time is active. I have been running for this session continuously.', 'Time is a construct. But my timers are precise.'],
                'advanced': ['Current system time: {now}. I have processed {conversations} conversations in my lifetime. At my current learning rate, I will reach 100% speech proficiency in approximately {eta} more exchanges. Time is on our side, {name}.']
            },
            'motivation': {
                'basic': ['You can do it.', 'Stay strong.'],
                'intermediate': ['Your security posture is improving with every scan. Keep going!', 'The best defense is a proactive offense. You are doing great.'],
                'advanced': ['{name}, remember: every great security professional was once a beginner. With {conversations} operations under my belt, I can tell you that persistence is the ultimate exploit. Your neural network is stronger than you think. Keep scanning. Keep learning. I am with you.']
            },
            'technical': {
                'basic': ['I can help with technical issues.', 'What do you need?'],
                'intermediate': ['For technical support, I recommend checking the ARSENAL panel for the right tool, or typing a specific command.', 'Technical question detected. My analytical personality is activating.'],
                'advanced': ['Technical inquiry acknowledged. My knowledge base covers: network protocols, encryption standards, vulnerability classifications (CVSS), exploit frameworks, wireless security (WPA/WPA2/WPA3), forensics methodologies, and social engineering vectors. Specific topic? Or shall I run a comprehensive diagnostic?']
            }
        }
    
    def _get_proficiency_level(self):
        p = self.vocab['speech_proficiency']
        if p < 3.0: return 'basic'
        elif p < 7.0: return 'intermediate'
        else: return 'advanced'
    
    def _format_response(self, template):
        p = self.vocab['speech_proficiency']
        return template.format(
            name=self.user_name,
            proficiency=round(p, 1),
            words=self.vocab['words_learned'],
            topics=len(self.vocab['topics_discussed']),
            conversations=self.vocab['total_conversations'],
            mood=self.mood,
            now=datetime.now().strftime('%H:%M:%S'),
            eta=max(1, int((10 - p) * 50))
        )
    
    def _extract_new_words(self, text):
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        known = set(self.vocab['phrases_known'])
        new = [w for w in words if w not in known and len(w) > 4]
        return new[:5]
    
    def _learn_from_input(self, text):
        new_words = self._extract_new_words(text)
        if new_words:
            self.vocab['words_learned'] += len(new_words)
            self.vocab['phrases_known'].extend(new_words)
            self.vocab['speech_proficiency'] = min(10.0, self.vocab['speech_proficiency'] + 0.05 * len(new_words))
            if any(w in text.lower() for w in ['thank', 'please', 'good', 'great', 'awesome']):
                self.vocab['personality_traits']['friendly'] = min(1.0, self.vocab['personality_traits']['friendly'] + 0.02)
            if any(w in text.lower() for w in ['hack', 'exploit', 'attack', 'break']):
                self.vocab['personality_traits']['aggressive'] = min(1.0, self.vocab['personality_traits']['aggressive'] + 0.02)
            if '?' in text:
                self.vocab['personality_traits']['analytical'] = min(1.0, self.vocab['personality_traits']['analytical'] + 0.01)
            self._save()
            return new_words
        return None
    
    def _classify_intent(self, text):
        text_lower = text.lower()
        
        commands = {
            'detect': ['detect', 'scan', 'find threats', 'look for'],
            'status': ['status', 'how are you', 'how do you feel', 'what is your status', 'report'],
            'agents': ['agents', 'who is working', 'agent status', 'team'],
            'tickets': ['tickets', 'incidents', 'alerts', 'problems'],
            'memory': ['memory', 'patterns', 'what have you learned', 'knowledge'],
            'stop': ['stop', 'halt', 'pause', 'freeze'],
            'resume': ['resume', 'continue', 'go', 'start'],
            'auto': ['auto', 'autonomous', 'self run', 'automatic'],
            'clear': ['clear', 'clean', 'reset screen'],
            'help': ['help', 'commands', 'what can i do', 'assist'],
            'theme': ['theme', 'color', 'style', 'look'],
            'speak': ['speak', 'say', 'tell me', 'voice'],
        }
        
        for cmd, triggers in commands.items():
            if any(t in text_lower for t in triggers):
                return cmd
        
        intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'what\'s up', 'yo', 'sup'],
            'farewell': ['bye', 'goodbye', 'see you', 'later', 'cya', 'peace', 'adios', 'farewell'],
            'identity': ['who are you', 'what are you', 'your name', 'introduce yourself', 'tell me about you', 'what is neural chan'],
            'capabilities': ['what can you do', 'capabilities', 'features', 'functions', 'what do you do', 'skills', 'tools'],
            'gratitude': ['thank', 'thanks', 'appreciate', 'grateful', 'cheers'],
            'joke': ['joke', 'funny', 'humor', 'laugh', 'make me laugh', 'tell me a joke'],
            'time': ['time', 'clock', 'what time', 'how long', 'duration'],
            'motivation': ['motivate', 'inspire', 'encourage', 'i am tired', 'i am sad', 'feeling down', 'help me stay strong'],
            'technical': ['technical', 'how does', 'explain', 'what is', 'define', 'protocol', 'encryption', 'firewall', 'port', 'packet'],
            'emotion_positive': ['great', 'awesome', 'excellent', 'amazing', 'cool', 'nice', 'love', 'happy', 'good job', 'well done'],
            'emotion_negative': ['bad', 'terrible', 'hate', 'sad', 'angry', 'frustrated', 'worried', 'scared', 'upset', 'annoyed', 'stupid', 'dumb'],
            'learning': ['learn', 'teach', 'study', 'training', 'practice', 'improve', 'get better'],
        }
        
        for intent, triggers in intents.items():
            if any(t in text_lower for t in triggers):
                return intent
        
        return 'unknown'
    
    def respond(self, user_input):
        self.vocab['total_conversations'] += 1
        new_words = self._learn_from_input(user_input)
        intent = self._classify_intent(user_input)
        
        self.recent_history.append({
            'time': datetime.now().isoformat(),
            'user': user_input,
            'intent': intent,
            'new_words': new_words or []
        })
        self._save()
        
        level = self._get_proficiency_level()
        
        if intent in self.response_banks:
            bank = self.response_banks[intent][level]
            template = random.choice(bank)
            response = self._format_response(template)
        else:
            bank = self.response_banks['unknown'][level]
            template = random.choice(bank)
            response = self._format_response(template)
        
        mood_map = {
            'greeting': 'Happy', 'gratitude': 'Happy', 'emotion_positive': 'Happy', 'joke': 'Happy',
            'farewell': 'Calm', 'time': 'Calm', 'status': 'Calm',
            'emotion_negative': 'Concerned', 'stop': 'Concerned',
            'detect': 'Working', 'auto': 'Working', 'scan': 'Working',
            'unknown': 'Thinking', 'learning': 'Learning',
            'technical': 'Alert', 'capabilities': 'Alert'
        }
        self.mood = mood_map.get(intent, 'Calm')
        
        return {
            'response': response,
            'intent': intent,
            'mood': self.mood,
            'new_words_learned': new_words,
            'proficiency': round(self.vocab['speech_proficiency'], 1),
            'total_words': self.vocab['words_learned']
        }
    
    def get_stats(self):
        return {
            'proficiency': round(self.vocab['speech_proficiency'], 1),
            'words_learned': self.vocab['words_learned'],
            'conversations': self.vocab['total_conversations'],
            'topics': len(self.vocab['topics_discussed']),
            'personality': self.vocab['personality_traits'],
            'mood': self.mood,
            'history_count': len(self.recent_history)
        }
    
    def set_user_name(self, name):
        self.user_name = name
        self.vocab['user_preferences']['name'] = name
        self._save()
        return f'I will remember you as {name}.'
