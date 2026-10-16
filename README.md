# Proyecto Restaurante

API REST para que el personal de sala gestione los pedidos de las mesas de un restaurante.
El cliente web en Angular está en su propio repositorio:
[Proyecto1FrontendRestauranteAngular](https://github.com/Ebeltran-bit/Proyecto1FrontendRestauranteAngular). El proyecto se entrega por fases; el registro de
decisiones y cambios está en [docs/memoria-proyecto.md](docs/memoria-proyecto.md).

| Carpeta    | Contenido                                   |
|------------|---------------------------------------------|
| `backend/` | API REST en Python con FastAPI              |
| `src/`     | Esqueleto Angular inicial, sin uso (el cliente está en el otro repositorio) |

## Backend (FastAPI)

### Requisitos

- Python 3.9 o superior.

### Instalación

Desde la carpeta `backend/`:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

La carpeta `.venv` no se sube al repositorio: cada persona crea la suya con los pasos anteriores.

### Ejecución

```bash
uvicorn app.main:app --reload
```

- Documentación interactiva de la API: `http://127.0.0.1:8000/docs`, desde donde se pueden
  ejecutar todas las consultas. Primero `POST /auth/login` y después el botón **Authorize**
  con el `access_token` recibido.
- Cliente web: arranca el frontend Angular (ver su README); llama a esta API en el puerto 8000.

### Usuarios de demostración

| Usuario   | Contraseña    | Rol      | Nombre       |
|-----------|---------------|----------|--------------|
| `manager` | `manager123`  | manager  | Laura Gómez  |
| `ana`     | `camarero123` | camarero | Ana Martín   |
| `luis`    | `camarero123` | camarero | Luis Pérez   |

Las contraseñas se guardan cifradas (PBKDF2-SHA256 con sal). Son solo para la demo.

### Pruebas

```bash
python -m pytest
```

### Estructura

```
backend/
  app/
    main.py            # crea la aplicación y registra los routers
    security.py        # cifrado de contraseñas y tokens (solo librería estándar)
    routers/           # endpoints agrupados por recurso
      dependencies.py  # búsquedas comunes (404) y control de sesión y rol (401/403)
    services/          # reglas que combinan varios almacenes: estado de mesa, cobro, resumen del día
    schemas/           # modelos Pydantic de entrada y salida
    data/
      sample_data.py   # carta con precios, mesas, pedidos y usuarios de ejemplo
      order_store.py   # pedidos en memoria
      table_waiters.py # camarero que atiende cada mesa
      user_store.py    # usuarios y sesiones
      bill_store.py    # cuentas cobradas
  tests/               # pruebas automáticas de los endpoints
  requirements.txt
```

### Endpoints

Salvo `/health` y `/auth/login`, todas las rutas piden la cabecera
`Authorization: Bearer <token>`. Sin ella responden `401`; las marcadas como *manager* responden
`403` a un camarero.

| Método | Ruta                                       | Descripción                                          |
|--------|--------------------------------------------|------------------------------------------------------|
| GET    | `/health`                                  | Confirma que la API funciona                         |
| POST   | `/auth/login`                              | Inicia sesión y devuelve el token                    |
| GET    | `/auth/me`                                 | Usuario de la sesión                                 |
| POST   | `/auth/logout`                             | Cierra la sesión                                     |
| GET    | `/tables`                                  | Mesas con su estado, camarero, nº de pedidos y total |
| GET    | `/tables/{table_id}`                       | Selecciona una mesa                                  |
| PUT    | `/tables/{table_id}/waiter`                | Elige el camarero que atiende la mesa (`null` lo quita) |
| POST   | `/tables/{table_id}/pay`                   | Mesa pagada: guarda la cuenta, vacía la mesa y devuelve el ticket |
| GET    | `/tables/{table_id}/orders`                | Lista los pedidos de la mesa                         |
| POST   | `/tables/{table_id}/orders`                | Añade un pedido a la mesa                            |
| GET    | `/tables/{table_id}/orders/{order_id}`     | Consulta un pedido de la mesa                        |
| PATCH  | `/tables/{table_id}/orders/{order_id}`     | Modifica presentación, cantidad o notas              |
| DELETE | `/tables/{table_id}/orders/{order_id}`     | Quita un pedido de la mesa                           |
| GET    | `/menu`                                    | Carta completa con presentaciones y precios          |
| GET    | `/categories`                              | Lista las categorías de la carta                     |
| GET    | `/categories/{category_id}/products`       | Lista los productos de una categoría                 |
| GET    | `/products/{product_id}`                   | Detalle de un producto con su categoría y presentaciones |
| GET    | `/products/{product_id}/presentations`     | Solo las presentaciones activas del producto, con precio |
| GET    | `/users?role=waiter`                       | Lista el personal (opcionalmente de un rol)          |
| POST   | `/users`                                   | Crea un camarero o manager (*manager*)               |
| DELETE | `/users/{user_id}`                         | Borra un usuario (*manager*)                         |
| GET    | `/bills?day=AAAA-MM-DD`                    | Cuentas cobradas de un día, hoy por defecto (*manager*) |
| GET    | `/bills/{bill_id}`                         | Una cuenta cobrada (para reimprimir el ticket)       |
| GET    | `/reports/daily?day=AAAA-MM-DD`            | Resumen del día: total, ticket medio, ventas por camarero y lo más vendido (*manager*) |

Cuerpo JSON para crear un pedido (`POST`); `notes` es opcional (máximo 200 caracteres):

```json
{"product_id": 5, "presentation_id": 3, "quantity": 2, "notes": "Sin gluten"}
```

Cuerpo JSON para modificarlo (`PATCH`), con uno o varios campos (`"notes": null` borra las notas):

```json
{"presentation_id": 4, "quantity": 3}
```

El precio de cada pedido (`unit_price`) lo pone siempre la API a partir de la carta.

Respuestas de error controladas:

- `401`: falta el token o ha caducado (`{"detail": "Inicia sesión para continuar"}`).
- `403`: la acción es solo para managers.
- `404`: la mesa, la categoría, el producto, el pedido, el usuario o la cuenta no existen, o el
  pedido es de otra mesa. Ejemplo: `{"detail": "No existe la mesa con id 999"}`.
- `409`: la acción no se puede hacer en este momento: cobrar una mesa sin pedidos o sin camarero,
  crear un usuario repetido, borrar a un camarero con mesas abiertas, a uno mismo o al último manager.
- `422`: el JSON no es válido (falta un campo, tipo incorrecto como `"2"` en vez de `2`,
  cantidad fuera de 1 a 99, campos desconocidos) o hace referencia a un producto o presentación
  que no existe o no está activa. Ejemplo: `{"detail": "Agua mineral no está disponible en Ración"}`.

### Datos de prueba

Los datos están en memoria, en `backend/app/data/sample_data.py`. Los pedidos que se crean o
modifican se pierden al reiniciar el servidor (la base de datos MySQL llegará más adelante).

- Categorías: 1 Bebidas, 2 Entrantes, 3 Carnes, 4 Pescados, 5 Postres.
- Mesas: 1 Mesa 1, 2 Mesa 2, 3 Mesa 3, 4 Terraza 1, 5 Barra.
- Presentaciones: 1 Unidad, 2 Tapa, 3 Media ración, 4 Ración.
- Productos: entre 2 y 3 por categoría, cada uno con sus presentaciones activas y su precio
  en cada una (por ejemplo, las bebidas solo se sirven por unidad).
- Pedidos iniciales: la Mesa 1 tiene 2 pedidos (atiende Ana), la Mesa 2 tiene 1 (atiende Luis)
  y el resto ninguno.
