"""Shared lookups for path parameters.

Each function is a FastAPI dependency: it returns the resource or answers 404
with a clear message, so the endpoints only deal with the happy path. The
authentication dependencies answer 401 (no valid session) or 403 (wrong role).
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.data.bill_store import bill_store
from app.data.order_store import order_store
from app.data.sample_data import CATEGORIES_BY_ID, PRODUCTS_BY_ID, TABLES_BY_ID
from app.data.user_store import user_store
from app.schemas import Bill, Category, Order, Product, Table, User

# auto_error=False: the 401 is raised below with a message in Spanish.
_bearer = HTTPBearer(auto_error=False, description="Token devuelto por POST /auth/login")


def _not_found(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def get_category_or_404(category_id: int) -> Category:
    category = CATEGORIES_BY_ID.get(category_id)
    if category is None:
        raise _not_found(f"No existe la categoría con id {category_id}")
    return category


def get_product_or_404(product_id: int) -> Product:
    product = PRODUCTS_BY_ID.get(product_id)
    if product is None:
        raise _not_found(f"No existe el producto con id {product_id}")
    return product


def get_table_or_404(table_id: int) -> Table:
    table = TABLES_BY_ID.get(table_id)
    if table is None:
        raise _not_found(f"No existe la mesa con id {table_id}")
    return table


def get_order_or_404(order_id: int, table: Table = Depends(get_table_or_404)) -> Order:
    order = order_store.get(order_id)
    if order is None or order.table_id != table.id:
        raise _not_found(f"La mesa {table.id} no tiene ningún pedido con id {order_id}")
    return order


def get_user_or_404(user_id: int) -> User:
    user = user_store.get(user_id)
    if user is None:
        raise _not_found(f"No existe el usuario con id {user_id}")
    return user


def get_bill_or_404(bill_id: int) -> Bill:
    bill = bill_store.get(bill_id)
    if bill is None:
        raise _not_found(f"No existe la cuenta con id {bill_id}")
    return bill


def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer)) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inicia sesión para continuar",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def get_current_user(token: str = Depends(get_token)) -> User:
    user = user_store.user_for_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha caducado. Vuelve a iniciar sesión",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_manager(user: User = Depends(get_current_user)) -> User:
    if user.role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo un manager puede hacer esto")
    return user
