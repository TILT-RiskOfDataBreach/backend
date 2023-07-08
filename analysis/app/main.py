from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import authentication, login, analysis


app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Set-Cookie"]
)

app.include_router(authentication.router)
app.include_router(login.router)
app.include_router(analysis.router)


@app.on_event("startup")
async def startup_event():
    print("startup")


@app.on_event("shutdown")
async def shutdown_event():
    print("shutdown")
