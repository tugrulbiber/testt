import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ---------------------- ARG CHECK ----------------------
if len(sys.argv) < 3:
    print("Kullanım: python analyze_commit_ai.py '<commit_message>' '<commit_diff>'")
    sys.exit(1)

commit_message = sys.argv[1]
commit_diff = sys.argv[2]

# ---------------------- LOAD MODEL ----------------------
model_path = "C:/path/to/your/model/deepseek-coder-5.7bmqa-base"  # <-- burayı kendi klasör yoluna göre düzenle
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto")

# ---------------------- PROMPT ----------------------
prompt = f"""
Sen bir yapay zeka kod inceleyicisisin.

Aşağıda bir commit mesajı ve ona ait kod farkı (diff) verilecektir.

Senin görevin:
- Eğer commit’te herhangi bir sorun, kötü pratik ya da geliştirilebilecek bir yer varsa, sadece o kısmı yaz.
- Eğer bir problem yoksa yalnızca "Sorun tespit edilmedi." yaz.

Commit mesajı:
{commit_message}

Kod diff:
{commit_diff}
"""

# ---------------------- TOKENIZE + GENERATE ----------------------
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512)

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)
