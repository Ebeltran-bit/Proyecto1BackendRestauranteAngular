"""Staff accounts. Anyone logged in can list them (to choose a table's waiter);
only a manager can create or delete them."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.data.table_waiters import table_waiter_store
from app.data.user_store import user_store
from app.routers.dependencies import get_user_or_404, require_manager
from app.schemas import Role, User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


def _conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


@router.get("", response_model=List[User], summary="List staff, optionally only one role")
def list_users(role: Optional[Role] = None) -> List[User]:
    users = user_store.list()
    return [user for user in users if role is None or user.role == role]


@router.post(
    "",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a waiter or manager (manager only)",
    dependencies=[Depends(require_manager)],
)
def create_user(body: UserCreate) -> User:
    if user_store.username_taken(body.username):
        raise _conflict(f"Ya existe un usuario con el nombre {body.username}")
    return user_store.add(body)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a member of staff (manager only)",
)
def delete_user(target: User = Depends(get_user_or_404), manager: User = Depends(require_manager)) -> None:
    if target.id == manager.id:
        raise _conflict("No puedes borrar tu propio usuario")
    if target.role == "manager" and user_store.count_role("manager") <= 1:
        raise _conflict("Tiene que quedar al menos un manager")
    if table_waiter_store.is_serving(target.id):
        raise _conflict(f"{target.full_name} está atendiendo mesas abiertas. Cóbralas o cambia el camarero primero")
    user_store.delete(target.id)
