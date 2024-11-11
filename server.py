from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# 데이터베이스 연결
def connect_db():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

# 데이터베이스 초기화
def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        tickets_left INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        event_id INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(event_id) REFERENCES events(id))''')
    conn.commit()
    conn.close()


# 이벤트 추가
@app.route('/event', methods=['POST'])
def add_event():
    data = request.json
    name = data['name']
    tickets_left = data['tickets_left']
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO events (name, tickets_left) VALUES (?, ?)', (name, tickets_left))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '이벤트가 추가되었습니다.'})



@app.route('/')
def index():
    return '서버가 정상적으로 작동 중입니다!'

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return jsonify({'message': '사용자가 등록되었습니다.'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': '이미 등록된 사용자입니다.'}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'message': '로그인 성공'}), 200
    else:
        return jsonify({'message': '사용자 이름 또는 비밀번호가 잘못되었습니다.'}), 400

@app.route('/events', methods=['GET'])
def get_events():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events')
    events = cursor.fetchall()
    conn.close()
    
    return jsonify({'events': [dict(event) for event in events]}), 200

@app.route('/reserve', methods=['POST'])
def reserve_ticket():
    data = request.json
    user_id = data['user_id']
    event_id = data['event_id']
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events WHERE id=?', (event_id,))
    event = cursor.fetchone()
    
    if event and event['tickets_left'] > 0:
        cursor.execute('UPDATE events SET tickets_left=tickets_left-1 WHERE id=?', (event_id,))
        cursor.execute('INSERT INTO reservations (user_id, event_id) VALUES (?, ?)', (user_id, event_id))
        conn.commit()
        conn.close()
        return jsonify({'message': '예약이 완료되었습니다.'}), 200
    else:
        conn.close()
        return jsonify({'message': '이벤트 예약이 불가능합니다.'}), 400

@app.route('/reservations', methods=['GET'])
def get_reservations():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reservations')
    reservations = cursor.fetchall()
    conn.close()
    
    return jsonify({'reservations': [dict(res) for res in reservations]}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
