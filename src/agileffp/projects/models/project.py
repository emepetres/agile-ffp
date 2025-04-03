from pydantic import BaseModel


class Project(BaseModel):
    name: str
    description: str

    # needed for db persistence
    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
