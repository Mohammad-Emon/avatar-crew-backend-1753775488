import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel
from openrouter_client import OpenRouterClient

app = FastAPI(title="Avatar-Crew API", version="0.1.0")

# Initialize OpenRouter client
def get_openrouter_client():
    return OpenRouterClient()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    model: str = "anthropic/claude-2:free"
    fallback_models: List[str] = [
        "google/gemini-pro:free",
        "mistral/mistral-7b:free"
    ]
    temperature: float = 0.7
    max_tokens: int = 300

class ChatResponse(BaseModel):
    success: bool
    content: str = ""
    model_used: str = ""
    error: str = ""

# Chat endpoint
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    client: OpenRouterClient = Depends(get_openrouter_client)
):
    """Chat with the AI using OpenRouter's free models."""
    try:
        logger.info(f"Received chat request with model: {request.model}")
        logger.debug(f"Full request: {request.dict()}")
        
        response = client.chat(
            message=request.message,
            model=request.model,
            fallback_models=request.fallback_models,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            app_name="Avatar-Crew",
            app_url="https://github.com/yourusername/avatar-crew"
        )
        
        logger.info(f"OpenRouter response: {response.get('success', False)}")
        
        if not response.get("success"):
            error_msg = response.get("error", "Unknown error from OpenRouter")
            logger.error(f"OpenRouter error: {error_msg}")
            return ChatResponse(
                success=False,
                error=error_msg,
                model_used=response.get("model_used", "none")
            )
            
        return ChatResponse(
            success=True,
            content=response["content"],
            model_used=response["model_used"]
        )
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Error in chat endpoint: {error_msg}")
        logger.error(traceback.format_exc())
        
        return ChatResponse(
            success=False,
            error=error_msg,
            model_used="none"
        )

# Allow local Vite dev server during development
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/agents")
async def list_dummy_agents():
    """Return placeholder agent list until CrewAI workflow is integrated."""
    return {
        "agents": [
            {"id": 1, "name": "Sales Avatar", "status": "ready"},
            {"id": 2, "name": "HR Interviewer", "status": "ready"},
        ]
    }

from crew_workflow import run_avatar_workflow
from rag_utils import rag_query
from voice_utils import tts, lip_sync
from browser_agent import browser_agent
from fastapi.responses import JSONResponse, HTMLResponse

# TODO: Integrate CrewAI and real workflows


@app.post("/run_workflow")
async def run_workflow(payload: dict):
    """Execute a minimal CrewAI workflow.
    Expected JSON: { "prompt": "..." }
    """
    prompt = payload.get("prompt", "")
    return await run_avatar_workflow(prompt)


@app.post("/rag_query")
async def rag_query_endpoint(payload: dict):
    """Answer a question using RAG (Weaviate + Ollama)"""
    question = payload.get("question", "")
    return rag_query(question)


@app.post("/tts")
async def tts_endpoint(payload: dict):
    """Generate speech audio (base64) from text using ElevenLabs."""
    text = payload.get("text", "")
    voice_id = payload.get("voice_id", "Rachel")
    return tts(text, voice_id)


@app.post("/lip_sync")
async def lip_sync_endpoint(payload: dict):
    """Generate lip-synced video URL using D-ID."""
    audio_b64 = payload.get("audio_base64", "")
    image_url = payload.get("image_url", "")
    return lip_sync(audio_b64, image_url)


# Browser automation endpoints
@app.post("/browser/start")
async def start_browser():
    """Start the browser instance."""
    result = await browser_agent.start()
    return result

@app.post("/browser/navigate")
async def navigate_to_url(request: dict):
    """Navigate to a URL with error handling."""
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        return await browser_agent.navigate(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/click")
async def click_element(request: dict):
    """Click an element matching the selector with timeout."""
    selector = request.get("selector")
    timeout = request.get("timeout", 30000)  # Default 30 seconds
    if not selector:
        raise HTTPException(status_code=400, detail="Selector is required")
    try:
        return await browser_agent.click(selector)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/type")
async def type_text(request: dict):
    """Type text into an input field with validation."""
    selector = request.get("selector")
    text = request.get("text")
    if not selector or text is None:
        raise HTTPException(status_code=400, detail="Selector and text are required")
    try:
        return await browser_agent.type_text(selector, text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/browser/content")
async def get_page_content():
    """Get the current page content with error handling."""
    try:
        return await browser_agent.get_content()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/browser/screenshot")
async def take_screenshot():
    """Take a screenshot of the current page with error handling."""
    try:
        return await browser_agent.take_screenshot()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/close")
async def close_browser():
    """Close the browser instance with error handling."""
    try:
        return await browser_agent.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/browser/cookies")
async def get_cookies():
    """Get all cookies from the current browser context."""
    try:
        return await browser_agent.get_cookies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/cookies/add")
async def add_cookies(cookies: List[Dict[str, Any]]):
    """Add cookies to the current browser context."""
    try:
        return await browser_agent.add_cookies(cookies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/cookies/delete")
async def delete_cookies(cookies: List[Dict[str, Any]]):
    """Delete cookies from the current browser context."""
    try:
        return await browser_agent.delete_cookies(cookies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    """Close the browser instance"""
    return await browser_agent.close()
