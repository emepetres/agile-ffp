from flask import (
    Blueprint,
    render_template,
)

bp = Blueprint("landing", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def landing():
    return render_template("landing.html")
