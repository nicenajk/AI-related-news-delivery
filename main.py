import os
import requests
from datetime import datetime
from docx import Document

# 환경 변수 로드
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TELE_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_ai_data():
    keywords = ["외식업 AI 자동화", "심리상담 AI 트렌드", "비즈니스 에이전트"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    reports = []
    print(f"🔍 데이터 수집 시작 (모델: Gemini 1.5 Flash)")
    
    for kw in keywords:
        prompt = f"30년 경력 경영자 관점에서 '{kw}' 관련 최신 트렌드 1개를 제목, 3줄 요약, 경영 인사이트 순으로 정리해줘."
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            res = requests.post(url, json=data, timeout=60)
            res.raise_for_status()
            content = res.json()['candidates'][0]['content']['parts'][0]['text']
            reports.append(content)
            print(f"✅ {kw} 수집 성공")
        except Exception as e:
            print(f"❌ {kw} 수집 중 오류: {e}")
            continue
    return reports

def create_word_and_send(results):
    # 1. Word 파일 생성
    date_str = datetime.now().strftime('%m%d')
    file_name = f"AI_Report_{date_str}.docx"
    doc = Document()
    doc.add_heading('최장규 대표의 AI 비즈니스 브리핑', 0)
    for r in results:
        doc.add_paragraph(r)
        doc.add_paragraph("-" * 50)
    doc.save(file_name)
    print(f"📂 Word 파일 생성 완료: {file_name}")

    # 2. 텔레그램 전송 (상세 로그 출력)
    send_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendDocument"
    print(f"🚀 텔레그램으로 전송 시도 중... (ID: {CHAT_ID})")
    
    try:
        with open(file_name, 'rb') as f:
            payload = {'chat_id': CHAT_ID, 'caption': f"📅 {datetime.now().strftime('%Y-%m-%d')} AI 리포트"}
            files = {'document': f}
            response = requests.post(send_url, data=payload, files=files)
            
            if response.status_code == 200:
                print("✨ 텔레그램 전송 최종 성공!")
            else:
                print(f"❗ 텔레그램 응답 에러: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 전송 과정 중 예외 발생: {e}")

if __name__ == "__main__":
    # 필수 변수 체크
    if not all([GEMINI_KEY, TELE_TOKEN, CHAT_ID]):
        print("❌ 설정 오류: GitHub Secrets에 등록된 키 중 누락된 것이 있습니다.")
        print(f"현재 상태: GEMINI_KEY={'O' if GEMINI_KEY else 'X'}, TOKEN={'O' if TELE_TOKEN else 'X'}, ID={'O' if CHAT_ID else 'X'}")
    else:
        data = get_ai_data()
        if data:
            create_word_and_send(data)
        else:
            print("❌ 수집된 데이터가 없어 파일을 생성하지 않았습니다.")
