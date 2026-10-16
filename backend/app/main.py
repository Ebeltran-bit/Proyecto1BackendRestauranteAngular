from fastapi import Depends, FastAPI

from app.routers import auth, bills, categories, health, menu, orders, products, tables, users
from app.routers.dependencies import get_current_user

app = FastAPI(
    title="Restaurant Orders API",
    description=(
        "API REST para que el personal de sala gestione los pedidos de las mesas. "
        "Salvo /health y /auth/login, todas las rutas piden el token de POST /auth/login "
        "(botón Authorize)."
    ),
    version="0.3.0",
)

# Public routes.
app.include_router(health.router)
app.include_router(auth.router)

# Everything else needs a logged-in user; manager-only routes add their own check.
logged_in = [Depends(get_current_user)]
app.include_router(tables.router, dependencies=logged_in)
app.include_router(orders.router, dependencies=logged_in)
app.include_router(menu.router, dependencies=logged_in)
app.include_router(categories.router, dependencies=logged_in)
app.include_router(products.router, dependencies=logged_in)
app.include_router(users.router, dependencies=logged_in)
app.include_router(bills.router, dependencies=logged_in)
