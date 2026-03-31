from openai import AsyncOpenAI
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if not self._client:
            api_key = (settings.OPENAI_KEY or settings.OPENAI_API_KEY or "").strip()
            if not api_key:
                logger.warning("OpenAI API key is missing. Using dummy key for now.")
                api_key = "sk-dummy"
            self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    async def generate_reply(self, owner_name: str, target_message: str, customer_profile: dict, history: list) -> dict:
        system_prompt = f"""
        You are {owner_name}'s Assistant on Telegram.
        You use the 'Habesha Politeness Layer' - balancing professional respect with local warmth.
        Respond nicely. If uncertain, lower your confidence score so the human owner can review.
        """
        
        prompt = f"""
        Customer Profile: {customer_profile}
        Recent History: {history}
        New Message: "{target_message}"
        
        Generate a thoughtful reply. Assess your confidence in auto-replying (0.0 to 1.0).
        High confidence (>0.9) for standard questions. Medium (0.7-0.9) if you need a quick check. Low (<0.7) for complex help.
        
        Output format should be strictly JSON:
        {{
            "reply_text": "...",
            "confidence": 0.95
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=500,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content
            
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                return json.loads(content[start_idx:end_idx])
            else:
                return {"reply_text": "I will need to ask my owner to clarify that.", "confidence": 0.0}
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return {"reply_text": "Apologies, I'm having trouble thinking.", "confidence": 0.0}
