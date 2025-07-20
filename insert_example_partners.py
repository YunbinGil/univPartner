import csv
import mysql.connector

# DB 연결
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='4564',
    database='univpartner_db'
)
cur = conn.cursor()

## ✅ 혜택 형태 (BenefitTypes) 로딩
cur.execute("SELECT type_id, name FROM BenefitTypes")
benefit_type_map = {name: type_id for type_id, name in cur.fetchall()}

# ✅ 카테고리 (BenefitCategories) 로딩
cur.execute("SELECT category_id, name FROM BenefitCategories")
category_map = {name: category_id for category_id, name in cur.fetchall()}

# ✅ CSV 파일 열기 (UTF-8)
with open('partners.csv', newline='', encoding='cp949') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        name = row['name']
        address = row.get('address') or None
        scope = row.get('scope') or None
        content = row.get('content') or None
        start_date = row.get('start_date') or None
        end_date = row.get('end_date') or None

        # 🔁 category_id 가져오기
        category_name = row.get('category')
        category_id = category_map.get(category_name)

        if not category_id:
            print(f"❗ 카테고리 매칭 실패: {category_name} → {name}")
            continue

        # ✍ created_by_user_id 임시로 1 고정
        created_by_user_id = 1

        # 🔁 Partners INSERT
        cur.execute("""
            INSERT INTO Partners (name, address, scope, image_url, latitude, longitude, content, start_date, end_date, category_id, created_by_user_id)
            VALUES (%s, %s, %s, NULL, NULL, NULL, %s, %s, %s, %s, %s)
        """, (name, address, scope, content, start_date, end_date, category_id, created_by_user_id))

        partner_id = cur.lastrowid  # 최근 삽입된 partner_id 가져오기

        # 🔁 혜택 타입 여러 개 처리
        type_str = row.get('type', '')
        for t in [x.strip() for x in type_str.split(',')]:
            type_id = benefit_type_map.get(t)
            if type_id:
                cur.execute("""
                    INSERT INTO PartnerBenefitTypes (partner_id, type_id)
                    VALUES (%s, %s)
                """, (partner_id, type_id))
            else:
                print(f"⚠️ 알 수 없는 혜택 type: '{t}' → {name}")

# ✅ commit & close
conn.commit()
cur.close()
conn.close()

print("✅ 모든 제휴 업체 삽입 완료!")