import os

from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from shoes_market import users, connection, middleware, settings, products, orders


os.makedirs(settings.MEDIA, exist_ok=True)
app = FastAPI(default_response_class=ORJSONResponse)
app.mount("/media", StaticFiles(directory=settings.MEDIA_PATH), name="media")
origins = ["http://localhost:3000", "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(middleware.JWTMiddleware, secret_key=settings.SECRET_KEY)

api_router = APIRouter(prefix='/api')
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(orders.router)

app.include_router(api_router)


@app.on_event('shutdown')
async def close_redis_connection():
    connection.Connection.close_redis()
    await connection.Connection.close_aioredis()
