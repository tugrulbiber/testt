from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "deepseek-ai/deepseek-coder-5.7bmqa-base"

print("📦 Tokenizer indiriliyor...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("🧠 Model indiriliyor...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    offload_folder="offload",  # bu klasör oluşur
    trust_remote_code=True
)
