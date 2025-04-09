from fasthtml.common import (
    FormData,
    Request,
    add_toast,
)

from agileffp.project import model, view
from agileffp.monitor import controller as monitor_controller

_render_target = None
index: callable = None


def init(router, endpoints, render_target: str):
    global _render_target
    _render_target = render_target

    @router.get(endpoints.LIST.value)
    def list_projects():
        projects = model.get_projects()
        return view.render_projects(projects, _render_target)

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

    @router.delete(endpoints.DELETE.value)
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
        yaml_content = model.get_project(name).yaml_content
        return monitor_controller.index(session, name, yaml_content)

    global index
    index = list_projects


def update_project(name: str, yaml_content: str):
    # # now = datetime.now().isoformat()
    model.update_project(name, yaml_content)
