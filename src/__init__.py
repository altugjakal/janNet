from pathlib import Path

from flask import Flask
from flask_cors import CORS
from huggingface_hub import login

from src.jannet.utils.config import Config
from api.routes.search import search_bp


def create_app():

    login(token=Config.HF_TOKEN)

    root_path = Path(__file__).resolve().parent.parent

    app = Flask(__name__, template_folder=str(root_path / 'templates'))

    CORS(app)

    app.register_blueprint(search_bp, url_prefix='/search')

    return app