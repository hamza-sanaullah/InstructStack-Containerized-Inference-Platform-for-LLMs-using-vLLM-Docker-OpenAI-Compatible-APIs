from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.vllm_client import call_vllm
import asyncio
import random
import time

from vllm.config import VLLM_API_URL, AVAILABLE_MODELS
from services.vllm_client import call_vllm

router = APIRouter()
templates = Jinja2Templates(directory="templates")

MODEL = "yasserrmd/Text2SQL-1.5B"
CONCURRENCY = 10
REQUESTS_PER_CLIENT = 5

# Shared prompt pool (backend-controlled)
PROMPT_POOL = [
    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nList all employees hired after 2020.\n\n### SQL:\n",
    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nFind employees in department 5 earning more than 100000.\n\n### SQL:\n",
    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nShow employee names and salaries ordered by salary descending.\n\n### SQL:\n",
    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nCount the number of employees in each department.\n\n### SQL:\n",
    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nWhat is the average salary of employees hired after 2015?\n\n### SQL:\n"
]

results = []

async def simulate_user(user_id: int):
    prompts = random.sample(PROMPT_POOL, REQUESTS_PER_CLIENT)
    for i, prompt in enumerate(prompts):
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "max_tokens": 128,
            "temperature": 0.3,
            "stop": [";"]
        }
        start = time.perf_counter()
        try:
            result = await asyncio.to_thread(call_vllm, payload)
            delta = time.perf_counter() - start
            msg = f"[User {user_id}][Req {i+1}] {delta:.2f}s → {result}"
        except Exception as e:
            msg = f"[User {user_id}][Req {i+1}] ERROR: {e}"
        print(msg)
        results.append(msg)

@router.post("/check-concurrency",response_class=HTMLResponse)
async def check_concurrency(request: Request):
    global results
    results = []  # Clear old results
    tasks = [simulate_user(i + 1) for i in range(CONCURRENCY)]
    await asyncio.gather(*tasks)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "concurrency_result": results
    })


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": AVAILABLE_MODELS,
        "response": None
    })


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    model: str = Form(...),
    prompt: str = Form(...),
    max_tokens: int = Form(50)
):
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens
    }

    result = call_vllm(payload)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "models": AVAILABLE_MODELS,
        "response": result,
        "selected_model": model,
        "prompt": prompt,
        "max_tokens": max_tokens
    })
