import sys
import re
import io
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

model_id = "deepseek-ai/deepseek-coder-5.7bmqa-base"
MAX_PROMPT_CHARS = 4000

def remove_xml_diffs(diff_text):
    blocks = re.split(r'(?=diff --git )', diff_text)
    return ''.join(block for block in blocks if not re.search(r'\.xml\b', block, re.IGNORECASE))

def clean_ai_output(text):
    lines = text.splitlines()
    cleaned_lines = []
    skip_patterns = [
        r'^diff --git',
        r'^index ', r'^--- ', r'^\+\+\+ ', r'^@@ ',
        r'^Commit message:', r'^Commit Message:',
        r'^\s*$'
    ]
    for line in lines:
        if any(re.match(pat, line) for pat in skip_patterns):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

# Argümanlar
repo_name = sys.argv[1] if len(sys.argv) > 1 else "unknown_repo"
file_name = sys.argv[2] if len(sys.argv) > 2 else "unknown_file"
commit_id = sys.argv[3] if len(sys.argv) > 3 else "unknown_commit"
commit_message = sys.argv[4] if len(sys.argv) > 4 else ""
commit_diff = sys.argv[5] if len(sys.argv) > 5 else ""

# Diff kontrolü
if not commit_diff.strip():
    print("Code diff is empty, no analysis performed.")
    sys.exit(0)

commit_diff_filtered = remove_xml_diffs(commit_diff)

if not commit_diff_filtered.strip():
    print("Only XML files found in diff, no analysis performed.")
    sys.exit(0)

commit_diff_limited = commit_diff_filtered[:MAX_PROMPT_CHARS]

# Prompt
prompt = f"""
You are an experienced software reviewer. Below is a commit message and a code diff snippet. Provide a clear, concise summary of any issues without repeating or quoting the diff or commit message.

Rules:
- Write only a human-readable summary of security risks, logic errors, missing validation, or code quality issues.
- Do NOT include raw diff or commit message text.
- Mention file or line info if relevant.
- Avoid repetition.
- If no issues found, say “No significant issues detected.”
- Mention if commit message and diff do not match.

Commit message:
{commit_message}

Code diff snippet:
{commit_diff_limited}
"""

# AI işleyişi
try:
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    raw_output = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)[0]["generated_text"]

    ai_explanation = clean_ai_output(raw_output)

    if not ai_explanation:
        ai_explanation = "No significant issues detected."

    print(ai_explanation)
except Exception:
    print("AI execution failed due to a technical error.")
    sys.exit(1)
