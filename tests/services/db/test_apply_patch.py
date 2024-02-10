from typing import Optional

from sqlmodel import SQLModel

from plm.services.db.patcher import apply_patch


class SampleModel(SQLModel):
    property_1: int
    property_2: int
    property_3: int


class IncomingModel(SQLModel):
    property_1: Optional[int]
    property_2: Optional[int]


def test_apply_patch():
    entity = SampleModel(property_1=1, property_2=2, property_3=3)
    payload = IncomingModel(property_1=100)

    apply_patch(entity, payload)

    assert entity.property_1 == 100
    assert entity.property_2 == 2
    assert entity.property_3 == 3
