from datetime import datetime

from fasthtml.common import (
    FormData,
    Request,
    add_toast,
)

from agileffp.monitor import controller as monitor_controller
from agileffp.project import model, view

_render_target = None


def init(router, endpoints, render_target: str):
    global _render_target
    _render_target = render_target

    @router.get(endpoints.LIST.value)
    def list_all():
        return list_projects()

    @router.get(endpoints.NEW_PROJECT.value)
    def new_project_dialog():
        return view.render_new_project_dialog(_render_target)

    @router.post(endpoints.CREATE.value)
    async def create_project(request: Request):
        form: FormData = await request.form()
        name = form.get("name")
        description = form.get("description")

        if not name or not description:
            add_toast(request.session,
                      "Name and description are required", "error")
            return

        model.create_project(name, description)

        add_toast(request.session, "Project created successfully!", "success")

        return list_projects()

    @router.post(endpoints.DELETE.value)
    async def delete_project(request: Request):
        form: FormData = await request.form()
        name = form.get("name")

        if not name:
            add_toast(request.session, "Project name is required", "error")
            return

        model.delete_project(name)
        add_toast(request.session, "Project deleted successfully!", "success")

        return list_projects()

    @router.get(endpoints.GET.value + "{name}")
    def get_project(name: str, session):
        project = model.get_project(name)
        if not project:
            add_toast(session, f"Project {name} not found", "error")
            return list_projects()

        return monitor_controller.index(name)


def list_projects():
    projects = model.get_projects()
    return view.render_projects(projects, _render_target)


def get_project_context(name: str, version: str = None):
    version, yaml_content, prev_version, next_version = model.get_yaml_version_context(name, version)
    return version, yaml_content, prev_version, next_version


def update_project(name: str, yaml_content: str):
    # Create a new version with the updated content
    return model.update_project(name, yaml_content)


def save_project_version(name: str, yaml_content: str, version_name: str, version_date: datetime):
    project = model.get_project(name)
    if not project:
        return False

    # Create a new version with the provided name and date
    return model.create_yaml_version(name, version_name, yaml_content, version_date) is not None


def delete_project_version(project_name: str, version: str) -> bool:
    return model.delete_yaml_version(project_name, version)
