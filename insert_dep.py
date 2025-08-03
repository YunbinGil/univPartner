import json
import mysql.connector
import requests
import MySQLdb
import time

API_BASE_URL = 'http://api.data.go.kr/openapi/tn_pubr_public_univ_major_api'
API_KEY = 'aZcI7QFc9yUfWvmODptQxI2SMyDwOsf8i30dGPKLjvbUO7Dcj67luMuga0d9hL4hS9EKWwS9GxDnxq7O%2BtBM9w%3D%3D'

# DB 연결
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='4564',
    database='univpartner_db'
)
cursor = db.cursor()

page = 1
all_items = []

print("📦 전국 대학 학과 데이터 수집 시작")

while True:
    url = (
            f"{API_BASE_URL}"
            f"?serviceKey={API_KEY}"
            f"&pageNo={page}"
            f"&numOfRows=1000"
            f"&type=json"
        )
    start = time.time()
    
    try:
        res = requests.get(url)
        print(f"🔄 page {page} - status: {res.status_code} - 소요 시간: {time.time() - start:.2f}초")
        # print(f"🔄 page {page} - status: {res.status_code}")
    
    except requests.exceptions.Timeout:
        print("⏱ 타임아웃 발생. 요청 중단.")
        break
    except Exception as e:
        print("❌ 요청 실패:", e)
        break

    if res.status_code != 200:
        print("❌ 응답 코드 문제:", res.status_code)
        print("본문 일부:", res.text[:300])
        break

    try:
        data = res.json()
        
        header = data['response']['header']
        if header['resultCode'] != "00":
            print(f"📭 No data on page {page} - {header['resultMsg']}")
            break 
        
        items = data['response']['body']['items']
        
        if isinstance(items, dict):
            items = [items]
        
    except Exception as e:
        print("❌ JSON 파싱 실패:", e)
        print("본문 일부:", res.text[:300])
        break

    if not items:
        print("✅ 더 이상 데이터 없음. 루프 종료.")
        break

    all_items.extend(items)
    page += 1
    time.sleep(0.5)

print(f"📊 총 {len(all_items)}개 학과 불러옴")

count = 0
records = []
for item in all_items:
    try:
        # print(f"DEBUG raw item: {item}")
        univ = item.get('schlNm', '').strip()
        college = item.get('collegeNm', '').strip()
        major = item.get('scsbjtNm', '').strip()
        # campus = item.get('sggNm', '').strip()  # 시군구를 캠퍼스로 간주
        # print(f"DEBUG: univ='{univ}', college='{college}', major='{major}'")
        
        # ⛔️ "대학원" 포함된 학교명은 제외
        if "대학원" in univ:
            # print(f"🚫 대학원 포함된 학교 제외: {univ}")
            continue
        
        if not (univ and college and major):
            print("❌ 필수 필드 누락:", univ, college, major)
            continue

        if not college:
            college = "단과대학없음"

        records.append((univ, college, major))
        count += 1
    except Exception as e:
        print(f"❌ 실패 항목: {item}")
        print("에러:", e)
        
cursor.execute("TRUNCATE TABLE departments")
print("🧹 departments 테이블 초기화 완료")

records.sort(key=lambda x: (x[0], x[1], x[2])) #가나다순

cursor.executemany("""
    INSERT INTO departments (univ, college, major)
    VALUES (%s, %s, %s)
""", records)

db.commit()
cursor.close()
db.close()
print(f"✅ 총 {count}개 학과 정보 저장 완료!")