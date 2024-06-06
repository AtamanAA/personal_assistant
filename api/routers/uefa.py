import os
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from loguru import logger

from variables import BASE_DIR
from services.uefa import UefaService
from utils import get_proxy_ip, check_proxy_list, get_proxies_list



log_file_path = "logs/uefa_logs.json"
logger.add(log_file_path, format="{time} {level} {message}", rotation="1 MB", serialize=True)

UEFA_SESSION_PATH = f'{BASE_DIR}/services/uefa/uefa_sessions.json'
SESSION_EXPIRE_TIME = 30

tag = "UEFA"
router = APIRouter(prefix="/uefa", tags=[tag])

templates = Jinja2Templates(directory="templates")


class Proxy(BaseModel):
    user: str
    host: str
    port: str


class SessionBase(BaseModel):
    proxy: Proxy
    ip: str
    data_dome_cookie: str


class Session(SessionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    expire_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(minutes=SESSION_EXPIRE_TIME))


class UserUEFA(BaseModel):
    email: str
    password: str


def get_uefa_available_session():
    with open(UEFA_SESSION_PATH, 'r') as file:
        sessions_content = file.read()
    sessions = json.loads(sessions_content)
    available_session = []
    for session in sessions:
        date_format = "%Y-%m-%d %H:%M:%S.%f"
        # session_expire_at = datetime.strptime(session["expire_at"], date_format)
        session_expire_at = datetime.fromisoformat(session["expire_at"])
        # if session_expire_at > datetime.now():
        current_date = datetime.now(session_expire_at.tzinfo)
        if session_expire_at > current_date:
            available_session.append(session)
    return available_session


@router.get("/sessions", response_model=List[Session])
def get_sessions():
    """
    Get full list of sessions for UEFA
    """
    with open(f'{BASE_DIR}/services/uefa/uefa_sessions.json') as file:
        sessions_content = file.read()
    sessions = json.loads(sessions_content)
    return sessions


@router.post("/sessions", response_model=Session)
def add_session(new_session: SessionBase):
    """
    Add a new session for UEFA
    """
    with open(UEFA_SESSION_PATH, 'r') as file:
        sessions_content = file.read()
    sessions = json.loads(sessions_content)

    # sessions.append(new_session.dict())
    sessions.append(Session(**new_session.dict()).dict())

    with open(UEFA_SESSION_PATH, 'w') as file:
        file.write(json.dumps(sessions, default=str, indent=4))

    return new_session


@router.post("/sessions_form", response_model=Session)
def add_session_form(
        proxy_user: str = Form(...),
        proxy_host: str = Form(...),
        proxy_port: str = Form(...),
        ip: str = Form(...),
        data_dome_cookie: str = Form(...)
):
    """
    Add a new session for UEFA
    """
    proxy = Proxy(user=proxy_user, host=proxy_host, port=proxy_port)
    new_session = SessionBase(proxy=proxy, ip=ip, data_dome_cookie=data_dome_cookie)

    with open(UEFA_SESSION_PATH, 'r') as file:
        sessions_content = file.read()
    sessions = json.loads(sessions_content)

    sessions.append(Session(**new_session.dict()).dict())

    with open(UEFA_SESSION_PATH, 'w') as file:
        file.write(json.dumps(sessions, default=str, indent=4))

    return RedirectResponse(url="/uefa", status_code=303)


@router.get("/available_sessions", response_model=List[Session])
def get_available_sessions():
    """
    Get list of available sessions for UEFA
    """
    return get_uefa_available_session()


@router.post("/run_uefa_script",
             # response_model=Session
             )
def run_uefa_script(user_info: UserUEFA):
    """
    Run UEFA script
    """
    available_session = get_uefa_available_session()

    if not available_session:
        raise HTTPException(detail="Available session didn't find", status_code=404)

    for session in available_session:
        session_ip = session["ip"]
        check_proxy_ip = get_proxy_ip(proxy=session["proxy"])
        print(f"Session IP    : {session_ip}")
        print(f"Check proxy IP: {check_proxy_ip}")
        if session_ip != check_proxy_ip:
            time.sleep(5)
            continue
        UefaService(
            proxy_user=session["proxy"]["user"],
            proxy_host=session["proxy"]["host"],
            proxy_port=session["proxy"]["port"],
            data_dome_cookie=session["data_dome_cookie"],
            user_email=user_info.email,
            user_password=user_info.password
        ).run()
        return {"Successful finished script"}  # TODO: Add error exceptions

    raise HTTPException(detail="Use all available sessions", status_code=404)


@router.post("/run_uefa_script_form",
             # response_model=Session
             )
def run_uefa_script_form(email: str = Form(...), password: str = Form(...)):
    """
    Run UEFA script
    """
    available_session = get_uefa_available_session()

    if not available_session:
        logger.warning("Available session didn't find")
        return RedirectResponse(url="/uefa", status_code=303)

    for session in available_session:
        session_ip = session["ip"]
        check_proxy_ip = get_proxy_ip(proxy=session["proxy"])
        if session_ip != check_proxy_ip:
            logger.warning(f"Session IP:{session_ip} not equal Check proxy IP:{check_proxy_ip}")
            time.sleep(10)
            continue
        logger.info(f"Session IP:{session_ip} is equal Check proxy IP:{check_proxy_ip}")
        UefaService(
            proxy_user=session["proxy"]["user"],
            proxy_host=session["proxy"]["host"],
            proxy_port=session["proxy"]["port"],
            data_dome_cookie=session["data_dome_cookie"],
            user_email=email,
            user_password=password
        ).run()
        logger.info("Finish UEFA script")
        return RedirectResponse(url="/uefa", status_code=303)  # TODO: Add error exceptions

    logger.warning("Session IP not equal Check proxy IP")
    logger.info("Finish UEFA script")
    return RedirectResponse(url="/uefa", status_code=303)


@router.get("/run_log_script")
def run_log_script():
    """
    Create fake logs for test
    """
    for i in range(10):
        logger.info(f"Test log: {i}")
        logger.success(f"Test log: {i}")
        time.sleep(5)
    return {"message": "Test completed"}


@router.get("/get_logs")
def get_logs():
    """
    Get logs from files
    """
    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()
    log_for_site = []
    for log in logs:
        item = json.loads(log.strip())
        if item["record"]["level"]["name"] != "DEBUG":
            log_for_site.append({
                "text": item["text"],
                "time": item["record"]["time"],
                "level": item["record"]["level"]["name"],
                "message": item["record"]["message"]
            })
    return log_for_site


@router.delete("/clear_logs")
def clear_logs():
    """
    Clears logs from the log file
    """
    try:
        with open(log_file_path, "w") as log_file:
            log_file.truncate(0)
        return {"message": "Logs cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check_proxies")
def check_proxies():
    """
    Check proxies list
    """
    return check_proxy_list(get_proxies_list())
