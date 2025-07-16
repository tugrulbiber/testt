# utils/email_formatter.py

def format_commit_alert_email(
    repo_name: str,
    file_name: str,
    commit_id: str,
    commit_message: str,
    ai_summary: str,
    line_info: str,
    error_traceback: str
) -> str:
    """
    CommitScanner için yapay zeka hatası mailini formatlayan fonksiyon.
    """
    email_content = f"""
Merhaba Tuğrul Biber,

Bir commit incelemesi sırasında dikkat edilmesi gereken bir durum tespit edildi:

📁 Repository: {repo_name}
📄 Dosya: {file_name}
🔁 Commit ID: {commit_id}
📝 Commit Mesajı: {commit_message}

🧠 Yapay Zeka Açıklaması:
{ai_summary}

📄 Log Detayı (Satır bilgisi: {line_info}):
{error_traceback}

Lütfen bu dosyayı gözden geçir.

Teşekkürler,
CommitScanner
""".strip()
    return email_content
