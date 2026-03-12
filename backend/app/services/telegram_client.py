import httpx
import logging

logger = logging.getLogger(__name__)

async def send_telegram_message(bot_token: str, chat_id: int, text: str) -> bool:
    """
    Sends a text message to a specified Telegram chat using the provided bot token.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully sent message to chat {chat_id}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred while sending telegram message: {e.response.text}")
    except Exception as e:
        logger.error(f"Error sending telegram message: {e}")
        
    return False
