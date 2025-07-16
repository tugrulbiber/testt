import sys
import re
import traceback
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_path = "C:\\Users\\TUĞRUL BİBER\\.cache\\huggingface\\hub\\models--deepseek-ai--deepseek-coder-5.7bmqa-base"

commit_message = sys.argv[1] if len(sys.argv) > 1 else "Mesaj boş"
commit_diff = sys.argv[2] if len(sys.argv) > 2 else "Diff boş"

# Path temizleme
commit_diff = re.sub(r'[A-Z]:\\\\[^\\s\n\r]+', '[local path]', commit_diff)
commit_diff = re.sub(r'(/[\w./\-]+)+', '[repo path]', commit_diff)

prompt = f"""
Sen bir yazılım denetleyicisisin.

Aşağıda bir commit mesajı ve kod farkı (diff) verilmiştir.

- Sorun varsa hangi dosyada, hangi satırda olduğunu yaz.
- Açık ve sade bir açıklama ver.
- Sorun yoksa "Sorun bulunamadı." yaz.

Commit mesajı:
{commit_message}

Kod diff:
{commit_diff}
"""

try:
    print("Tokenizer indiriliyor...")
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)

    print("Model indiriliyor...")
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)

    print("Cevap üretiliyor...")
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    output = pipe(prompt, max_new_tokens=300, do_sample=False)[0]["generated_text"]

    # Gereksiz path'leri temizle
    output = re.sub(r'[A-Z]:\\\\[^\\s\n\r]+', '[local path]', output)
    output = re.sub(r'(/[\w./\-]+)+', '[repo path]', output)

    print(output)

except Exception as e:
    error_summary = "Yapay zeka analizi sırasında bir hata oluştu: "

    if "HFValidationError" in str(e):
        message = "Repo kimliği geçersiz formatta. Lütfen model yolu veya HuggingFace erişim ayarlarınızı kontrol edin."
    elif "safetensors" in str(e):
        message = "Model yüklenemedi. 'safetensors' kütüphanesi eksik olabilir."
    else:
        # Daha genel bir hata özeti
        tb_lines = traceback.format_exception_only(type(e), e)
        message = tb_lines[-1].strip()

    print(f"{error_summary}{message}")
