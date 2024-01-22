from fastapi import Depends, APIRouter, Path
from plm.schemas import Page, TaskResponse, TaskCreate, TaskUpdate, TaskSingleResponse
from plm.models import Task
from plm.dependencies import get_db
from sqlmodel import Session, select
from fastapi_pagination.ext.sqlalchemy import paginate
from plm.services.db import apply_patch
from plm.endpoints.helpers.task_helpers import get_task_or_404

router = APIRouter(prefix="/v1")


@router.get(
    path="/tasks/{userId}",
    name="Get all tasks for a user",
    response_model=Page[TaskResponse],
    response_model_exclude_none=True,
)
def get_tasks(user_id: str = Path(alias="userId"), db: Session = Depends(get_db)):

    query = select(Task).filter(Task.user_id == user_id)

    return paginate(db, query.order_by(Task.id))


@router.get(
    path="/tasks/{userId}/{taskId}",
    name="Get a given task by id",
    response_model=TaskSingleResponse,
    response_model_exclude_none=True,
)
def get_task(
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
):

    query = get_task_or_404(db, user_id, task_id)

    return query


@router.post(
    path="/tasks",
    name="Create new task",
    response_model=TaskResponse,
    response_model_exclude_none=True,
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
):
    task_entity = Task.parse_obj(payload)

    db.add(task_entity)
    db.commit()

    return task_entity


@router.patch(
    path="/tasks/{userId}/{taskId}",
    name="Update an existing task",
    response_model=TaskResponse,
    response_model_exclude_none=True,
)
def update_task(
    payload: TaskUpdate,
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
):
    task_entity = get_task_or_404(db, user_id, task_id)

    apply_patch(task_entity, payload)

    db.commit()

    return task_entity


@router.delete(path="/tasks/{userId}/{taskId}", name="Delete a task", status_code=204)
def delete_task(
    user_id: str = Path(alias="userId"),
    task_id: int = Path(alias="taskId"),
    db: Session = Depends(get_db),
) -> None:
    task_entity = get_task_or_404(db, user_id, task_id)

    db.delete(task_entity)
    db.commit()
