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
from agileffp.gantt.gantt import Gantt

from agileffp.utils import read_yaml_file

bp = Blueprint("gantt", __name__, url_prefix="/gantt")


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
            return redirect(url_for("gantt.render_chart", filename=filename))

    return render_template("gantt/landing.html")


@bp.route("/chart/<filename>")
def render_chart(filename):
    data = read_yaml_file(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    gantt = Gantt.from_dict(data)
    print(gantt.tasks_assigned)

    capacity = None
    timeline_tasks = None
    if not gantt.tasks_assigned:
        capacity = CapacityTeam.parse(data)
        gantt.assign_capacity(capacity)
        timeline_tasks = [tl for c in capacity.values() for tl in c.to_timeline()]

    info = gantt.to_list()

    return render_template(
        "gantt/render.html",
        gantt=info,
        gantt_height=15 + 45 * len(info),
        timeline=timeline_tasks,
        timeline_height=55 * (len(capacity) if capacity else 0),
    )
