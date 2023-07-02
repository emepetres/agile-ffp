import os
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.milestone.estimation import parse_estimation

from agileffp.utils import read_yaml_file

bp = Blueprint("estimation", __name__, url_prefix="/estimation")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@bp.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            return redirect(url_for("estimation.render_chart", filename=filename))

    return render_template("estimation/landing.html")


@bp.route("/chart/<filename>")
def render_chart(filename):
    data = read_yaml_file(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    estimation = parse_estimation(data)
    info = [t for t in estimation.values()]

    capacity = CapacityTeam.parse(data)
    for t in info:
        t.compute_price(capacity.values())

    print([t.price for t in info])

    return render_template(
        "estimation/render.html",
        estimation=info,
    )
