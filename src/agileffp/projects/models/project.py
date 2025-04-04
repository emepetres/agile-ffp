from pydantic import BaseModel


class Project(BaseModel):
    name: str
    description: str
    yaml_content: str

    # needed for db persistence
    def __init__(self, name: str, description: str, yaml_content: str = "") -> None:
        super().__init__(name=name, description=description, yaml_content=yaml_content)
