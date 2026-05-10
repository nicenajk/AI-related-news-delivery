import os
import requests
from datetime import datetime
from docx import Document # Word 생성을 위한 라이브러리

# GitHub Secrets에서 가져오기
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELE_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_ai_data():
    keywords = ["외식업 AI 자동화", "심리상담 AI 트렌드", "비즈니스 에이전트"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    reports = []
    for kw in keywords:
        prompt = f"30년 경력 경영자 관점에서 '{kw}' 관련 최신 트렌드 1개를 제목, 3줄 요약, 경영 인사이트 순으로 정리해줘."
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            res = requests.post(url, json=data, timeout=60)
            content = res.json()['candidates'][0]['content']['parts'][0]['text']
            reports.append(content)
        except:
            continue
    return reports

def create_word_and_send(results):
    # 1. Word 파일 생성
    file_name = f"AI_Report_{datetime.now().strftime('%m%d')}.docx"
    doc = Document()
    doc.add_heading('최장규 대표의 AI 비즈니스 브리핑', 0)
    
    for r in results:
        doc.add_paragraph(r)
        doc.add_paragraph("-" * 50)
    doc.save(file_name)

    # 2. 텔레그램으로 파일 전송
    file_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendDocument"
    with open(file_name, 'rb') as f:
        payload = {'chat_id': CHAT_ID, 'caption': f"📅 {datetime.now().strftime('%Y-%m-%d')} AI 리포트가 도착했습니다."}
        files = {'document': f}
        requests.post(file_url, data=payload, files=files)

if __name__ == "__main__":
    print("🚀 리포트 생성 및 파일 전송 시작...")
    data = get_ai_data()
    if data:
        create_word_and_send(data)
        print("✅ 파일 전송 완료!")
