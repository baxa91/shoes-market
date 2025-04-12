from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import jwt


class JWTMiddleware:
    def __init__(self, app: FastAPI, secret_key: str):
        self.app = app
        self.secret_key = secret_key

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive)
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            request.state.user = None
            request.state.is_authenticated = False
            response = await self.app(request.scope, receive, send)
            return response

        if not authorization_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content="Invalid token")

        token = authorization_header.replace("Bearer ", "")

        try:
            decoded_token = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JSONResponse(status_code=401, content="Token has expired")
        except jwt.InvalidTokenError:
            return JSONResponse(status_code=401, content="Invalid token")

        user = decoded_token.get("user")
        request.state.user = user
        request.state.is_authenticated = True
        response = await self.app(request.scope, receive, send)
        return response
