#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""사용 가능한 Gemini 모델 목록 확인"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("=" * 80)
print("사용 가능한 Gemini 모델 목록")
print("=" * 80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\nOK {model.name}")
        print(f"   Description: {model.description}")
        print(f"   Supported: {', '.join(model.supported_generation_methods)}")
