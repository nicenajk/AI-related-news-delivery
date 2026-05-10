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
    # 모델명을 'gemini-1.5-flash-latest'로 구체화하여 경로 오류를 방지합니다.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    reports = []
    print(f"🔍 데이터 수집 시작 (타겟 모델: gemini-1.5-flash-latest)")
    
    for kw in keywords:
        prompt = f"30년 경력 경영자 관점에서 '{kw}' 관련 최신 트렌드 1개를 제목, 3줄 요약, 경영 인사이트 순으로 정리해줘."
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            res = requests.post(url, headers=headers, json=data, timeout=60)
            
            # 만약 1.5-flash가 실패하면 1.5-pro로 한 번 더 시도 (백업 로직)
            if res.status_code != 200:
                print(f"⚠️ {kw} 기본 모델 실패, 백업 모델로 재시도 중...")
                backup_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_KEY}"
                res = requests.post(backup_url, headers=headers, json=data, timeout=60)

            res.raise_for_status()
            content = res.json()['candidates'][0]['content']['parts'][0]['text']
            reports.append(content)
            print(f"✅ '{kw}' 분석 완료")
        except Exception as e:
            print(f"❌ '{kw}' 수집 실패: {e}")
            continue
    return reports

def create_word_and_send(results):
    # Word 파일 생성
    date_str = datetime.now().strftime('%m%d')
    file_name = f"AI_Report_{date_str}.docx"
    doc = Document()
    doc.add_heading('최장규 대표의 AI 비즈니스 인텔리전스', 0)
    doc.add_heading(f"발행일: {datetime.now().strftime('%Y-%m-%d')}", level=1)
    
    for r in results:
        doc.add_paragraph(r)
        doc.add_paragraph("-" * 50)
    doc.save(file_name)
    print(f"📂 Word 파일 생성 완료: {file_name}")

    # 텔레그램 전송
    send_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendDocument"
    try:
        with open(file_name, 'rb') as f:
            payload = {'chat_id': CHAT_ID, 'caption': f"📅 {datetime.now().strftime('%Y-%m-%d')} AI 리포트"}
            files = {'document': f}
            response = requests.post(send_url, data=payload, files=files)
            if response.status_code == 200:
                print("✨ 텔레그램 리포트 배달 성공!")
            else:
                print(f"❌ 전송 에러: {response.text}")
    except Exception as e:
        print(f"❌ 전송 오류: {e}")

if __name__ == "__main__":
    if all([GEMINI_KEY, TELE_TOKEN, CHAT_ID]):
        data = get_ai_data()
        if data:
            create_word_and_send(data)
        else:
            print("❌ 수집 데이터 없음")
    else:
        print("❌ 설정값 누락")
