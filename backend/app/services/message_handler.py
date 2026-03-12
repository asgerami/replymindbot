import logging
from app.models.telegram import TelegramWebhookPayload
from app.services.supabase_client import get_supabase
from app.services.llm_service import LLMService

# Import our new Telegram client
from app.services.telegram_client import send_telegram_message

# Import the new Memory Service
from app.services.memory_service import get_or_create_customer_profile, get_recent_history

logger = logging.getLogger(__name__)
llm = LLMService()

async def process_telegram_update(owner_id: str, payload: dict):
    """
    Core pipeline: Parse -> Retrieve Memory -> LLM Score & Reply -> Route.
    """
    try:
        update = TelegramWebhookPayload(**payload)
        
        if not update.message or not update.message.text:
            return
            
        tg_user = update.message.from_
        msg_text = update.message.text
        chat_id = update.message.chat.id
        
        logger.info(f"Processing message '{msg_text}' from {tg_user.first_name}")
        
        # 1. Initialize Supabase Client
        db = get_supabase()
        
        # Fetch Owner details to get the Bot Token dynamically!
        owner_res = db.table('business_owners').select('owner_name, telegram_bot_token, telegram_id').eq('id', owner_id).execute()
        
        if not owner_res.data:
            logger.error(f"Owner {owner_id} not found in database.")
            return
            
        owner = owner_res.data[0]
        owner_name = owner.get('owner_name', 'Business Owner')
        bot_token = owner.get('telegram_bot_token')
        
        if not bot_token:
            logger.error(f"Bot token missing for owner {owner_id}.")
            return
            
        owner_tg_id = owner.get('telegram_id')
        
        # --- OWNER ROUTING ---
        if owner_tg_id and str(tg_user.id) == str(owner_tg_id):
            logger.info("Message is from the Business Owner.")
            if update.message.reply_to_message and update.message.reply_to_message.text:
                prev_text = update.message.reply_to_message.text
                if "Customer TG ID:" in prev_text:
                    import re
                    match = re.search(r"Customer TG ID:\s*(\d+)", prev_text)
                    if match:
                        dest_tg_id = match.group(1)
                        # Owner sending a reply back to customer
                        await send_telegram_message(bot_token, dest_tg_id, msg_text)
                        
                        # Log it into the conversation
                        cust_res = db.table('customers').select('id').eq('business_owner_id', owner_id).eq('telegram_id', dest_tg_id).execute()
                        if cust_res.data:
                            cust_db_id = cust_res.data[0]['id']
                            conv_res = db.table('conversations').select('id').eq('customer_id', cust_db_id).eq('status', 'Open').execute()
                            if conv_res.data:
                                db.table('messages').insert({
                                    'conversation_id': conv_res.data[0]['id'],
                                    'sender_type': 'Owner',
                                    'content': msg_text,
                                    'status': 'Sent'
                                }).execute()
                                
                        await send_telegram_message(bot_token, owner_tg_id, "✅ Reply successfully sent to customer.")
                        return
                    else:
                        await send_telegram_message(bot_token, owner_tg_id, "⚠️ Could not parse Customer Telegram ID from the message you replied to.")
                        return
                else:
                    await send_telegram_message(bot_token, owner_tg_id, "⚠️ Please reply to an official alert message containing a 'Customer TG ID'.")
                    return
            else:
                await send_telegram_message(bot_token, owner_tg_id, "💡 You are recognized as the Business Owner. To reply to a customer, please use Telegram's 'Reply' feature on one of the alert messages.")
                return
        # --- END OWNER ROUTING ---
            
        # 2. Memory Context Layer
        # Retrieve or initialize the Customer's Memory Profile
        customer_profile = await get_or_create_customer_profile(owner_id, tg_user)
        
        # Retrieve recent conversation history specific to this customer
        history = await get_recent_history(owner_id, tg_user.id, limit=6)
        
        # Determine the Customer ID from the profile
        customer_id = customer_profile.get('customer_id')
        
        # 3. Conversation & Message Logging
        # Find or create an active conversation for the customer
        conv_res = db.table('conversations').select('id').eq('customer_id', customer_id).eq('status', 'Open').execute()
        
        if not conv_res.data:
            new_conv = db.table('conversations').insert({
                'customer_id': customer_id,
                'business_owner_id': owner_id,
                'status': 'Open'
            }).execute()
            conversation_id = new_conv.data[0]['id']
        else:
            conversation_id = conv_res.data[0]['id']
            
        # Log the incoming customer message
        db.table('messages').insert({
            'conversation_id': conversation_id,
            'sender_type': 'Customer',
            'content': msg_text,
            'status': 'Received'
        }).execute()
        
        # 4. Intelligence Layer
        response_data = await llm.generate_reply(
            owner_name=owner_name,
            target_message=msg_text,
            customer_profile=customer_profile,
            history=history
        )
        
        confidence = response_data.get("confidence", 0.0)
        reply = response_data.get("reply_text", "")
        
        logger.info(f"LLM Reply Score {confidence}: {reply}")
        
        # 5. Routing Based on Confidence
        if confidence >= 0.90:
            logger.info("ROUTING: High Confidence -> Auto-Reply directly to customer")
            success = await send_telegram_message(bot_token, chat_id, reply)
            
            if success:
                # Log the sent message
                db.table('messages').insert({
                    'conversation_id': conversation_id,
                    'sender_type': 'Assistant',
                    'content': reply,
                    'confidence_score': confidence,
                    'status': 'Sent'
                }).execute()
                
                # Log the Analytics Event
                db.table('analytics_events').insert({
                    "business_owner_id": owner_id,
                    "event_type": "Auto_Replied",
                    "metadata": {"confidence": confidence, "message_length": len(reply)}
                }).execute()
                
        elif confidence >= 0.70:
            logger.info("ROUTING: Medium Confidence -> Save to Owner's Draft Queue")
            db.table('messages').insert({
                'conversation_id': conversation_id,
                'sender_type': 'Assistant',
                'content': reply,
                'confidence_score': confidence,
                'status': 'Draft'
            }).execute()
            
            db.table('analytics_events').insert({
                "business_owner_id": owner_id,
                "event_type": "Draft_Created",
                "metadata": {"confidence": confidence}
            }).execute()
            
        else:
            logger.info("ROUTING: Low Confidence -> Alert Owner")
            db.table('messages').insert({
                'conversation_id': conversation_id,
                'sender_type': 'Assistant',
                'content': reply,
                'confidence_score': confidence,
                'status': 'Action_Required'
            }).execute()
            
            # Send an alert to the owner (you could use the bot to message the owner directly)
            # Find owner's telegram ID if stored, and send them a message:
            owner_tg_id = owner.get('telegram_id') # Assuming this exists
            if owner_tg_id:
                alert_text = f"🚨 Action Required: New complex message from {tg_user.first_name}.\nCustomer TG ID: {tg_user.id}\n\nMessage: \"{msg_text}\"\n\n👉 Reply directly to this message to answer the customer."
                await send_telegram_message(bot_token, owner_tg_id, alert_text)
                
            db.table('analytics_events').insert({
                "business_owner_id": owner_id,
                "event_type": "Action_Required",
                "metadata": {"confidence": confidence}
            }).execute()
            
    except Exception as e:
        logger.error(f"Error processing update: {e}")
