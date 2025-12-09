from dotenv import load_dotenv
import os

load_dotenv()

def get_env(name: str, default=None):
    return os.getenv(name, default)
