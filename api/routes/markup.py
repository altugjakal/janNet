from flask import render_template, Blueprint

markup_bp = Blueprint('markup_bp', __name__)

@markup_bp.route("/")
def index():
    return render_template("index.html")
