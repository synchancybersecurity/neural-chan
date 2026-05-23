#!/usr/bin/env python3
"""Domain Ingestion Engine — bulk-load categorized knowledge into Neural Chan."""
import json, os, sys
from datetime import datetime

DATA_DIR = os.path.expanduser('~/neural-chan/data')
VOCAB_FILE = os.path.join(DATA_DIR, 'vocabulary_v2.json')

def load_vocab():
    try:
        with open(VOCAB_FILE, 'r') as f:
            vocab = json.load(f)
    except:
        vocab = {}
    for key in ['words', 'proficiency', 'conversations', 'name', 'personality', 'dictionary', 'domains']:
        if key not in vocab:
            vocab[key] = {} if key in ['dictionary', 'domains', 'personality'] else ([] if key == 'words' else 1.0 if key == 'proficiency' else 0 if key == 'conversations' else 'User')
    return vocab

def save_vocab(vocab):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(VOCAB_FILE, 'w') as f:
        json.dump(vocab, f, indent=2)

def ingest_domain_file(path, domain_name):
    vocab = load_vocab()
    added = 0
    skipped = 0
    
    if domain_name not in vocab['domains']:
        vocab['domains'][domain_name] = {'count': 0, 'ingested': datetime.now().isoformat()}
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = None
            for delim in [' | ', ' : ', ': ', ' - ', ' – ', '\t']:
                if delim in line:
                    parts = line.split(delim, 1)
                    break
            if not parts and ' ' in line:
                parts = line.split(' ', 1)
            if parts and len(parts) == 2:
                term = parts[0].strip().lower()
                definition = parts[1].strip()
                if len(term) > 1:
                    if term not in vocab['words']:
                        vocab['words'].append(term)
                        added += 1
                    vocab['dictionary'][term] = {
                        'definition': definition,
                        'domain': domain_name,
                        'ingested': datetime.now().isoformat()
                    }
                    skipped += 1
            else:
                skipped += 1
    
    vocab['domains'][domain_name]['count'] += added
    vocab['proficiency'] = min(100.0, vocab['proficiency'] + (0.02 * added))
    save_vocab(vocab)
    print(f"[✓] Domain '{domain_name}': +{added} terms | Total vocab: {len(vocab['words'])} | Proficiency: {vocab['proficiency']:.1f}%")
    return added

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 domain_ingest.py <file.txt> <domain_name>")
        print("Example: python3 domain_ingest.py math.txt mathematics")
        sys.exit(1)
    ingest_domain_file(sys.argv[1], sys.argv[2])
