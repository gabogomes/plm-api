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


class TaskStatus(_StringEnum):
    ToDo = "To Do"
    InProgress = "In Progress"
    PendingForRevision = "Pending for Revision"
    Done = "Done"


class TaskTypes(_StringEnum):
    Work = "Work"
    Studies = "Studies"
    WellBeing = "Well Being"
    Others = "Others"


class PersonalNoteTypes(_StringEnum):
    Description = "Description"
    ProgressReport = "Progress Report"
    Observations = "Observations"
