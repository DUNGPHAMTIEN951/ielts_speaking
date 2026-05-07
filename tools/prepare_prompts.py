import os
import json
import re
import glob

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# If script is in 'scripts' or 'tools' folder, BASE_DIR is parent. Otherwise, it's current dir.
if os.path.basename(SCRIPT_DIR) in ['scripts', 'tools']:
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
else:
    BASE_DIR = SCRIPT_DIR

def sanitize_id(text):
    # Remove non-alphanumeric (except underscores and spaces)
    s = re.sub(r'[^a-zA-Z0-9\s_]', '', text)
    # Replace ALL whitespace (newlines, tabs, etc.) with underscores
    s = re.sub(r'\s+', '_', s)
    s = s.strip('_').lower()
    # Replace multiple underscores with a single one
    s = re.sub(r'_+', '_', s)
    return s[:100]

def split_sentences(text):
    if not isinstance(text, str): return []
    # Basic sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 15]

def extract_from_json(base_dir):
    data_dirs = [
        os.path.join(base_dir, "ielts_data_48"),
        os.path.join(base_dir, "ielts_data_p2")
    ]
    prompts = []
    seen_ids = set()
    
    for d in data_dirs:
        if not os.path.exists(d):
            print(f"Directory not found: {d}")
            continue
        files = glob.glob(os.path.join(d, "*.json"))
        for fpath in files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    fname = os.path.basename(fpath)
                    
                    # 1. Standard Vocab
                    vocab = data.get('v', [])
                    for item in vocab:
                        word = item.get('word', '')
                        example = item.get('example', '')
                        if not word: continue
                        word_id = sanitize_id(f"word_{word}")
                        if word_id and word_id not in seen_ids:
                            seen_ids.add(word_id)
                            clean_example = example.replace('"', '').replace("'", "").strip()
                            prompt = (
                                f"An educational illustration representing the English concept '{word}'. "
                                f"Scene: {clean_example}. "
                                f"Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, "
                                f"detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                            )
                            prompts.append({"id": word_id, "prompt": prompt})

                    # 2. Extract from examiner_note (words in quotes)
                    note = data.get('examiner_note', '')
                    quoted_phrases = re.findall(r"['\"]([^'\"]{4,})['\"]", note)
                    for phrase in quoted_phrases:
                        phrase_id = sanitize_id(f"note_{phrase}")
                        if phrase_id and phrase_id not in seen_ids:
                            seen_ids.add(phrase_id)
                            prompt = (
                                f"An educational illustration representing the idiom or phrase '{phrase}'. "
                                f"Concept: IELTS speaking high-level vocabulary. "
                                f"Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, "
                                f"detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                            )
                            prompts.append({"id": phrase_id, "prompt": prompt})

                    # 3. Extract sentences from ALL sample levels (Band 7, 8, 9)
                    samples = data.get('samples', {})
                    if isinstance(samples, dict):
                        for level in ['band7', 'band8', 'band9']:
                            level_data = samples.get(level, '')
                            text = ""
                            if isinstance(level_data, dict):
                                text = level_data.get('text', '')
                            else:
                                text = level_data
                            
                            if text:
                                sentences = split_sentences(text)
                                for i, sent in enumerate(sentences):
                                    sent_id = sanitize_id(f"sent_{fname}_{level}_{i}")
                                    if sent_id not in seen_ids:
                                        seen_ids.add(sent_id)
                                        clean_sent = sent.replace('"', '').replace("'", "").strip()
                                        prompt = (
                                            f"A cinematic Solarpunk scene representing: {clean_sent}. "
                                            f"Style: Makoto Shinkai anime art style, vibrant colors, high-quality digital art, 8k."
                                        )
                                        prompts.append({"id": sent_id, "prompt": prompt})
            except Exception as e:
                print(f"Error in JSON {fpath}: {e}")
    return prompts, seen_ids

def extract_from_html(base_dir, seen_ids):
    html_files = glob.glob(os.path.join(base_dir, "ielts_speaking_part_*.html"))
    prompts = []
    
    # Regex to find word objects: { word: "...", meaning: "..." }
    word_re = re.compile(r'\{\s*word:\s*["\']([^"\']+)["\'],\s*meaning:\s*["\']([^"\']+)["\']\s*\}')
    # Regex for answer strings in HTML
    a_re = re.compile(r'a:\s*["\']([^"\']{30,})["\']')
    # Regex for upgradeToBand8 replacements
    upgrade_re = re.compile(r'res:\s*["\']([^"\']{5,})["\']')

    for fpath in html_files:
        fname = os.path.basename(fpath)
        print(f"Processing HTML: {fname}")
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 1. Words from v: [] blocks
                words = word_re.findall(content)
                for word, meaning in words:
                    word_id = sanitize_id(f"html_word_{word}")
                    if word_id and word_id not in seen_ids:
                        seen_ids.add(word_id)
                        prompt = (
                            f"An educational illustration for the concept '{word}'. "
                            f"Meaning: {meaning}. "
                            f"Style: Solarpunk aesthetic, Makoto Shinkai art style, vibrant colors, "
                            f"detailed environment, peaceful atmosphere, high-quality digital art, 8k resolution."
                        )
                        prompts.append({"id": word_id, "prompt": prompt})

                # 2. Sentences from answers
                answers = a_re.findall(content)
                for i, ans in enumerate(answers):
                    sentences = split_sentences(ans)
                    for j, sent in enumerate(sentences):
                        sent_id = sanitize_id(f"html_sent_{fname}_{i}_{j}")
                        if sent_id not in seen_ids:
                            seen_ids.add(sent_id)
                            clean_sent = sent.replace('"', '').replace("'", "").strip()
                            prompt = (
                                f"A cinematic Solarpunk scene representing: {clean_sent}. "
                                f"Style: Makoto Shinkai anime art style, vibrant colors, high-quality digital art."
                            )
                            prompts.append({"id": sent_id, "prompt": prompt})

                # 3. Phrases from upgradeToBand8
                upgrades = upgrade_re.findall(content)
                for phrase in upgrades:
                    phrase_id = sanitize_id(f"upgrade_{phrase}")
                    if phrase_id and phrase_id not in seen_ids:
                        seen_ids.add(phrase_id)
                        prompt = (
                            f"A visual representation of the advanced English phrase '{phrase}'. "
                            f"Style: Solarpunk, Makoto Shinkai, beautiful landscape, digital art, 8k."
                        )
                        prompts.append({"id": phrase_id, "prompt": prompt})

        except Exception as e:
            print(f"Error processing {fpath}: {e}")
            
    return prompts

def main():
    base_dir = BASE_DIR
    
    # 1. Extract from JSON
    json_prompts, seen_ids = extract_from_json(base_dir)
    print(f"Extracted {len(json_prompts)} prompts from JSON directories.")
    
    # 2. Extract from HTML
    html_prompts = extract_from_html(base_dir, seen_ids)
    print(f"Extracted {len(html_prompts)} additional prompts from HTML files.")
    
    all_prompts = json_prompts + html_prompts
    
    # 3. Ensure output directory exists
    output_dir = os.path.join(base_dir, "data", "prompts")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "prompts.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_prompts, f, ensure_ascii=False, indent=2)
        
    print("-" * 40)
    print(f"FINAL SUMMARY:")
    print(f"Total unique image prompts: {len(all_prompts)}")
    print(f"Output saved to: {output_path}")
    
    if len(all_prompts) < 5000:
        print(f"Warning: Only {len(all_prompts)} items found. Still below the 5000 goal.")
    else:
        print(f"Success! Goal of 5000+ items met (Total: {len(all_prompts)}).")
    print("-" * 40)

if __name__ == "__main__":
    main()
