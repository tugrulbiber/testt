import sys
import re
import os
import io
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def format_email_body(repository, filename, commit_id, commit_message, ai_explanation):
    filename_clean = os.path.basename(filename) if filename is not None else "-"
    commit_id_clean = commit_id if commit_id else "unknown_commit"
    commit_message_clean = commit_message if commit_message else "Empty message"
    return f"""
A potential issue has been detected during the review of a commit:

Repository: {repository}
File: {filename_clean}
Commit ID: {commit_id_clean}
Commit Message: {commit_message_clean}

AI Explanation:
{ai_explanation}

Please review this file.

Thank you,
CommitScanner
""".strip()

model_id = "deepseek-ai/deepseek-coder-5.7bmqa-base"

def remove_xml_diffs(diff_text):
    blocks = re.split(r'(?=diff --git )', diff_text)
    return ''.join(block for block in blocks if not re.search(r'\.xml\b', block, re.IGNORECASE))

MAX_PROMPT_CHARS = 4000

repo_name = sys.argv[1] if len(sys.argv) > 1 else "unknown_repo"
file_name = sys.argv[2] if len(sys.argv) > 2 else "unknown_file"
commit_id = sys.argv[3] if len(sys.argv) > 3 else "unknown_commit"
commit_message = sys.argv[4] if len(sys.argv) > 4 else "Empty message"
commit_diff = sys.argv[5] if len(sys.argv) > 5 else ""

if not commit_diff.strip():
    explanation = "Code diff is empty, no analysis performed."
    email_body = format_email_body(
        repository=repo_name,
        filename=file_name,
        commit_id=commit_id,
        commit_message=commit_message,
        ai_explanation=explanation
    )
    print(email_body)
    sys.exit(0)

commit_diff_filtered = remove_xml_diffs(commit_diff)

if not commit_diff_filtered.strip():
    explanation = "Only XML files were found in the diff, no analysis performed."
    email_body = format_email_body(
        repository=repo_name,
        filename=file_name,
        commit_id=commit_id,
        commit_message=commit_message,
        ai_explanation=explanation
    )
    print(email_body)
    sys.exit(0)

commit_diff_limited = commit_diff_filtered[:MAX_PROMPT_CHARS]

prompt = f"""
You are an experienced software reviewer. Below is a commit message and code diff. Use this information to provide a technical feedback.

Rules:
- Explain if there is any security vulnerability, logical error, missing validation, or code quality issue.
- Specify file or line information if possible.
- Provide examples where necessary.
- Avoid unnecessary repetition.
- If no issues are found, write “No significant issues detected in the code.”
- Mention if the commit message is inconsistent with the diff.

Commit message:
{commit_message}

Code diff:
{commit_diff_limited}
"""

try:
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    raw_output = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)[0]["generated_text"]
    email_body = format_email_body(
        repository=repo_name,
        filename=file_name,
        commit_id=commit_id,
        commit_message=commit_message,
        ai_explanation=raw_output.strip()
    )
    print(email_body)
except Exception:
    error_message = "AI execution failed due to a technical error."
    email_body = format_email_body(
        repository=repo_name,
        filename=file_name,
        commit_id=commit_id,
        commit_message=commit_message,
        ai_explanation=error_message
    )
    print(email_body)
    sys.exit(1)
