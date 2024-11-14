# client.py
import os
import requests
import json
import logging

BASE_URL = "http://127.0.0.1:5000"

# 로그인 상태 유지
token = None
is_admin = False

# 로그 파일 경로 수정 (윈도우 호환성)
log_file_path = os.path.join(os.getcwd(), 'client_activity.log')

# 로그 설정
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CLI 메뉴 함수
def main_menu():
    while True:
        print("\n1. 사용자 등록\n2. 로그인\n3. 로그아웃\n4. 이벤트 조회")
        if is_admin:
            print("5. 이벤트 생성 (관리자)\n6. 사용자 정보 삭제 (관리자)\n7. 이벤트 삭제 (관리자)\n8. 사용자 목록 조회 (관리자)")
        print("9. 티켓 예약\n10. 티켓 예약 취소\n11. 예약 현황 조회\n12. 종료")
        choice = input("원하는 기능의 번호를 입력하세요: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            logout_user()
        elif choice == '4':
            get_events()
        elif is_admin and choice == '5':
            create_event()
        elif is_admin and choice == '6':
            delete_user()
        elif is_admin and choice == '7':
            delete_event()
        elif is_admin and choice == '8':
            get_users()
        elif choice == '9':
            reserve_ticket()
        elif choice == '10':
            cancel_reservation()
        elif choice == '11':
            get_my_reservations()
        elif choice == '12':
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

# 사용자 로그인
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

# 사용자 목록 조회 (관리자)
def get_users():
    if not token:
        print("먼저 로그인하세요.")
        return
    if not is_admin:
        print("이 기능은 관리자만 사용할 수 있습니다.")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/users", cookies={"session": token})
        users = response.json().get("users", [])
        if users:
            print("\n사용자 목록:")
            for user in users:
                print(f"ID: {user['id']}, 이름: {user['username']}, 관리자 여부: {'예' if user['is_admin'] else '아니오'}")
        else:
            print("등록된 사용자가 없습니다.")
        logging.info("사용자 목록 조회 - 성공")
    except requests.RequestException as e:
        print("사용자 목록 조회 실패:", e)
        logging.error(f"사용자 목록 조회 실패: {e}")

# 사용자 정보 삭제 (관리자)
def delete_user():
    if not token:
        print("먼저 로그인하세요.")
        return
    if not is_admin:
        print("이 기능은 관리자만 사용할 수 있습니다.")
        return

    # 사용자 목록을 보여줌으로써 정확한 ID를 입력할 수 있도록 도움
    get_users()

    user_id = input("삭제할 사용자 ID를 입력하세요: ")
    try:
        response = requests.delete(f"{BASE_URL}/users/{user_id}", cookies={"session": token})
        if response.status_code == 200:
            message = response.json().get("message", "사용자 정보 삭제에 성공했습니다.")
            print(message)
            logging.info(f"사용자 삭제: ID {user_id} - {message}")
        elif response.status_code == 404:
            print("삭제할 사용자를 찾을 수 없습니다.")
            logging.warning(f"사용자 삭제 실패: ID {user_id} - 사용자 없음")
        else:
            print("사용자 정보 삭제 실패:", response.json().get("message", "알 수 없는 오류가 발생했습니다."))
            logging.error(f"사용자 정보 삭제 실패: ID {user_id} - {response.status_code}")
    except requests.RequestException as e:
        print("사용자 정보 삭제 실패:", e)
        logging.error(f"사용자 정보 삭제 실패: {e}")

# 이벤트 삭제 (관리자)
def delete_event():
    if not token:
        print("먼저 로그인하세요.")
        return
    if not is_admin:
        print("이 기능은 관리자만 사용할 수 있습니다.")
        return
    
    event_id = input("삭제할 이벤트 ID를 입력하세요: ")
    try:
        response = requests.delete(f"{BASE_URL}/events/{event_id}", cookies={"session": token})
        message = response.json().get("message", "이벤트 삭제에 성공했습니다.")
        print(message)
        logging.info(f"이벤트 삭제: ID {event_id} - {message}")
    except requests.RequestException as e:
        print("이벤트 삭제 실패:", e)
        logging.error(f"이벤트 삭제 실패: {e}")

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