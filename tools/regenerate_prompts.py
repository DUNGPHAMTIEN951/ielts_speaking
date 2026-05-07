import os
import json
import re
import glob
import hashlib
import subprocess

# Constants
BASE_DIR = r"d:\Ton_nhi\ielts_splits"
DATA_FILE = os.path.join(BASE_DIR, "ielts_all_data.js")
PROMPTS_FILE = os.path.join(BASE_DIR, "data", "prompts", "prompts.json")

def sanitize_id(text):
    if not text: return "unknown"
    # Remove non-alphanumeric (except underscores and spaces)
    s = re.sub(r'[^a-zA-Z0-9\s_]', '', str(text))
    # Replace ALL whitespace with underscores
    s = re.sub(r'\s+', '_', s)
    s = s.strip('_').lower()
    # Replace multiple underscores with a single one
    s = re.sub(r'_+', '_', s)
    return s[:100]

def split_sentences(text):
    if not isinstance(text, str): return []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 15]

def extract_prompts():
    prompts = []
    seen_ids = set()

    # 1. Extract from ielts_all_data.js via Node.js
    if os.path.exists(DATA_FILE):
        print(f"Reading {DATA_FILE} via Node.js...")
        try:
            result = subprocess.run(['node', 'tools/extract_data.js'], capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for part in ['p1', 'p2', 'p3']:
                    items = data.get(part, [])
                    for q in items:
                        qid = q.get('id', 'unknown')
                        # Vocab
                        vocab = q.get('v', [])
                        for v in vocab:
                            word = v.get('word', '')
                            example = v.get('example', '')
                            if word:
                                word_id = sanitize_id(f"word_{word}")
                                if word_id not in seen_ids:
                                    seen_ids.add(word_id)
                                    prompts.append({
                                        "id": word_id,
                                        "prompt": f"An educational illustration representing the English concept '{word}'. Scene: {example}. Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                                    })
                        
                        # Examiner Note extraction
                        note = q.get('examiner_note', '')
                        if note:
                            quoted_phrases = re.findall(r"['\"]([^'\"]{4,})['\"]", note)
                            for phrase in quoted_phrases:
                                phrase_id = sanitize_id(f"note_{phrase}")
                                if phrase_id not in seen_ids:
                                    seen_ids.add(phrase_id)
                                    prompts.append({
                                        "id": phrase_id,
                                        "prompt": f"An educational illustration representing the English idiom or phrase '{phrase}'. Concept: IELTS high-level vocabulary. Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                                    })

                        # Samples
                        samples = q.get('samples', {})
                        for level in ['band7', 'band8', 'band9', 'suggested_answer']:
                            level_data = samples.get(level, '')
                            if not level_data and level == 'suggested_answer':
                                level_data = q.get('suggested_answer', '')
                            text = ""
                            if isinstance(level_data, dict):
                                text = level_data.get('text', '')
                            else:
                                text = level_data
                            
                            if text:
                                sentences = split_sentences(text)
                                for i, sent in enumerate(sentences):
                                    sent_id = sanitize_id(f"sent_{qid}_{level}_{i}")
                                    if sent_id not in seen_ids:
                                        seen_ids.add(sent_id)
                                        prompts.append({
                                            "id": sent_id,
                                            "prompt": f"A cinematic scene from an IELTS story: {sent}. Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                                        })
            else:
                print(f"Node.js error: {result.stderr}")
        except Exception as e:
            print(f"Error extracting data via Node.js: {e}")

    # 2. Extract from ai_vocab
    ai_vocab_files = glob.glob(os.path.join(BASE_DIR, "ai_vocab", "*.json"))
    for fpath in ai_vocab_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                vocab = data.get('vocab', [])
                for v in vocab:
                    word = v.get('word', '')
                    example = v.get('example', '')
                    if word:
                        word_id = sanitize_id(f"word_{word}")
                        if word_id not in seen_ids:
                            seen_ids.add(word_id)
                            prompts.append({
                                "id": word_id,
                                "prompt": f"An educational illustration representing the English concept '{word}'. Scene: {example}. Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                            })
        except: pass

    # 3. Extract from ai_suggestions
    ai_sug_files = glob.glob(os.path.join(BASE_DIR, "ai_suggestions", "*.json"))
    for fpath in ai_sug_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                qid = data.get('id', 'unknown')
                band = data.get('band', '8')
                text = data.get('content', '') or data.get('suggested_answer', '')
                if text:
                    sentences = split_sentences(text)
                    for i, sent in enumerate(sentences):
                        sent_id = sanitize_id(f"sent_ai_{qid}_band{band}_{i}")
                        if sent_id not in seen_ids:
                            seen_ids.add(sent_id)
                            prompts.append({
                                "id": sent_id,
                                "prompt": f"A cinematic scene from an IELTS Phạm Tiến Dũng Gia Sư story: {sent}. Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                            })
        except: pass

    print(f"Extracted {len(prompts)} unique prompts.")
    
    os.makedirs(os.path.dirname(PROMPTS_FILE), exist_ok=True)
    with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    print(f"Saved to {PROMPTS_FILE}")

if __name__ == "__main__":
    extract_prompts()
