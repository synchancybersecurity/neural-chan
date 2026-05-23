import sys, os, re

with open('neural_conversation_v2.py', 'r') as f:
    code = f.read()

# Replace the old respond() method with a domain-aware version
old_respond = '''    def respond(self, text):
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
                    'new_words_learned': [], 'total_words': 0, 'proficiency': 0}'''

new_respond = '''    def respond(self, text):
        try:
            self.vocab['conversations'] += 1
            new_words = [w for w in re.findall(r'\\b[a-zA-Z]{4,}\\b', text.lower())
                        if w not in self.vocab['words'] and len(w) > 4][:5]
            if new_words:
                self.vocab['words'].extend(new_words)
                self.vocab['proficiency'] = min(100.0, self.vocab['proficiency'] + 0.1 * len(new_words))
                self._save()

            intent = self._classify(text)
            ctx = {
                'name': self.vocab.get('name', 'User'),
                'proficiency': round(self.vocab['proficiency'], 1),
                'words': len(self.vocab['words']),
                'conversations': self.vocab['conversations'],
                'mood': self.mood
            }

            # Domain-aware lookup — if user mentions a known technical term, define it
            domain_response = self._lookup_domain_term(text)
            if domain_response:
                self.mood = 'Learning'
                self.history.append({'user': text, 'bot': domain_response, 'intent': 'definition', 'time': datetime.now().isoformat()})
                self._save()
                return {'response': domain_response, 'intent': 'definition', 'mood': 'Learning',
                        'new_words_learned': new_words, 'total_words': len(self.vocab['words']), 'proficiency': ctx['proficiency']}

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
                    'new_words_learned': [], 'total_words': 0, 'proficiency': 0}'''

code = code.replace(old_respond, new_respond)

# Add the _lookup_domain_term method after _mood_for_intent
old_mood = '''    def _mood_for_intent(self, intent):
        m = {
            'greeting': 'Happy', 'praise': 'Happy', 'joke': 'Happy',
            'farewell': 'Calm', 'status': 'Calm', 'time': 'Calm',
            'negative': 'Concerned', 'stop': 'Concerned',
            'detect': 'Working', 'auto': 'Working', 'system': 'Alert',
            'search': 'Learning', 'learning': 'Learning', 'unknown': 'Thinking'
        }
        return m.get(intent, 'Calm')'''

new_mood = '''    def _mood_for_intent(self, intent):
        m = {
            'greeting': 'Happy', 'praise': 'Happy', 'joke': 'Happy',
            'farewell': 'Calm', 'status': 'Calm', 'time': 'Calm',
            'negative': 'Concerned', 'stop': 'Concerned',
            'detect': 'Working', 'auto': 'Working', 'system': 'Alert',
            'search': 'Learning', 'learning': 'Learning', 'unknown': 'Thinking'
        }
        return m.get(intent, 'Calm')

    def _lookup_domain_term(self, text):
        """Look up technical terms in the ingested dictionary and return a definition if found."""
        try:
            dict_data = self.vocab.get('dictionary', {})
            words_in_text = re.findall(r'\\b[a-zA-Z_]+\\b', text.lower())
            for w in words_in_text:
                if w in dict_data:
                    entry = dict_data[w]
                    domain = entry.get('domain', 'general')
                    definition = entry.get('definition', 'No definition available.')
                    return f'[{domain.upper()}] {w}: {definition[:200]}'
                # Try matching multi-word keys
                for key in dict_data:
                    if key in text.lower() and len(key) > 3:
                        entry = dict_data[key]
                        domain = entry.get('domain', 'general')
                        definition = entry.get('definition', 'No definition available.')
                        return f'[{domain.upper()}] {key}: {definition[:200]}'
        except Exception as e:
            pass
        return None'''

code = code.replace(old_mood, new_mood)

with open('neural_conversation_v2.py', 'w') as f:
    f.write(code)

print('[✓] neural_conversation_v2.py patched — domain-aware responses')
