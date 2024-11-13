# client.py
import requests
import json
import logging

BASE_URL = "http://127.0.0.1:5000"

# 로그인 상태 유지
token = None
is_admin = False

# 로그 설정
logging.basicConfig(filename='client_activity.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CLI 메뉴 함수
def main_menu():
    while True:
        print("\n1. 사용자 등록\n2. 로그인\n3. 로그아웃\n4. 이벤트 조회\n5. 이벤트 생성 (관리자)\n6. 티켓 예약\n7. 티켓 예약 취소\n8. 예약 현황 조회\n9. 종료")
        choice = input("원하는 기능의 번호를 입력하세요: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            logout_user()
        elif choice == '4':
            get_events()
        elif choice == '5':
            create_event()
        elif choice == '6':
            reserve_ticket()
        elif choice == '7':
            cancel_reservation()
        elif choice == '8':
            get_my_reservations()
        elif choice == '9':
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

# 사용자 등록
def register_user():
    username = input("사용자 이름을 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    is_admin = input("관리자 계정으로 등록하려면 1을 입력하세요 (기본값: 일반 사용자): ")
    is_admin = 1 if is_admin == '1' else 0
    
    data = {
        "username": username,
        "password": password,
        "is_admin": is_admin
    }
    try:
        response = requests.post(f"{BASE_URL}/register", json=data)
        message = response.json().get("message", "등록에 성공했습니다.")
        print(message)
        logging.info(f"사용자 등록: {username} - {message}")
    except requests.RequestException as e:
        print("사용자 등록 실패:", e)
        logging.error(f"사용자 등록 실패: {e}")

# 사용자 로그인 수정
def login_user():
    global token, is_admin
    username = input("사용자 이름을 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    
    data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=data)
        if response.status_code == 200:
            print(response.json().get("message", "로그인에 성공했습니다."))
            token = response.cookies.get('session')  # 세션 토큰 저장
            is_admin = response.json().get('is_admin', 0) == 1  # 관리자 여부 저장
            logging.info(f"사용자 로그인: {username} - 성공")
        else:
            message = response.json().get("message", "로그인 실패")
            print(message)
            logging.warning(f"사용자 로그인: {username} - {message}")
    except requests.RequestException as e:
        print("로그인 실패:", e)
        logging.error(f"로그인 실패: {e}")


# 사용자 로그아웃
def logout_user():
    global token, is_admin
    try:
        response = requests.post(f"{BASE_URL}/logout", cookies={"session": token})
        message = response.json().get("message", "로그아웃되었습니다.")
        print(message)
        logging.info("사용자 로그아웃 - 성공")
        token = None
        is_admin = False
    except requests.RequestException as e:
        print("로그아웃 실패:", e)
        logging.error(f"로그아웃 실패: {e}")

# 이벤트 조회
def get_events():
    try:
        response = requests.get(f"{BASE_URL}/events")
        events = response.json().get("events", [])
        if events:
            print("\n이벤트 목록:")
            for event in events:
                print(f"ID: {event['id']}, 이름: {event['name']}, 남은 티켓: {event['tickets_left']}")
        else:
            print("등록된 이벤트가 없습니다.")
        logging.info("이벤트 조회 - 성공")
    except requests.RequestException as e:
        print("이벤트 조회 실패:", e)
        logging.error(f"이벤트 조회 실패: {e}")

# 이벤트 생성 (관리자)
def create_event():
    if not token:
        print("먼저 로그인하세요.")
        return
    if not is_admin:
        print("이 기능은 관리자만 사용할 수 있습니다.")
        return
    
    name = input("이벤트 이름을 입력하세요: ")
    tickets_left = int(input("티켓 수량을 입력하세요: "))
    
    data = {
        "name": name,
        "tickets_left": tickets_left
    }
    try:
        response = requests.post(f"{BASE_URL}/events", json=data, cookies={"session": token})
        message = response.json().get("message", "이벤트 생성에 성공했습니다.")
        print(message)
        logging.info(f"이벤트 생성: {name} - {message}")
    except requests.RequestException as e:
        print("이벤트 생성 실패:", e)
        logging.error(f"이벤트 생성 실패: {e}")

# 티켓 예약
def reserve_ticket():
    if not token:
        print("먼저 로그인하세요.")
        return
    
    event_id = int(input("예약할 이벤트 ID를 입력하세요: "))
    try:
        response = requests.post(f"{BASE_URL}/events/{event_id}/reserve", cookies={"session": token})
        message = response.json().get("message", "티켓 예약에 성공했습니다.")
        print(message)
        logging.info(f"티켓 예약: 이벤트 ID {event_id} - {message}")
    except requests.RequestException as e:
        print("티켓 예약 실패:", e)
        logging.error(f"티켓 예약 실패: {e}")

# 티켓 예약 취소
def cancel_reservation():
    if not token:
        print("먼저 로그인하세요.")
        return
    
    event_id = int(input("취소할 이벤트 ID를 입력하세요: "))
    try:
        response = requests.delete(f"{BASE_URL}/events/{event_id}/cancel", cookies={"session": token})
        message = response.json().get("message", "티켓 예약 취소에 성공했습니다.")
        print(message)
        logging.info(f"티켓 예약 취소: 이벤트 ID {event_id} - {message}")
    except requests.RequestException as e:
        print("티켓 예약 취소 실패:", e)
        logging.error(f"티켓 예약 취소 실패: {e}")

# 예약 현황 조회
def get_my_reservations():
    if not token:
        print("먼저 로그인하세요.")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/my_reservations", cookies={"session": token})
        reservations = response.json().get("reservations", [])
        if reservations:
            print("\n나의 예약 목록:")
            for res in reservations:
                print(f"이벤트 ID: {res['event_id']}, 이벤트 이름: {res['event_name']}")
        else:
            print("예약된 이벤트가 없습니다.")
        logging.info("예약 현황 조회 - 성공")
    except requests.RequestException as e:
        print("예약 현황 조회 실패:", e)
        logging.error(f"예약 현황 조회 실패: {e}")

if __name__ == "__main__":
    main_menu()
