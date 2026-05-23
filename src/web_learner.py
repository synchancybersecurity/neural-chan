"""Web Learner — searches the web and caches knowledge for Neural Chan."""
import urllib.request, urllib.parse, re, json, os, html
from datetime import datetime

class WebLearner:
    def __init__(self, data_dir='~/neural-chan/data'):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.knowledge_file = os.path.join(self.data_dir, 'web_knowledge.json')
        self.knowledge = self._load()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _load(self):
        try:
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save(self):
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def _duckduckgo_search(self, query):
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html_text = resp.read().decode('utf-8', errors='ignore')
            
            snippets = []
            for match in re.finditer(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>.*?<<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', html_text, re.DOTALL):
                title = re.sub(r'<[^>]+>', '', match.group(1))
                snippet = re.sub(r'<[^>]+>', '', match.group(2))
                snippets.append({'title': html.unescape(title), 'snippet': html.unescape(snippet)})
            
            if not snippets:
                for match in re.finditer(r'<div[^>]*class="result__snippet"[^>]*>(.*?)</div>', html_text, re.DOTALL):
                    text = re.sub(r'<[^>]+>', '', match.group(1))
                    snippets.append({'title': 'Web Result', 'snippet': html.unescape(text)})
            
            return snippets[:5]
        except Exception as e:
            return [{'title': 'Search Error', 'snippet': f'Could not search: {str(e)}'}]
    
    def search_and_learn(self, query):
        cache_key = query.lower().strip()
        
        if cache_key in self.knowledge:
            self.cache_hits += 1
            entry = self.knowledge[cache_key]
            age = (datetime.now() - datetime.fromisoformat(entry['cached'])).total_seconds()
            if age < 86400:
                return {
                    'query': query,
                    'source': 'cache',
                    'age_hours': round(age / 3600, 1),
                    'results': entry['results'],
                    'summary': entry.get('summary', 'Cached knowledge.')
                }
        
        self.cache_misses += 1
        results = self._duckduckgo_search(query)
        
        summary_parts = []
        for r in results:
            if 'snippet' in r and r['snippet']:
                summary_parts.append(r['snippet'])
        summary = ' '.join(summary_parts[:3])[:500] if summary_parts else 'No summary available.'
        
        self.knowledge[cache_key] = {
            'cached': datetime.now().isoformat(),
            'query': query,
            'results': results,
            'summary': summary
        }
        self._save()
        
        return {
            'query': query,
            'source': 'web',
            'results': results,
            'summary': summary
        }
    
    def get_fact(self, topic):
        topic = topic.lower().strip()
        if topic in self.knowledge:
            return self.knowledge[topic].get('summary', 'No fact available.')
        return None
    
    def get_stats(self):
        return {
            'cached_topics': len(self.knowledge),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': round(self.cache_hits / max(1, self.cache_hits + self.cache_misses) * 100, 1)
        }
