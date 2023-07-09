from fastapi import APIRouter, FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from shoes_market import users, connection, middleware, settings


app = FastAPI(default_response_class=ORJSONResponse)
origins = [
    "http://localhost",
    "http://localhost:8080",
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

app.include_router(api_router)


@app.on_event('shutdown')
async def close_redis_connection():
    connection.Connection.close_redis()
    await connection.Connection.close_aioredis()
