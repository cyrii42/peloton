import requests
import time

from constants import PELOTON_PASSWORD, PELOTON_USERNAME, PELOTON_USER_ID

BASE_URL = "https://api.onepeloton.com"

# user id d181e93bdc6c42d3b388a8e72c3b62a6
# session id f27f987482584fa283cf1fc99486bc44

SESSION_ID = '135cbf06d25849a4beac7510d9395b26'


class PelotonLoginException(Exception):
    pass

class PylotonZMV():
    def __init__(self, username: str, password: str, user_id: str = None, session_id: str = None):
        self.username = username
        self.password = password
        self.session = requests.Session()

        if session_id is None:
            resp = self.login()
            # self.session_id = resp.json()['session_id']
            # self.user_id = resp.json()['user_id']
            # self.session.cookies.set('peloton_session_id', self.session_id)
        else:
            self.session_id = session_id
            self.session.cookies.set('peloton_session_id', self.session_id)
            self.user_id = (user_id if user_id is not None
                                    else self.get_user_id())  

        self.total_workouts = None
        # Dictionary for caching Instructor IDs
        self.instructor_id_dict = {}
        self.tried_once_already = False

    def login(self) -> requests.Response:
        auth_login_url = f"{BASE_URL}/auth/login"
        auth_payload = {'username_or_email': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/json', 'User-Agent': 'pyloton'}
        resp = self.session.post(url=auth_login_url, 
                                                    json=auth_payload, 
                                                    headers=headers, 
                                                    timeout=10)
        resp.raise_for_status()
        self.session_id = resp.json()['session_id']
        self.user_id = resp.json()['user_id']
        self.session.cookies.set('peloton_session_id', self.session_id)
        return resp

    def get_user_id(self) -> str:
        resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
        resp.raise_for_status()
        return resp.json()["id"]

    def get_total_workouts(self) -> int:
        try:
            resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
            resp.raise_for_status()
            return resp.json()["total_workouts"]
        except requests.HTTPError:
            if self.tried_once_already:
                print("Two login errors -- exiting now.")
                exit()
            else:
                print("Login error.  Getting new session ID and trying again in 5 seconds...")
                self.tried_once_already = True
                time.sleep(5)
                
                resp = self.login()
                self.session_id = resp.json()['session_id']
                self.user_id = resp.json()['user_id']
                self.session.cookies.set('peloton_session_id', self.session_id)

                resp = self.session.get(f"{BASE_URL}/api/me", timeout=10)
                return resp.json()["total_workouts"]
        

    def get_workout_ids(self, num_workouts: int = None) -> list[str]:
        if num_workouts is None:
            num_workouts = (self.get_total_workouts() if self.total_workouts is None 
                                                    else self.total_workouts)

        limit = 100
        pages = num_workouts // limit
        rem = num_workouts % limit

        base_workout_url = f"{BASE_URL}/api/user/{self.user_id}/workouts?sort_by=-created"

        workout_list = []
        current_page = 0

        while current_page < pages:
            url = "%s&page=%s&limit=%s" % (
                base_workout_url,
                current_page,
                limit,
            )
            resp = self.s.get(url, timeout=10).json()
            workout_list.extend(resp["data"])
            current_page += 1

        # if we have a remainder to fetch, then do another
        # call and extend on only that numbder of results
        if rem != 0:
            url = "%s&page=%s&limit=%s" % (
                base_workout_url,
                current_page,
                limit,
            )
            resp = self.s.get(url, timeout=10).json()
            workout_list.extend(resp["data"][0:rem])

        return workout_list


def main():
    pass
    pyloton = PylotonZMV(PELOTON_USERNAME, PELOTON_PASSWORD,
                         user_id=PELOTON_USER_ID, session_id=SESSION_ID)
    print(pyloton.session.cookies.get_dict())
    print(pyloton.get_total_workouts())
    print(f"Session ID: {pyloton.session_id}")


if __name__ == '__main__':
    main()