from dotenv import load_dotenv
import os
import json
import requests
import re

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
NUM_QUESTIONS = 10


def _format_one_question(index: int, q: dict) -> str:
    raw_q = q.get("question", "")
    options = q.get("options", {})
    question_text = re.sub(r'^\d+\.\s*', '', raw_q).strip()

    lines = [f"### Question {index}"]
    lines.append(f"Question: {question_text}\n")

    if options:
        lines.append("Choices:")
        for key, val in options.items():
            lines.append(f"{key}. {val.strip()}")

    return "\n".join(lines)


def load_questions_from_file(
    path: str = "processed/questions.json", limit: int = NUM_QUESTIONS
) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        return ""

    subset = data[: min(limit, len(data))]
    blocks = [_format_one_question(i + 1, q) for i, q in enumerate(subset)]
    return "\n\n".join(blocks)


def analyze_questions(questions: str):
    url = "https://api.perplexity.ai/v1/responses"

    prompt = f"""
You are an expert TNPSC exam coach.

For EACH question below (numbered ### Question N), return one analysis object in the same order:
1. subject (Polity, History, Geography, Science, Current Affairs, etc.)
2. difficulty (Easy / Medium / Hard)
3. correct_answer (single letter: A, B, C, D, or E — match the choices given)

Return ONLY a valid JSON array with one object per question, in order (Question 1 first, then 2, ...). No markdown fences.
Example shape:
[
  {{"subject": "...", "difficulty": "...", "correct_answer": "A"}},
  {{"subject": "...", "difficulty": "...", "correct_answer": "C"}}
]

Questions:
{questions}


"""

    payload = {
        "model": "openai/gpt-5-mini",
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        content = result["output"][0]["content"][0]["text"]

        return content

    except Exception as e:
        print("[ERROR]", e)
        return None


if __name__ == "__main__":
    questions_text = load_questions_from_file("processed/questions.json")
    result = analyze_questions(questions_text)
    print(result)