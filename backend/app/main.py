from fastapi import FastAPI
from .database import init_db
from .routers import users, registry, reservations, search, ws, csrf, oauth
from .pubsub import pubsub
from .middleware import OriginValidationMiddleware
import asyncio

app = FastAPI(title='Gift Registry API')
app.add_middleware(OriginValidationMiddleware)

app.include_router(users.router)
app.include_router(registry.router)
app.include_router(reservations.router)
app.include_router(search.router)
app.include_router(csrf.router)
app.include_router(ws.router)
app.include_router(oauth.router)

@app.on_event('startup')
async def startup():
    init_db()
    # start pubsub connection (non-blocking)
    asyncio.create_task(pubsub.connect())
