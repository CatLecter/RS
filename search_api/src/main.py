import asyncio

import api
import uvicorn
from core import config
from core.config import jwt_algorithms, jwt_secret_key
from db.elastic import elastic_connect, elastic_disconnect
from db.redis import redis_connect, redis_disconnect
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from jose import JWTError, jwt

app = FastAPI(
    title=config.PROJECT_NAME,
    description=config.PROJECT_DESCRIPTION,
    version=config.PROJECT_VERSION,
    license_info=config.PROJECT_LICENSE_INFO,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    openapi_tags=config.PROJECT_TAGS_METADATA,
    default_response_class=ORJSONResponse,
)


@app.middleware("http")
async def jwt_handler(request: Request, call_next):
    roles = {}
    token_status = "None"

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token_status = "OK"
        jwt_token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(jwt_token, jwt_secret_key, algorithms=jwt_algorithms)
            roles = set(payload.get("roles", {}))
        except JWTError as e:
            token_status = f"Error: {e}"

    request.state.user_roles = roles
    response = await call_next(request)
    response.headers["X-Token-Status"] = token_status
    return response


@app.on_event("startup")
async def startup():
    await asyncio.gather(
        redis_connect(),
        elastic_connect(),
    )


@app.on_event("shutdown")
async def shutdown():
    await asyncio.gather(
        redis_disconnect(),
        elastic_disconnect(),
    )


app.include_router(api.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
