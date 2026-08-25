from pydantic import BaseModel, ConfigDict


class KnowledgeComponentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    learning_objectives: list[str]
    prerequisites: list[str]
