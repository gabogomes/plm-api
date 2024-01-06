from enum import Enum


class _StringEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Permission(_StringEnum):
    Read = "read:all"
    Admin = "admin:all"
