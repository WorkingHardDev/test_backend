from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from auth.middleware import auth_middleware
from routers.user.views import router as user_router
from routers.jwt_auth.views import router as jwt_auth_router
from routers.post.views import router as post_router

app = FastAPI()

origins = [
    "*"
]


@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    response = Response()
    res = await auth_middleware(request, response, call_next)
    return res


# Apply CORS middleware first
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

app.include_router(user_router)
app.include_router(jwt_auth_router)
app.include_router(post_router)
