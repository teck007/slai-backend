from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
load_dotenv()

app = Flask(__name__)
CORS(app, origins=os.getenv("FRONTEND_URL"))

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[os.getenv("LIMIT_IP_DAY"), os.getenv("LIMIT_IP_HOUR")],
    storage_uri=os.getenv("REDIS_URI")
)

from app.controllers.short import short
from app.controllers.main import main
from app.controllers.user import get_user_links, post_delete_user_links