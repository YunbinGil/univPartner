from flask import Blueprint,  request, render_template, redirect, url_for, jsonify, request, session
from app import mysql
import os
import requests #외부 api요청보내기 용, flask의 request는 사용자가 보낸 요청 받기용임

#API_BASE_URL = 'http://api.data.go.kr/openapi/tn_pubr_public_univ_major_api'
API_KEY = 'aZcI7QFc9yUfWvmODptQxI2SMyDwOsf8i30dGPKLjvbUO7Dcj67luMuga0d9hL4hS9EKWwS9GxDnxq7O%2BtBM9w%3D%3D'

main = Blueprint('main', __name__, template_folder=os.path.join(os.path.dirname(__file__), '../templates'))
#BluePrint = 일종의 "라우터 묶음.
#여러개의 라우트를 그룹으로 만들어서 앱에 붙일 수 ㅇㅇ
#즉 로그인/회원가입 등 기능을 각가 다른 blueprint로 나눠서 코딩딩

#나중엔 /signup, /login 등 여기나 다른파일에서 만들면 됨
@main.route('/') #디폴트
def index():
    return redirect(url_for('main.login'))
    

@main.route('/test-db')
def test_db():
    cur = mysql.connection.cursor()
    cur.execute("SELECT NOW() AS time")
    result = cur.fetchone()
    return f"DB 연결 성공! 현재 시간: {result['time']}"

@main.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        loginID = request.form['loginID']
        password = request.form['password']  # 암호화는 나중에 추가 가능!

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (loginID, password) VALUES (%s, %s)",
                    (loginID, password))
        mysql.connection.commit()
        cur.close()
        #url_for인자넣을때 -대신 함수명인 _로 넣어야됨!
        return redirect(url_for('main.signup_profile', loginID=loginID))  # loginID 전달해도 되고 안 해도 됨
    return render_template('signup.html')

@main.route('/check-id')
def check_id():
    loginID = request.args.get('loginID')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE loginID = %s", (loginID,))
    user = cur.fetchone()
    cur.close()
    return jsonify({'exists': bool(user)})

@main.route('/signup-profile', methods=['GET','POST'])
def signup_profile():
    if request.method == "POST":
        nickname = request.form['nickname']
        univ = request.form['univ']
        campus = request.form['campus']
        major = request.form['major']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (nickname, univ, campus, major) VALUES (%s, %s, %s, %s)",
                    (nickname, univ, campus, major))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('main.home')) 
    print("🔄 학과 테이블 업데이트 점검 중...")
    fetch_and_update_departments()
    return render_template('signup_profile.html')

@main.route('/home', methods=['GET','POST'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginID = request.form['loginID']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Users WHERE loginID = %s AND password = %s", (loginID, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user['user_id']  # 로그인 상태 저장
            return redirect(url_for('main.home'))  # 로그인 성공 시 이동
        else:
            return "로그인 실패: 아이디 또는 비밀번호가 틀렸습니다"

    return render_template('login.html')

@main.route('/check-nickname')
def check_nickname():
    nickname = request.args.get('nickname')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE nickname = %s", (nickname,))
    user = cur.fetchone()
    cur.close()
    return jsonify({'exists': bool(user)})

# 공공데이터 open api활용  --

#학과정보 fetch함수
def fetch_and_update_departments():
    print("📦 전체 학과 데이터 수집 시작")

    API_BASE_URL = "http://api.data.go.kr/openapi/tn_pubr_public_univ_major_api"
    page = 1
    all_items = []

    while True:
        url = (
            f"{API_BASE_URL}"
            f"?serviceKey={API_KEY}&returnType=json&pageNo={page}&numOfRows=1000&type=json"
        )

        print(url)

        res = requests.get(url)
        print(f"🔄 page {page} - status: {res.status_code}")

        if res.status_code != 200:
            print("❌ 요청 실패:", res.status_code)
            print(res.text[:300])
            break

        try:
            data = res.json()
            items = data['response']['body']['items']
        except Exception as e:
            print("❌ JSON 파싱 실패:", e)
            print("본문 일부:", res.text[:300])
            break

        if not items:
            print("✅ 더 이상 데이터 없음. 루프 종료.")
            break

        all_items.extend(items)
        page += 1

    if not all_items:
        print("⚠️ 가져온 데이터 없음")
        return


    new_date = items[0].get('CRTR_YMD')

    # 기존 테이블에서 기준일자 조회
    cur = mysql.connection.cursor()
    cur.execute("SELECT MAX(updated_at) FROM departments")
    existing_date = cur.fetchone()['MAX(updated_at)']

    if existing_date is None or str(existing_date) < new_date:
        print('학과 데이터 갱신됨. DB 새로 저장 시작')
        cur.execute("DELETE FROM departments")
        for item in items:
            cur.execute("""
                INSERT INTO departments (univ, college, major, updated_at)
                VALUES (%s, %s, %s, %s)
            """, (
                item.get('SCHL_NM'),
                item.get('COLLEGE_NM'),
                item.get('SCSBJT_NM'),
                item.get('CRTR_YMD')
            ))
        mysql.connection.commit()
    cur.close()

@main.route('/api/univ-list')
def univ_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT univ FROM departments")
    rows = cur.fetchall()
    cur.close()
    return jsonify([row['univ'] for row in rows])

@main.route('/api/college-list')
def college_list():
    univ = request.args.get('univ')
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT DISTINCT college FROM departments " \
        "WHERE univ = %s", (univ,))
    rows = cur.fetchall()
    cur.close()
    return jsonify([row['college'] for row in rows])

@main.route('/api/major-list')
def major_list():
    univ = request.args.get('univ')
    college = request.args.get('college')
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT DISTINCT major FROM departments " \
        "WHERE univ = %s AND college = %s",
        (univ, college))
    rows = cur.fetchall()
    cur.close()
    return jsonify([row['major'] for row in rows])

@main.route('/mypage-edit') #마이페이지 - 회원정보수정 
def edit_info():
    print("🔄 학과 테이블 업데이트 점검 중...")
    fetch_and_update_departments()
    ...


@main.route('/menu', methods=['GET','POST'])
def menu():
    return render_template('menu.html')

@main.route('/fetch/editor-info', methods=['GET'])
def fetch_editor_info():
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401
    
    user_id = session['user_id']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user  = cur.fetchone()

    if not user:
        cur.close()
        return jsonify({'error': '유저 정보 없음'}), 403

    if user['role'] == 'admin':
        cur.close()
        return jsonify({'role': 'admin'})

    if user['role'] == 'editor':
        cur.execute("SELECT * FROM editors WHERE submitted_by = %s AND status = 'approved'", (user_id,))
        editor = cur.fetchone()
        cur.close()

        if editor:
            return jsonify(editor)

    return jsonify({'error': '편집자 승인 필요'}), 403

@main.route('/benefit/add', methods=['GET','POST'])
def add_benefit():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    #fetch_and_update_departments() #api연결후

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if request.method == 'POST':
        store_name = request.form.get('store_name')
        address = request.form.get('address')
        content = request.form.get('content')
        type_ids = request.form.getlist('type_ids')  # 체크박스는 여러 개
        category_id = request.form.get('category')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        
        scope = None

        if user['role'] == 'editor':
            # 🧠 editor_id 가져오기
            cur.execute("SELECT * FROM editors WHERE submitted_by = %s AND status = 'approved'", (user_id,))
            editor = cur.fetchone()
            if not editor:
                cur.close()
                return "❌ 편집자 승인 상태가 아닙니다."
            # editor_id = editor['editor_id']
            scope = editor['aff_council']
            scopeStr = editor['univ']
            if(scope == 'college'):
                scopeStr += f" { editor['college']}" 
            if(scope == 'major'):
                scopeStr += f" { editor['college']} {editor['major']}" 

        elif user['role'] == 'admin':
            univ = request.form.get('scope_univ')
            college = request.form.get('scope_college')
            major = request.form.get('scope_major')

            if not univ:
                return "❌ 범위 지정 오류: 대학교는 필수입니다."

            scopeStr = univ
            if college:
                scopeStr += f" {college}"
            if major:
                scopeStr += f" {college} {major}"
        else:
            cur.close()
            return "❌ 권한 없음: 편집자 또는 관리자만 등록 가능"
        

        try:
            # ✅ 1. partners 테이블에 insert
            cur.execute("""
                INSERT INTO partners 
                (name, address, content, scope, start_date, end_date, category_id, created_by_user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (store_name, address, content, scopeStr, start_date, end_date, category_id, user_id))
            mysql.connection.commit()

            partner_id = cur.lastrowid

            # ✅ 2. PartnerBenefitTypes 연결테이블에 insert
            for type_id in type_ids:
                cur.execute("""
                    INSERT INTO PartnerBenefitTypes (partner_id, type_id)
                    VALUES (%s, %s)
                """, (partner_id, type_id))

            mysql.connection.commit()
            cur.close()

            print("✅ 혜택 등록 완료:", store_name)
            return redirect(url_for('main.benefit_edit_success'))

        except Exception as e:
            print("❌ 오류 발생:", e)
            mysql.connection.rollback()
            return "서버 오류 발생"
    
    # GET 요청 시: BenefitTypes 불러와서 템플릿에 넘기기

    type_name_kor = {
        'discount': '할인',
        'event': '이벤트',
        'freshman': '새내기 혜택',
        'offer': '제공'
    }
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM BenefitTypes")
    benefit_types = cur.fetchall()
    
    return render_template('benefit_add.html', benefit_types=benefit_types)

@main.route('/benefit/edit_success', methods=['GET','POST'])
def benefit_edit_success():
    return render_template('benefit_edit_success.html')

@main.route('/benefit/edit', methods=['GET','POST'])
def edit_benefit():
    return render_template('benefit_edit.html')

@main.route('/fetch/partners-by-scope', methods=['GET'])
def fetch_partners_by_scope():
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        cur.close()
        return jsonify({'error': '유저 없음'}), 403

    if user['role'] == 'editor':
        cur.execute("SELECT * FROM editors WHERE submitted_by = %s AND status = 'approved'", (user_id,))
        editor = cur.fetchone()
        if not editor:
            cur.close()
            return jsonify({'error': '편집자 인증 필요'}), 403

        # ✅ fullScope 만들기
        full_scope = editor['univ']
        if editor['aff_council'] == 'college':
            full_scope += f" {editor['college']}"
        elif editor['aff_council'] == 'major':
            full_scope += f" {editor['college']} {editor['major']}"

        # ✅ JOIN 쿼리로 모든 필요한 정보 가져오기
        query = """
            SELECT 
                p.partner_id,
                p.name,
                p.address,
                p.content,
                p.scope,
                p.start_date,
                p.end_date,
                p.category_id,
                bc.name AS category_name,
                GROUP_CONCAT(bt.name SEPARATOR ', ') AS benefit_types
            FROM partners p
            LEFT JOIN BenefitCategories bc ON p.category_id = bc.category_id
            LEFT JOIN PartnerBenefitTypes pbt ON p.partner_id = pbt.partner_id
            LEFT JOIN BenefitTypes bt ON pbt.type_id = bt.type_id
            WHERE p.scope = %s
            GROUP BY p.partner_id
            ORDER BY p.start_date DESC
        """
        cur.execute(query, (full_scope,))
        partners = cur.fetchall()
        cur.close()

        return jsonify(partners)

    cur.close()
    return jsonify({'error': '접근 권한 없음'}), 403

@main.route('/benefit/edit/form')
def benefit_edit_form():
    return render_template('benefit_edit_form.html')

@main.route('/benefit/update', methods=['POST'])
def update_benefit():
    partner_id = request.form.get('partner_id')
    store_name = request.form.get('store_name')
    address = request.form.get('address')
    content = request.form.get('content')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    category_id = request.form.get('category')
    type_ids = request.form.getlist('type_ids')

    if not partner_id:
        return "❌ 혜택 ID 없음", 400

    try:
        cur = mysql.connection.cursor()

        # ✅ partners 테이블 업데이트
        cur.execute("""
            UPDATE partners
            SET name = %s, address = %s, content = %s,
                start_date = %s, end_date = %s, category_id = %s
            WHERE partner_id = %s
        """, (store_name, address, content, start_date, end_date, category_id, partner_id))

        # ✅ 연결 테이블 싹 지우고 다시 넣기
        cur.execute("DELETE FROM PartnerBenefitTypes WHERE partner_id = %s", (partner_id,))
        for type_id in type_ids:
            cur.execute("""
                INSERT INTO PartnerBenefitTypes (partner_id, type_id)
                VALUES (%s, %s)
            """, (partner_id, type_id))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main.benefit_edit_success'))

    except Exception as e:
        print("❌ 수정 실패:", e)
        mysql.connection.rollback()
        return "서버 오류 발생", 500

@main.route('/fetch/scope-info', methods=['GET'])
def fetch_scope_info():
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'error': '유저 정보 없음'}), 403

    return jsonify({
        'role': user['role'],
        'univ': user['univ'],
        'college': user['college'],
        'major': user['major']
    })

@main.route('/benefit/types', methods=['GET'])
def get_benefit_types():
    cur = mysql.connection.cursor()
    cur.execute("SELECT type_id, name FROM BenefitTypes")
    types = cur.fetchall()
    cur.close()
    return jsonify(types)

@main.route('/search-results', methods=['POST'])
def search_results():
    import json
    keyword = request.form.get('keyword', '').strip()
    target = request.form.get('target')  # name or content
    scopes_str = request.form.get('scopes')
    category = request.form.get('category')
    type_ids_str = request.form.get('type_ids')  # JSON string

    try:
        type_ids = json.loads(type_ids_str) if type_ids_str else []
    except:
        type_ids = []

    try:
        scopes = json.loads(scopes_str) if scopes_str else []
    except:
        scopes = []

    # ✅ 쿼리 만들기
    query = """
        SELECT 
            p.*, 
            bc.name AS category_name,
            GROUP_CONCAT(bt.name SEPARATOR ', ') AS benefit_types
        FROM partners p
        LEFT JOIN BenefitCategories bc ON p.category_id = bc.category_id
        LEFT JOIN PartnerBenefitTypes pbt ON p.partner_id = pbt.partner_id
        LEFT JOIN BenefitTypes bt ON pbt.type_id = bt.type_id
        WHERE 1=1
    """
    params = []

    if scopes:
        placeholders = ', '.join(['%s'] * len(scopes))
        query += f" AND p.scope IN ({placeholders})"
        params.extend(scopes)

    if category and category != 'null':
        query += " AND bc.name = %s"
        params.append(category)

    if type_ids:
        placeholders = ', '.join(['%s'] * len(type_ids))
        query += f""" AND p.partner_id IN (
            SELECT partner_id 
            FROM PartnerBenefitTypes 
            WHERE type_id IN ({placeholders})
        )"""
        params.extend(type_ids)

    if keyword and target in ('name', 'content'):
        query += f" AND p.{target} LIKE %s"
        params.append(f"%{keyword}%")
    elif keyword and target == 'all':
        query += " AND (p.name LIKE %s OR p.content LIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    query += " GROUP BY p.partner_id ORDER BY p.start_date DESC"

    print("🔍 최종 쿼리:", query)
    print("🔍 파라미터:", params)
    
    cur = mysql.connection.cursor()
    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
        
    return jsonify(results)

@main.route('/search', methods=['GET','POST'])
def search():
    keyword = request.form.get('keyword', '').strip() if request.method == 'POST' else ''
    return render_template('search.html', keyword=keyword)

@main.route('/map', methods=['GET','POST'])
def map():
    return render_template('map.html')

@main.route('/bookmark')
def bookmark():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.*, 
            bc.name AS category_name,
            GROUP_CONCAT(bt.name SEPARATOR ', ') AS benefit_types
        FROM Bookmarks b
        JOIN Partners p ON b.partner_id = p.partner_id
        LEFT JOIN BenefitCategories bc ON p.category_id = bc.category_id
        LEFT JOIN PartnerBenefitTypes pbt ON p.partner_id = pbt.partner_id
        LEFT JOIN BenefitTypes bt ON pbt.type_id = bt.type_id
        WHERE b.user_id = %s
        GROUP BY p.partner_id
        ORDER BY p.start_date DESC
    """, (user_id,))
    bookmarks = cur.fetchall()
    cur.close()

    return render_template('bookmark.html', bookmarks=bookmarks)

@main.route('/bookmark/toggle', methods=['POST'])
def toggle_bookmark():
    if 'user_id' not in session:
        return jsonify({'error': '로그인 필요'}), 401

    user_id = session['user_id']
    partner_id = request.form.get('partner_id')

    if not partner_id:
        return jsonify({'error': 'partner_id 없음'}), 400

    cur = mysql.connection.cursor()

    # 존재하는지 확인
    cur.execute("SELECT * FROM Bookmarks WHERE user_id = %s AND partner_id = %s", (user_id, partner_id))
    existing = cur.fetchone()

    if existing:
        cur.execute("DELETE FROM Bookmarks WHERE user_id = %s AND partner_id = %s", (user_id, partner_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'status': 'removed'})
    else:
        cur.execute("INSERT INTO Bookmarks (user_id, partner_id) VALUES (%s, %s)", (user_id, partner_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'status': 'added'})



@main.route('/mypage', methods=['GET','POST'])
def mypage():
    return render_template('mypage.html')

@main.route('/recent', methods=['GET','POST'])
def recent():
    return render_template('recent.html')
