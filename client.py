import requests

BASE_URL = "http://127.0.0.1:5000"

def register_user():
    username = input("사용자 이름을 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    try:
        response = requests.post(f"{BASE_URL}/register", json={'username': username, 'password': password})
        response.raise_for_status()
        print(response.json().get("message", "등록에 성공했습니다."))
    except requests.RequestException as e:
        print("사용자 등록 실패:", e)

def login_user():
    username = input("사용자 이름을 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    try:
        response = requests.post(f"{BASE_URL}/login", json={'username': username, 'password': password})
        response.raise_for_status()
        print(response.json().get("message", "로그인에 성공했습니다."))
    except requests.RequestException as e:
        print("로그인 실패:", e)

def view_events():
    try:
        response = requests.get(f"{BASE_URL}/events")
        response.raise_for_status()
        events = response.json().get("events", [])
        if events:
            for event in events:
                print(f"ID: {event['id']}, 이름: {event['name']}, 남은 티켓: {event['tickets_left']}")
        else:
            print("이벤트가 없습니다.")
    except requests.RequestException as e:
        print("이벤트 조회 실패:", e)

def reserve_ticket():
    user_id = input("사용자 ID를 입력하세요: ")
    event_id = input("예약할 이벤트의 ID를 입력하세요: ")
    try:
        response = requests.post(f"{BASE_URL}/reserve", json={'user_id': user_id, 'event_id': event_id})
        response.raise_for_status()
        print(response.json().get("message", "예약이 완료되었습니다."))
    except requests.RequestException as e:
        print("티켓 예약 실패:", e)

def view_reservations():
    try:
        response = requests.get(f"{BASE_URL}/reservations")
        response.raise_for_status()
        reservations = response.json().get("reservations", [])
        if reservations:
            for res in reservations:
                print(f"예약 ID: {res['id']}, 사용자 ID: {res['user_id']}, 이벤트 ID: {res['event_id']}")
        else:
            print("예약된 티켓이 없습니다.")
    except requests.RequestException as e:
        print("예약 조회 실패:", e)

def view_registered_users():
    try:
        response = requests.get(f"{BASE_URL}/users")  # 서버에서 등록된 사용자 목록을 가져오는 API
        response.raise_for_status()
        users = response.json().get("users", [])
        if users:
            print("\n등록된 사용자 목록:")
            for user in users:
                print(f"ID: {user['id']}, 사용자 이름: {user['username']}")
        else:
            print("등록된 사용자가 없습니다.")
    except requests.RequestException as e:
        print("사용자 목록 조회 실패:", e)

def show_user_menu():
    while True:
        print("\n1. 사용자 등록\n2. 사용자 목록 조회\n3. 다시 선택\n4. 메인 메뉴로 돌아가기")
        choice = input("원하는 기능의 번호를 입력하세요: ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            view_registered_users()
        elif choice == '3':
            continue  # 다시 선택을 누르면 그때그때 메뉴로 돌아감
        elif choice == '4':
            return  # 메인 메뉴로 돌아감
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

def main():
    while True:
        print("\n메뉴:\n1. 사용자 등록\n2. 사용자 로그인\n3. 이벤트 조회\n4. 티켓 예약\n5. 예약 현황 조회\n6. 종료")
        choice = input("원하는 기능의 번호를 입력하세요: ")
        
        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            view_events()
        elif choice == '4':
            reserve_ticket()
        elif choice == '5':
            view_reservations()
        elif choice == '6':
            print("프로그램을 종료합니다.")
            break
        elif choice == '7':
            show_user_menu()  # 사용자 메뉴로 가기
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

if __name__ == "__main__":
    main()
