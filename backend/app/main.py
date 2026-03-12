import logging
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.message_handler import process_telegram_update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ReplyMind Backend API",
    description="FastAPI service for the ReplyMind Telegram Assistant webhook.",
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "ReplyMind API",
        "version": settings.VERSION
    }

@app.post("/webhook/telegram/{owner_id}")
async def telegram_webhook(owner_id: str, request: Request, background_tasks: BackgroundTasks):
    """
    Ingress point for Telegram messages directed to a specific business owner's bot.
    """
    try:
        payload = await request.json()
        logger.info(f"Received webhook for owner: {owner_id}")
        
        # Delegate processing to background task to keep webhook response time fast (<200ms)
        background_tasks.add_task(process_telegram_update, owner_id, payload)
        
    except Exception as e:
        logger.error(f"Error reading webhook payload: {e}")
        
    # Telegram requires an immediate 200 OK response, otherwise it will retry sending the message.
    return {"status": "accepted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
