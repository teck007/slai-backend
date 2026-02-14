from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
CORS(app)

from app.controllers.short import short
from app.controllers.main import main