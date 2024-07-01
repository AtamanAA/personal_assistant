import os
import sys
import time
import json
import uuid
import requests
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, Form, Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from loguru import logger

from variables import BASE_DIR
from services.uefa import UefaService
from utils import get_proxy_ip, check_proxy_list, get_proxies_list, find_proxy_by_ip


log_file_path = f"{BASE_DIR}/logs/uefa_logs.json"
core_log_file_path = f"{BASE_DIR}/logs/core_uefa_logs.json"
# logger.remove()
logger.add(log_file_path, format="{time} {level} {message}", rotation="1 MB", serialize=True)
logger.add(core_log_file_path, format="{time} {level} {message}", rotation="1 MB", serialize=True)
# logger.add(sys.stdout, level="DEBUG")

UEFA_SESSION_PATH = f'{BASE_DIR}/services/uefa/uefa_sessions.json'
UEFA_TASKS_PATH = f'{BASE_DIR}/services/uefa/uefa_tasks.json'
SESSION_EXPIRE_TIME = 30

tag = "UEFA"
router = APIRouter(prefix="/uefa", tags=[tag])

templates = Jinja2Templates(directory="templates")


class Proxy(BaseModel):
    user: str
    host: str
    port: str


class SessionBase(BaseModel):
    proxy: Optional[Proxy]
    ip: str
    data_dome_cookie: str


class Session(SessionBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    expire_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(minutes=SESSION_EXPIRE_TIME))


class UserUEFA(BaseModel):
    email: str
    password: str


class TaskUEFA(BaseModel):
    id: str
    email: str
    status: str
    created_at: datetime = Field(default_factory=datetime.now)


def get_uefa_available_session():
    if not os.path.exists(UEFA_SESSION_PATH):
        # Create the file if it doesn't exist
        with open(UEFA_SESSION_PATH, 'w') as file:
            json.dump([], file)

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


def add_new_session(new_session: SessionBase):
    logger.debug(f"Try add new uefa session | Session data: {new_session}")
    with open(UEFA_SESSION_PATH, 'r') as file:
        sessions_content = file.read()
    sessions = json.loads(sessions_content)

    if not new_session.proxy:
        logger.debug("Try find IP in proxy list")
        proxy_export_list = get_proxies_list()
        proxy = find_proxy_by_ip(proxy_list=proxy_export_list, ip=new_session.ip)
        if not proxy:
            raise HTTPException(detail="IP didn't find from proxy list", status_code=404)
        if proxy:
            logger.debug(f"Found IP in proxy list. Proxy: {proxy}")
            new_session.proxy = Proxy(user=proxy["username"], host=proxy["ip"], port=str(proxy["port"]))

    sessions.append(Session(**new_session.dict()).dict())

    with open(UEFA_SESSION_PATH, 'w') as file:
        file.write(json.dumps(sessions, default=str, indent=4))


@router.post("/sessions")
def add_session(background_tasks: BackgroundTasks, new_session: SessionBase):
    background_tasks.add_task(add_new_session, new_session=new_session)
    return "Session data sent for processing"


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


def set_task_status(id: str, email: str, status: str):
    if not os.path.exists(UEFA_TASKS_PATH):
        with open(UEFA_TASKS_PATH, 'w') as file:
            json.dump([], file)

    with open(UEFA_TASKS_PATH, 'r') as file:
        tasks_content = file.read() or "[]"
    tasks = json.loads(tasks_content)

    if status == "processing":
        tasks.append(TaskUEFA(id=id, email=email, status=status).dict())

    else:
        for task in tasks:
            if task["id"] == id:
                task["status"] = status

    with open(UEFA_TASKS_PATH, 'w') as file:
        file.write(json.dumps(tasks, default=str, indent=4))

    return True


def uefa_script(email: str, password: str):
    clear_logs()
    task_id = str(uuid.uuid4())
    set_task_status(id=task_id, email=email, status="processing")
    logger.info(f"Run UEFA script")
    available_session = get_uefa_available_session()

    if not available_session:
        logger.info("Available session didn't find")
        logger.info("Failed UEFA script")
        set_task_status(id=task_id, email=email, status="failed")

    for session in available_session:
        session_ip = session["ip"]
        check_proxy_ip = get_proxy_ip(proxy=session["proxy"])
        if session_ip != check_proxy_ip:
            logger.debug(f"Session IP:{session_ip} not equal Check proxy IP:{check_proxy_ip}")
            time.sleep(10)
            continue
        logger.debug(f"Session IP:{session_ip} is equal Check proxy IP:{check_proxy_ip}")
        logger.info(f"Try use session IP:{session_ip}")
        time.sleep(10)
        script_result = UefaService(
            proxy_user=session["proxy"]["user"],
            proxy_host=session["proxy"]["host"],
            proxy_port=session["proxy"]["port"],
            data_dome_cookie=session["data_dome_cookie"],
            user_email=email,
            user_password=password
        ).run()

        if script_result:
            logger.info("Successful finish UEFA script")
            set_task_status(id=task_id, email=email, status="completed")
            return True
        else:
            continue

    logger.warning("Didn't find any correct IP from available sessions")
    logger.info("Finish UEFA script")
    set_task_status(id=task_id, email=email, status="failed")
    return False


@router.post("/run_uefa_script_form")
def run_uefa_script_form(background_tasks: BackgroundTasks, email: str = Form(...), password: str = Form(...)):
    """
    Run UEFA script in background task
    """
    background_tasks.add_task(uefa_script, email=email, password=password)
    return RedirectResponse(url="/uefa", status_code=303)


@router.get("/get_logs")
def get_logs():
    """
    Get logs from files
    """
    with open(log_file_path, "r") as log_file:
        logs = log_file.readlines()
    unique_text = set()
    log_for_site = []
    for log in logs:
        item = json.loads(log.strip())
        item_log_level = item["record"]["level"]["name"]
        if item_log_level == "INFO":
            if item["text"] not in unique_text:
                log_for_site.append({
                    "text": item["text"],
                    "time": item["record"]["time"],
                    "level": item["record"]["level"]["name"],
                    "message": item["record"]["message"]
                })
                unique_text.add(item["text"])
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


@router.get("/get_last_screenshot")
def get_last_screenshot():
    """
    Get the last screenshot for UEFA
    """

    screen_short_dir = f"{BASE_DIR}/screenshots/uefa"

    if not os.path.exists(screen_short_dir):
        raise HTTPException(status_code=404, detail="Screenshot directory not found")

    # List all files in the directory
    files = [os.path.join(screen_short_dir, file) for file in os.listdir(screen_short_dir) if
             os.path.isfile(os.path.join(screen_short_dir, file))]

    if not files:
        raise HTTPException(status_code=404, detail="No screenshots found")

    # Get the most recent file by modification date
    latest_file = max(files, key=os.path.getmtime)

    if not latest_file:
        raise HTTPException(status_code=404, detail="No screenshots found")

    # Read the content of the file (assuming it's an image, you may want to handle it differently)
    with open(latest_file, "rb") as f:
        file_content = f.read()

    return Response(content=file_content, media_type="image/png")


@router.get("/get_task_status")
def get_task_status():
    """
    Get the last task status
    """
    with open(UEFA_TASKS_PATH, 'r') as file:
        tasks_content = file.read() or "[]"
    tasks = json.loads(tasks_content)
    if not tasks:
        return "undefined"
    last_task = tasks[-1]
    return last_task["status"].capitalize()
