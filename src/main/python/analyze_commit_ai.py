import sys
import re
import traceback
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from utilsemailformatter import format_email_body  # Burada mail formatlama fonksiyonunu import ettim

# Hugging Face model ID'si
model_id = "deepseek-ai/deepseek-coder-5.7b-instruct"

commit_message = sys.argv[1] if len(sys.argv) > 1 else "Mesaj boş"
commit_diff = sys.argv[2] if len(sys.argv) > 2 else "Diff boş"

# Path temizleme
commit_diff_clean = re.sub(r'[A-Z]:\\\\[^\\s\n\r]+', '[local path]', commit_diff)
commit_diff_clean = re.sub(r'(/[\w./\-]+)+', '[repo path]', commit_diff_clean)

prompt = f"""
Sen deneyimli bir yazılım denetleyicisisin ve görevin commit mesajı ile birlikte verilen kod farklarını (diff) analiz ederek olası sorunları belirlemek.

⛏️ Analiz Kuralları:
1. Kodda **hatalı mantık, eksik validasyon, güvenlik açığı** veya **kod kalitesi sorunları** varsa tespit et.
2. Hangi **dosyada** ve mümkünse **satır numarasında** olduğunu belirt.
3. Açıklaman **teknik ve profesyonel** olsun. Gereksiz tekrar veya varsayım yapma.
4. Eğer açık bir sorun yoksa **“Kodda belirgin bir sorun tespit edilmedi.”** de.
5. Commit mesajı ile diff arasında tutarsızlık varsa, belirt.

Commit mesajı:
{commit_message}

Kod diff:
{commit_diff_clean}
"""

try:
    print("📦 Tokenizer indiriliyor...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    print("🧠 Model indiriliyor...")
    model = AutoModelForCausalLM.from_pretrained(model_id)

    print("🤖 Cevap üretiliyor...")
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    raw_output = pipe(prompt, max_new_tokens=300, do_sample=False)[0]["generated_text"]

    # Output'ta local path tekrar temizle
    output_clean = re.sub(r'[A-Z]:\\\\[^\\s\n\r]+', '[local path]', raw_output)
    output_clean = re.sub(r'(/[\w./\-]+)+', '[repo path]', output_clean)

    # Mail formatını kullanarak çıktıyı hazırla
    email_body = format_email_body(
        repository="leave_management_ai",  # Burayı dinamik yapabilirsin
        filename="[dosya adı]",            # Dinamik hale getirilebilir
        commit_id="[commit id]",           # Dinamik olarak dışardan al
        commit_message=commit_message,
        ai_explanation=output_clean
    )

    print(email_body)

except Exception as e:
    tb_lines = traceback.format_exception_only(type(e), e)
    error_summary = tb_lines[-1].strip()
    match = re.search(r'line (\d+)', error_summary)
    line_info = f"Satır: {match.group(1)}" if match else "Satır bilgisi bulunamadı"
    error_message = f"Yapay Zeka çalıştırılamadı. Hata: {error_summary} ({line_info})"

    email_body = format_email_body(
        repository="leave_management_ai",
        filename="[dosya adı]",
        commit_id="[commit id]",
        commit_message=commit_message,
        ai_explanation=error_message
    )

    print(email_body)
