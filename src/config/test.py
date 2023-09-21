from dotenv import load_dotenv
import os

load_dotenv()

mariadb_user = os.getenv("MARIADB_USERNAME_PYTHON")

print(mariadb_user)