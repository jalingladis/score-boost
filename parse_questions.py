import re
import json

INPUT_FILE = "ocr_text/output.txt"
OUTPUT_FILE = "processed/questions.json"


# -------------------------------
# STEP 1: Read OCR text
# -------------------------------
def read_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# -------------------------------
# STEP 2: Split questions
# -------------------------------
def split_questions(text):
    # normalize weird formats first
    text = re.sub(r'(\d+)\s*,', r'\1.', text)   # "6 ," → "6."
    text = re.sub(r'(\d+)\s*\)', r'\1.', text)  # "6)" → "6."

    # now split
    questions = re.split(r'\n(?=\d+\.)', text)

    return questions


# -------------------------------
# STEP 3: Keep only English lines
# -------------------------------
def extract_english_block(block):
    lines = block.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Stop after answer line
        if "Answer not known" in line:
            clean_lines.append(line)
            break

        # Keep only ASCII (English)
        if re.match(r'^[\x00-\x7F]+$', line):
            clean_lines.append(line)

    return clean_lines


# -------------------------------
# STEP 4: Parse question + options
# -------------------------------
def parse_question(lines):
    question_lines = []
    options = {}

    option_pattern = re.compile(r'^\(?([A-E])\)?\s*(.*)')

    for line in lines:
        match = option_pattern.match(line)

        if match:
            key = match.group(1)
            value = match.group(2).strip()
            options[key] = value
        else:
            question_lines.append(line)

    question_text = " ".join(question_lines).strip()

    return {
        "question": question_text,
        "options": options
    }


# -------------------------------
# STEP 5: Full pipeline
# -------------------------------
def extract_questions(text):
    raw_questions = split_questions(text)
    parsed_questions = []

    for q in raw_questions:
        if len(q.strip()) < 30:
            continue

        lines = extract_english_block(q)
        parsed = parse_question(lines)

        # keep only valid questions
        if parsed["options"]:
            parsed_questions.append(parsed)

    return parsed_questions


# -------------------------------
# STEP 6: Save JSON
# -------------------------------
def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Saved {len(data)} questions to {path}")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    text = read_text(INPUT_FILE)
    questions = extract_questions(text)
    save_json(questions, OUTPUT_FILE)