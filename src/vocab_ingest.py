#!/usr/bin/env python3
"""Vocabulary Ingestion Engine — bulk-load dictionary entries into Neural Chan's brain."""
import json, os, re, sys
from datetime import datetime

DATA_DIR = os.path.expanduser('~/neural-chan/data')
VOCAB_FILE = os.path.join(DATA_DIR, 'vocabulary_v2.json')

def load_vocab():
    try:
        with open(VOCAB_FILE, 'r') as f:
            vocab = json.load(f)
    except:
        vocab = {}
    # Ensure all required keys exist
    if 'words' not in vocab:
        vocab['words'] = []
    if 'proficiency' not in vocab:
        vocab['proficiency'] = 1.0
    if 'conversations' not in vocab:
        vocab['conversations'] = 0
    if 'name' not in vocab:
        vocab['name'] = 'User'
    if 'personality' not in vocab:
        vocab['personality'] = {'friendly': 0.5, 'analytical': 0.5}
    if 'dictionary' not in vocab:
        vocab['dictionary'] = {}
    return vocab

def save_vocab(vocab):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(VOCAB_FILE, 'w') as f:
        json.dump(vocab, f, indent=2)

def ingest_file(path):
    """Ingest dictionary entries from a text file.
    Format per line: word | definition
    Or: word: definition
    Or: word - definition
    """
    vocab = load_vocab()
    added = 0
    skipped = 0
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try multiple delimiters
            parts = None
            for delim in [' | ', ' : ', ': ', ' - ', ' – ', '\t']:
                if delim in line:
                    parts = line.split(delim, 1)
                    break
            
            if not parts and ' ' in line:
                # First word is the term, rest is definition
                parts = line.split(' ', 1)
            
            if parts and len(parts) == 2:
                word = parts[0].strip().lower()
                definition = parts[1].strip()
                
                if len(word) > 2 and word not in vocab['words']:
                    vocab['words'].append(word)
                    vocab['dictionary'][word] = {
                        'definition': definition,
                        'source': 'NTC Super Mini English Dictionary',
                        'ingested': datetime.now().isoformat()
                    }
                    added += 1
                else:
                    skipped += 1
            else:
                skipped += 1
    
    # Boost proficiency based on new words
    if added > 0:
        vocab['proficiency'] = min(100.0, vocab['proficiency'] + (0.05 * added))
    
    save_vocab(vocab)
    print(f"[✓] Ingested {added} words | Skipped {skipped} | Proficiency: {vocab['proficiency']:.1f}%")
    print(f"[✓] Total vocabulary: {len(vocab['words'])} words")
    print(f"[✓] Dictionary entries: {len(vocab['dictionary'])}")
    return added

def ingest_list(word_list, definitions=None):
    """Ingest a raw list of words."""
    vocab = load_vocab()
    added = 0
    defs = definitions or {}
    
    for word in word_list:
        w = word.strip().lower()
        if len(w) > 2 and w not in vocab['words']:
            vocab['words'].append(w)
            vocab['dictionary'][w] = {
                'definition': defs.get(w, 'Dictionary entry'),
                'source': 'NTC Super Mini English Dictionary',
                'ingested': datetime.now().isoformat()
            }
            added += 1
    
    if added > 0:
        vocab['proficiency'] = min(100.0, vocab['proficiency'] + (0.05 * added))
    
    save_vocab(vocab)
    print(f"[✓] Ingested {added} words | Total: {len(vocab['words'])} | Proficiency: {vocab['proficiency']:.1f}%")
    return added

def export_dictionary_md():
    """Export learned dictionary to markdown."""
    vocab = load_vocab()
    out_dir = os.path.expanduser('~/neural-chan/memory')
    os.makedirs(out_dir, exist_ok=True)
    
    md = f"""# Neural Chan — Ingested Dictionary

**Source:** NTC's Super Mini English Dictionary  
**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Entries:** {len(vocab.get('dictionary', {}))}

---

"""
    for word, entry in sorted(vocab.get('dictionary', {}).items()):
        md += f"**{word}** — {entry.get('definition', 'No definition.')}\n\n"
    
    path = os.path.join(out_dir, 'dictionary.md')
    with open(path, 'w') as f:
        f.write(md)
    print(f"[✓] Dictionary exported to {path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 vocab_ingest.py <dictionary.txt>")
        print("       python3 vocab_ingest.py --export")
        sys.exit(1)
    
    if sys.argv[1] == '--export':
        export_dictionary_md()
    else:
        ingest_file(sys.argv[1])
