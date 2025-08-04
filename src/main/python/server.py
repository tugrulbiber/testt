from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
import torch

app = FastAPI()

model_id = "deepseek-ai/deepseek-coder-5.7bmqa-base"
MAX_PROMPT_CHARS = 4000

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

class AnalyzeRequest(BaseModel):
    commitMessage: str
    diff: str

def remove_xml_diffs(diff_text):
    blocks = re.split(r'(?=diff --git )', diff_text)
    return ''.join(block for block in blocks if not re.search(r'\.xml\b', block, re.IGNORECASE))

def clean_ai_output(text):
    lines = text.splitlines()
    cleaned_lines = []
    skip_patterns = [
        r'^diff --git', r'^index ', r'^--- ', r'^\+\+\+ ', r'^@@ ',
        r'^Commit message:', r'^Commit Message:', r'^\s*$'
    ]
    for line in lines:
        if any(re.match(pat, line) for pat in skip_patterns):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

@app.post("/analyze")
async def analyze_commit(req: AnalyzeRequest):
    commit_diff = req.diff.strip()
    commit_message = req.commitMessage.strip()

    if not commit_diff:
        return {"result": "Code diff is empty, no analysis performed."}

    filtered_diff = remove_xml_diffs(commit_diff)
    if not filtered_diff:
        return {"result": "Only XML files found in diff, no analysis performed."}

    limited_diff = filtered_diff[:MAX_PROMPT_CHARS]

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
{limited_diff}
"""

    try:
        output = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)[0]["generated_text"]
        cleaned = clean_ai_output(output)
        if not cleaned:
            cleaned = "No significant issues detected."
        return {"result": cleaned}
    except Exception as e:
        return {"result": f"AI execution failed: {str(e)}"}
