from dotenv import load_dotenv
import os

load_dotenv()

def get_env(name: str, default=""):
    return os.getenv(name, default)
