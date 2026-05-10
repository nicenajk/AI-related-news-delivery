import os
import requests
from datetime import datetime
from docx import Document # Word 파일 생성을 위한 라이브러리

# GitHub Secrets에서 정보 로드
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELE_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_ai_data():
    """Gemini API를 통해 키워드별 트렌드 수집"""
    keywords = ["외식업 AI 자동화", "심리상담 AI 트렌드", "비즈니스 에이전트 설계"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    reports = []
    for kw in keywords:
        prompt = f"30년 경력 경영자 관점에서 '{kw}' 관련 최신 트렌드 1개를 제목, 3줄 요약, 경영 인사이트 순으로 정리해줘."
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            res = requests.post(url, headers=headers, json=data, timeout=60)
            res.raise_for_status()
            content = res.json()['candidates'][0]['content']['parts'][0]['text']
            reports.append(content)
            print(f"✅ {kw} 분석 완료")
        except Exception as e:
            print(f"❌ {kw} 분석 실패: {e}")
            continue
    return reports

def create_word_and_send(results):
    """수집된 데이터를 Word로 저장하고 텔레그램으로 전송"""
    # 1. Word 문서 생성
    date_str = datetime.now().strftime('%m%d')
    file_name = f"AI_Business_Report_{date_str}.docx"
    
    doc = Document()
    doc.add_heading('최장규 대표의 AI 비즈니스 브리핑', 0)
    doc.add_heading(f"발행일: {datetime.now().strftime('%Y-%m-%d')}", level=1)
    
    for r in results:
        doc.add_paragraph(r)
        doc.add_paragraph("-" * 50)
    
    doc.save(file_name)
    print(f"📂 파일 생성 성공: {file_name}")

    # 2. 텔레그램 '문서 전송(sendDocument)' API 사용
    send_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendDocument"
    with open(file_name, 'rb') as f:
        payload = {
            'chat_id': CHAT_ID,
            'caption': f"📅 {datetime.now().strftime('%Y-%m-%d')} 리포트가 도착했습니다."
        }
        files = {'document': f}
        response = requests.post(send_url, data=payload, files=files)
        
        if response.status_code == 200:
            print("🚀 텔레그램 파일 전송 성공!")
        else:
            print(f"❌ 전송 실패: {response.text}")

if __name__ == "__main__":
    if all([GEMINI_KEY, TELE_TOKEN, CHAT_ID]):
        print("🚀 시스템 가동 시작...")
        ai_results = get_ai_data()
        if ai_results:
            create_word_and_send(ai_results)
    else:
        print("❌ 설정값(Secrets)이 누락되었습니다.")
