import os
import requests
from datetime import datetime

# GitHub Secrets에서 가져오기
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELE_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_briefing():
    # 대표님의 사업 키워드
    keywords = ["외식업 AI 자동화", "심리상담 트렌드", "비즈니스 에이전트"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    header = {'Content-Type': 'application/json'}
    final_text = f"📅 {datetime.now().strftime('%Y-%m-%d')} 리더를 위한 AI 브리핑\n"
    final_text += "━━━━━━━━━━━━━━━━━━\n\n"

    for kw in keywords:
        prompt = f"30년 경력 경영자 관점에서 '{kw}' 관련 최신 트렌드 1개를 제목, 요약, 시사점 순으로 짧게 정리해줘."
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            res = requests.post(url, headers=header, json=data, timeout=60)
            res.raise_for_status()
            content = res.json()['candidates'][0]['content']['parts'][0]['text']
            final_text += f"🔍 {kw}\n{content}\n\n"
        except:
            continue
    return final_text

def send_to_telegram(message):
    send_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(send_url, json=payload)

if __name__ == "__main__":
    if GEMINI_KEY and TELE_TOKEN and CHAT_ID:
        report = get_briefing()
        send_to_telegram(report)
    else:
        print("설정값 확인이 필요합니다.")
