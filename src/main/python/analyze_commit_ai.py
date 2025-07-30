import sys
import re
import os
import io
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def format_email_body(repository, filename, commit_id, commit_message, ai_explanation):
filename_clean = os.path.basename(filename) if filename else "-"
commit_id_clean = commit_id if commit_id else "unknown_commit"
commit_message_clean = commit_message if commit_message else "Mesaj boş"
return f"""
Bir commit incelemesi sırasında dikkat edilmesi gereken bir durum tespit edildi:

Repository: {repository}
Dosya: {filename_clean}
Commit ID: {commit_id_clean}
Commit Mesajı: {commit_message_clean}

Yapay Zeka Açıklaması:
{ai_explanation}

Lütfen bu dosyayı gözden geçir.

Teşekkürler,
CommitScanner
""".strip()

model_id = "deepseek-ai/deepseek-coder-5.7bmqa-base"

def remove_xml_diffs(diff_text):
blocks = re.split(r'(?=diff --git )', diff_text)
return ''.join(block for block in blocks if not re.search(r'.xml\b', block, re.IGNORECASE))

MAX_PROMPT_CHARS = 4000

repo_name = sys.argv[1] if len(sys.argv) > 1 else "unknown_repo"
file_name = sys.argv[2] if len(sys.argv) > 2 else "unknown_file"
commit_id = sys.argv[3] if len(sys.argv) > 3 else "unknown_commit"
commit_message = sys.argv[4] if len(sys.argv) > 4 else "Mesaj boş"
commit_diff = sys.argv[5] if len(sys.argv) > 5 else ""

if not commit_diff.strip():
explanation = "Kod diff'i boş olduğu için analiz yapılmadı."
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
explanation = "Sadece XML dosyaları içerdiği için analiz yapılmadı."
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
Sen deneyimli bir yazılım denetleyicisisin. Aşağıda bir commit mesajı ve kod farkı (diff) veriliyor. Bu bilgileri kullanarak teknik bir geri bildirim oluştur.

Kurallar:

Güvenlik açığı, mantık hatası, validasyon eksikliği veya kod kalitesi sorunu varsa açıkla.

Dosya veya satır bilgisi belirtilebiliyorsa belirt.

Gerekli yerlerde örnek ver.

Gereksiz tekrar yapma.

Sorun yoksa “Kodda belirgin bir sorun tespit edilmedi.” yaz.

Commit mesajı ile diff tutarsızsa bunu da belirt.

Commit mesajı:
{commit_message}

Kod diff:
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
error_message = "Yapay zeka çalıştırılamadı, teknik bir hata oluştu."
email_body = format_email_body(
repository=repo_name,
filename=file_name,
commit_id=commit_id,
commit_message=commit_message,
ai_explanation=error_message
)
print(email_body)
sys.exit(1)