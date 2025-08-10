from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from vllm.config import VLLM_API_URL, AVAILABLE_MODELS
from services.vllm_client import call_vllm

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
