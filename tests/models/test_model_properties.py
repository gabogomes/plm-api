from plm.models import Task, PersonalNote
from plm.enums import PersonalNoteTypes, TaskStatus, TaskTypes


def test_task_model_properties():
    mock_task = Task(
        id=1,
        name="Task 1",
        status=TaskStatus.ToDo,
        type=TaskTypes.Work,
        user_id="sk-duh7d81o7db81o3dybi",
        correspondence_email_address="test@localdev.com",
        personal_notes=[
            PersonalNote(
                task_id=1,
                name="personal note 1",
                type=PersonalNoteTypes.Observations,
                note=" This is a test note",
                user_id="sk-duh7d81o7db81o3dybi",
                correspondence_email_address="test@localdev.com",
            ),
            PersonalNote(
                task_id=1,
                name="personal note 2",
                type=PersonalNoteTypes.ProgressReport,
                note=" This is a test note 2",
                user_id="sk-duh7d81o7db81o3dybi",
                correspondence_email_address="test@localdev.com",
            ),
        ],
    )

    assert mock_task.id == 1
    assert mock_task.name == "Task 1"
    assert mock_task.status == "To Do"
    assert mock_task.type == "Work"
    assert mock_task.user_id == "sk-duh7d81o7db81o3dybi"
    assert mock_task.correspondence_email_address == "test@localdev.com"
    assert mock_task.personal_notes[0].task_id == 1
    assert mock_task.personal_notes[0].name == "personal note 1"
    assert mock_task.personal_notes[0].type == "Observations"
    assert mock_task.personal_notes[0].note == "This is a test note"
    assert mock_task.personal_notes[0].user_id == "sk-duh7d81o7db81o3dybi"
    assert (
        mock_task.personal_notes[0].correspondence_email_address == "test@localdev.com"
    )
    assert mock_task.personal_notes[1].task_id == 1
    assert mock_task.personal_notes[1].name == "personal note 2"
    assert mock_task.personal_notes[1].type == "Progress Report"
    assert mock_task.personal_notes[1].note == "This is a test note 2"
    assert mock_task.personal_notes[1].user_id == "sk-duh7d81o7db81o3dybi"
    assert (
        mock_task.personal_notes[1].correspondence_email_address == "test@localdev.com"
    )
