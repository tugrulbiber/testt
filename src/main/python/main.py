import os
from dotenv import load_dotenv
from github import Github
from transformers import pipeline
import smtplib
from email.mime.text import MIMEText

# .env dosyasını yükle
load_dotenv()

# Config ayarları
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
EMAIL_CONFIG = {
    "address": os.getenv("EMAIL_ADDRESS"),
    "password": os.getenv("EMAIL_PASSWORD")
}

# Llama modelini yükle
feedback_analyzer = pipeline("text-generation", model="decapoda-research/llama-1b-hf")

def get_commits(repo_name, max_commits=5):
    """GitHub'dan commit'leri çek."""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        return list(repo.get_commits()[:max_commits])
    except Exception as e:
        print(f"❌ GitHub API Hatası: {e}")
        return []

def generate_feedback(commit):
    """Commit mesajına göre feedback üret."""
    prompt = f"""
    Aşağıdaki commit mesajını analiz edip geliştiriciye **kod kalitesi** açısından feedback ver:
    Commit Mesajı: '{commit.commit.message}'
    Değişiklikler: '{commit.files[0].patch if commit.files else 'N/A'}'
    Feedback:
    """
    feedback = feedback_analyzer(prompt, max_length=200)[0]['generated_text']
    return feedback.split("Feedback:")[-1].strip()

def send_email(to_email, feedback):
    """Feedback'i mail olarak gönder."""
    try:
        msg = MIMEText(feedback)
        msg['Subject'] = "🤖 AI Code Feedback"
        msg['From'] = EMAIL_CONFIG["address"]
        msg['To'] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["address"], EMAIL_CONFIG["password"])
            server.send_message(msg)
        print(f"📧 Feedback gönderildi: {to_email}")
    except Exception as e:
        print(f"❌ Mail Gönderme Hatası: {e}")

if __name__ == "__main__":
    # Kullanıcıdan girdileri al (veya sabit değerler kullan)
    REPO_NAME = "tugrulbiber/CommitScannerAi"  # Örnek repo
    TARGET_EMAIL = "target_email@example.com"  # Feedback'in gideceği mail

    # İş akışı
    commits = get_commits(REPO_NAME)
    for commit in commits:
        feedback = generate_feedback(commit)
        print(f"💡 Feedback: {feedback}")
        send_email(TARGET_EMAIL, feedback)