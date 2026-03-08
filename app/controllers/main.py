from app import app
from flask import redirect
import os

FRONTEND_URL = os.getenv('FRONTEND_URL')

@app.route('/', methods=['GET'])
def main():
    return redirect(FRONTEND_URL)