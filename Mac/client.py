# client.py
import requests

BASE_URL = "http://127.0.0.1:5000"

def register_user():
    while True:
        print("\n1. 사용자 등록\n2. 등록자 확인\n3. 목록으로 돌아가기")
        choice = input("원하는 기능의 번호를 입력하세요: ")

        if choice == '1':
            username = input("사용자 이름을 입력하세요: ")
            password = input("비밀번호를 입력하세요: ")
            try:
                response = requests.post(f"{BASE_URL}/register", json={'username': username, 'password': password})
                response.raise_for_status()
                print(response.json().get("message", "등록에 성공했습니다."))
            except requests.RequestException as e:
                print("사용자 등록 실패:", e)
        
        elif choice == '2':
            view_registered_users()  # 등록된 사용자 목록을 조회하는 기능을 호출
        
        elif choice == '3':
            return  # 목록으로 돌아가기
        
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

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

def login_user():
    username = input("사용자 이름을 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    try:
        response = requests.post(f"{BASE_URL}/login", json={'username': username, 'password': password})
        response.raise_for_status()
        print(response.json().get("message", "로그인에 성공했습니다."))
    except requests.RequestException as e:
        print("로그인 실패:", e)

if __name__ == "__main__":
    while True:
        print("\n1. 사용자 등록\n2. 로그인\n3. 종료")
        choice = input("원하는 기능의 번호를 입력하세요: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            break
        else:
            print("잘못된 입력입니다. 다시 시도하세요.")

