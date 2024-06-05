from typing import Union

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.routers import uefa

app = FastAPI(
    title="Tickets",
    version="0.1",
    description="""
        API for tickets portal
    """,
    swagger_ui_parameters={"docExpansion": "none"},
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        # Middleware(ValidateParams),
        # Middleware(LogExceptions),
    ]
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

prefix = "/api/v1"
app.include_router(uefa.router, prefix=prefix)


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    test_value = 33
    return templates.TemplateResponse(
        request=request, name="index.html", context={"test_value": test_value}
    )


@app.get("/uefa", response_class=HTMLResponse)
async def get_uefa(request: Request):
    available_session = len(uefa.get_available_sessions())
    return templates.TemplateResponse(
        request=request, name="uefa.html",
        context={"available_session": available_session}
    )


if __name__ == '__main__':
    uvicorn.run(app, port=8004)
