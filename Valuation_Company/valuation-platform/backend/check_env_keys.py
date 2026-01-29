import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

keys = [
    "GOOGLE_API_KEY",      # Gemini
    "NAVER_CLIENT_ID",     # Naver Search
    "NAVER_CLIENT_SECRET", # Naver Search
    "SMTP_USER",          # Email Sender
    "SMTP_PASSWORD"        # Email Password
]

print("Checking environment variables...")
for key in keys:
    value = os.getenv(key)
    if value:
        print(f"✅ {key}: Found")
    else:
        print(f"❌ {key}: Missing")
