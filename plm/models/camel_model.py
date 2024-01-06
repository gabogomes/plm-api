from sqlmodel import SQLModel

from humps import camelize


class CamelModel(SQLModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
        anystr_strip_whitespace = True
