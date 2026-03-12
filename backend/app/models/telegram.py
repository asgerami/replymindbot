from pydantic import BaseModel, Field
from typing import Optional

class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str] = None
    language_code: Optional[str] = None

class TelegramChat(BaseModel):
    id: int
    first_name: Optional[str] = None
    username: Optional[str] = None
    type: str

class TelegramMessage(BaseModel):
    message_id: int
    from_: Optional[TelegramUser] = Field(None, alias='from')
    chat: TelegramChat
    date: int
    text: Optional[str] = None

class TelegramWebhookPayload(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
