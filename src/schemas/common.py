from pydantic import BaseModel, ConfigDict
from humps import camelize

class CamelCaseModel(BaseModel):
    """A base model that converts field names to camelCase when serializing."""
    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True)
