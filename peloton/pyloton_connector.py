import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from pprint import pprint

import requests
from constants import PELOTON_PASSWORD, PELOTON_USERNAME
from typing_extensions import Self
from pyloton_models import PelotonInstructor

BASE_URL = "https://api.onepeloton.com"
EASTERN_TIME = ZoneInfo('America/New_York')
SESSION_JSON = Path('..').resolve().joinpath('session_id.json')

@dataclass
class PelotonSessionIDToken():
    session_id: str
    user_id: str
    created_at: datetime = datetime.now(tz=EASTERN_TIME)

    def write_session_id_json(self, filename: str = SESSION_JSON) -> None:
        """ Writes this Peloton session ID token to a JSON file on the filesystem. """
        tokens_dict = asdict(self)
        tokens_dict = { x: (y.isoformat() if isinstance(y, datetime) else y) for (x, y) in tokens_dict.items() }

        print(f"\nWriting token data to {filename}...")
        with open(filename, "w") as file:
            json.dump(tokens_dict, file, indent=4)
        print("Done.")

    @classmethod
    def read_session_id_from_json(cls, filename: str = SESSION_JSON) -> Self | None:
        """ Factory method:  reads session ID from a JSON file and instantiates a new `PelotonSessionIDToken`. """
        
        print(f"\nReading tokens from {filename}...\n")

        with open(filename, "r") as file:
            tokens_dict = json.load(file)
        session_id = tokens_dict['session_id']
        user_id = tokens_dict['user_id']
        created_at = datetime.fromisoformat(tokens_dict['created_at']).astimezone(tz=EASTERN_TIME)

        session_token = cls(session_id=session_id, 
                            user_id=user_id, 
                            created_at=created_at)
        return session_token


class PylotonZMVConnector():
    def __init__(self, username: str = PELOTON_USERNAME, password: str = PELOTON_PASSWORD) -> None:
        self.username = username
        self.password = password
        self.session = requests.Session()

        try:
            self.login_token = PelotonSessionIDToken.read_session_id_from_json()
        except FileNotFoundError:
            print("JSON file not found.  Getting new login token...")
            self.get_new_login_token()
        except KeyError:
            print("Key error in JSON file.  Getting new login token...")
            self.get_new_login_token()
        else:
            self.session.cookies.set('peloton_session_id', self.login_token.session_id)

    def get_new_login_token(self) -> None:
        print("Getting new session ID and resuming in 3 seconds...")
        time.sleep(3)
        auth_login_url = f"{BASE_URL}/auth/login"
        auth_payload = {'username_or_email': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/json', 'User-Agent': 'pyloton'}
        resp = self.session.post(url=auth_login_url,json=auth_payload, headers=headers, timeout=10)
        resp.raise_for_status()
        
        self.login_token = PelotonSessionIDToken(resp.json()['session_id'], resp.json()['user_id'])
        self.login_token.write_session_id_json()
        self.session.cookies.set('peloton_session_id', self.login_token.session_id)


def main():
    pass

if __name__ == '__main__':
    main()