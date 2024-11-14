# server.py
import os
from flask import Flask, request, jsonify, session
import sqlite3
from flask_bcrypt import Bcrypt
from flask import session
from functools import wraps
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션 관리를 위해 필요한 비밀 키 설정
bcrypt = Bcrypt(app)

# 데이터베이스 파일 경로 수정 (윈도우 호환성)
db_file_path = os.path.join(os.getcwd(), 'events.db')

# 데이터베이스 연결
def connect_db():
    conn = sqlite3.connect(db_file_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 딕셔너리 스타일로 데이터 가져오기
    return conn

# 초기 데이터베이스 설정
def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0  -- 관리자 여부를 나타내는 컬럼 (0: 일반 사용자, 1: 관리자)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tickets_left INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')
    conn.commit()
    conn.close()

# 로그인 필요 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': '로그인이 필요합니다.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 티켓 예약 시 동시성 문제 방지를 위한 Lock 객체 생성
reserve_lock = threading.Lock()

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Flask server! This is the home page.", 200

# 사용자 등록
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', 0)

    if not username or not password:
        return jsonify({'message': '사용자 이름과 비밀번호가 필요합니다.'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)', (username, hashed_password, is_admin))
    conn.commit()
    conn.close()

    return jsonify({'message': '사용자 등록에 성공했습니다.'}), 201

# 사용자 로그인
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, password, is_admin FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['is_admin'] = user['is_admin']
        return jsonify({'message': '로그인에 성공했습니다.', 'is_admin': user['is_admin']}), 200
    else:
        return jsonify({'message': '사용자 이름 또는 비밀번호가 잘못되었습니다.'}), 401

# 사용자 로그아웃
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'message': '로그아웃되었습니다.'}), 200

# 사용자 목록 조회 (관리자 전용)
@app.route('/users', methods=['GET'])
@login_required
def get_users():
    if not session.get('is_admin'):
        return jsonify({'message': '관리자 권한이 필요합니다.'}), 403
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, is_admin FROM users')
    users = cursor.fetchall()
    conn.close()

    users_list = [{'id': user['id'], 'username': user['username'], 'is_admin': user['is_admin']} for user in users]
    return jsonify({'users': users_list}), 200

# 사용자 삭제 (관리자 전용)
@app.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not session.get('is_admin'):
        return jsonify({'message': '관리자 권한이 필요합니다.'}), 403

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({'message': '삭제할 사용자를 찾을 수 없습니다.'}), 404

    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': '사용자 정보 삭제에 성공했습니다.'}), 200

# 이벤트 생성 (관리자 전용)
@app.route('/events', methods=['POST'])
@login_required
def create_event():
    if not session.get('is_admin'):
        return jsonify({'message': '관리자 권한이 필요합니다.'}), 403
    
    data = request.json
    name = data.get('name')
    tickets_left = data.get('tickets_left')
    
    if not name or tickets_left is None:
        return jsonify({'message': '이벤트 이름과 티켓 수량이 필요합니다.'}), 400
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (name, tickets_left) VALUES (?, ?)', (name, tickets_left))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '이벤트가 성공적으로 생성되었습니다.'}), 201

# 이벤트 목록 조회
@app.route('/events', methods=['GET'])
def get_events():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events')
    events = cursor.fetchall()
    conn.close()

    events_list = [{'id': event['id'], 'name': event['name'], 'tickets_left': event['tickets_left']} for event in events]
    return jsonify({'events': events_list}), 200

# 티켓 예약
@app.route('/events/<int:event_id>/reserve', methods=['POST'])
@login_required
def reserve_ticket(event_id):
    user_id = session['user_id']
    with reserve_lock:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT tickets_left FROM events WHERE id = ?', (event_id,))
        event = cursor.fetchone()
        if event and event['tickets_left'] > 0:
            cursor.execute('INSERT INTO reservations (user_id, event_id) VALUES (?, ?)', (user_id, event_id))
            cursor.execute('UPDATE events SET tickets_left = tickets_left - 1 WHERE id = ?', (event_id,))
            conn.commit()
            conn.close()
            return jsonify({'message': '티켓 예약에 성공했습니다.'}), 200
        else:
            conn.close()
            return jsonify({'message': '티켓이 매진되었습니다.'}), 400

# 티켓 예약 취소
@app.route('/events/<int:event_id>/cancel', methods=['DELETE'])
@login_required
def cancel_reservation(event_id):
    user_id = session['user_id']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM reservations WHERE user_id = ? AND event_id = ?', (user_id, event_id))
    cursor.execute('UPDATE events SET tickets_left = tickets_left + 1 WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '티켓 예약 취소에 성공했습니다.'}), 200

# 나의 예약 현황 조회
@app.route('/my_reservations', methods=['GET'])
@login_required
def get_my_reservations():
    user_id = session['user_id']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT events.id, events.name FROM reservations
        JOIN events ON reservations.event_id = events.id
        WHERE reservations.user_id = ?
    ''', (user_id,))
    reservations = cursor.fetchall()
    conn.close()

    return jsonify({'reservations': [{'event_id': res['id'], 'event_name': res['name']} for res in reservations]}), 200

# 이벤트 수정 (관리자 전용)
@app.route('/events/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    if not session.get('is_admin'):
        return jsonify({'message': '관리자 권한이 필요합니다.'}), 403
    
    data = request.json
    name = data.get('name')
    tickets_left = data.get('tickets_left')
    
    conn = connect_db()
    cursor = conn.cursor()
    if name:
        cursor.execute('UPDATE events SET name = ? WHERE id = ?', (name, event_id))
    if tickets_left is not None:
        cursor.execute('UPDATE events SET tickets_left = ? WHERE id = ?', (tickets_left, event_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '이벤트가 성공적으로 수정되었습니다.'}), 200

# 이벤트 삭제 (관리자 전용)
@app.route('/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    if not session.get('is_admin'):
        return jsonify({'message': '관리자 권한이 필요합니다.'}), 403
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '이벤트가 성공적으로 삭제되었습니다.'}), 200

# 특정 이벤트의 예약자 목록 조회 (관리자 전용)
@app.route('/events/<int:event_id>/reservations', methods=['GET'])
@login_required
def get_event_reservations(event_id):
    if not session.get('is_admin'):
        return jsonify({'message': '관리자 권한이 필요합니다.'}), 403
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT users.id, users.username FROM reservations
        JOIN users ON reservations.user_id = users.id
        WHERE reservations.event_id = ?
    ''', (event_id,))
    reservations = cursor.fetchall()
    conn.close()
    
    return jsonify({'reservations': [{'id': res['id'], 'username': res['username']} for res in reservations]}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
