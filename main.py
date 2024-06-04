from typing import Union

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

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


prefix = "/api/v1"
app.include_router(uefa.router, prefix=prefix)


if __name__ == '__main__':
    uvicorn.run(app, port=8003)
