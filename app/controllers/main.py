from app import app
from flask import redirect
from app.utils.auth import token_required
import os

FRONTEND_URL = os.getenv('FRONTEND_URL')

@app.route('/', methods=['GET'])
def main():
    return redirect(FRONTEND_URL)