import logging
from app.services.supabase_client import get_supabase
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

async def get_or_create_customer_profile(owner_id: str, telegram_user: dict) -> Dict[str, Any]:
    """
    Fetches the customer's memory profile from Supabase, or creates a new 
    customer and empty profile if they are messaging for the first time.
    """
    db = get_supabase()
    tg_id = str(telegram_user.id)
    first_name = telegram_user.first_name
    username = telegram_user.username
    
    # 1. Try to find existing Customer
    customer_res = db.table('customers').select('id, business_owner_id').eq('business_owner_id', owner_id).eq('telegram_id', tg_id).execute()
    
    if not customer_res.data:
        # Create new Customer
        logger.info(f"Creating new customer record for {first_name}")
        new_customer = db.table('customers').insert({
            'business_owner_id': owner_id,
            'telegram_id': tg_id,
            'first_name': first_name,
            'username': username
        }).execute()
        
        customer_id = new_customer.data[0]['id']
        
        # Create initial Memory Profile based on Tier 1 principles (Default settings)
        new_profile = db.table('memory_profiles').insert({
            'customer_id': customer_id,
            'preferences': 'Amharic/English',
            'historical_orders': [],
            'summary': 'New customer'
        }).execute()
        
        return new_profile.data[0]
    else:
        # Existing customer found, get their memory profile
        customer_id = customer_res.data[0]['id']
        logger.info(f"Existing customer found: {customer_id}. Fetching memory profile.")
        
        # Update last_active
        db.table('customers').update({'last_active': 'now()'}).eq('id', customer_id).execute()
        
        profile_res = db.table('memory_profiles').select('*').eq('customer_id', customer_id).execute()
        if profile_res.data:
            # Increment interaction counter
            current_interactions = profile_res.data[0].get('lifetime_interactions', 0)
            db.table('memory_profiles').update({
                'lifetime_interactions': current_interactions + 1,
                'updated_at': 'now()'
            }).eq('id', profile_res.data[0]['id']).execute()
            
            return profile_res.data[0]
            
        return {} # Edge case where profile was deleted

async def get_recent_history(owner_id: str, telegram_user_id: int, limit: int = 10) -> List[Dict[str, str]]:
    """
    Fetches the last N messages across all conversations for this specific user to provide immediate context to the LLM.
    """
    db = get_supabase()
    tg_id = str(telegram_user_id)
    
    # 1. Get the customer ID
    customer_res = db.table('customers').select('id').eq('business_owner_id', owner_id).eq('telegram_id', tg_id).execute()
    if not customer_res.data:
        return []
        
    customer_id = customer_res.data[0]['id']
    
    # 2. Find their active conversation, or get latest messages
    # In Supabase, we can use Foreign Key inner joins.
    # We query messages, joining conversations where conversation.customer_id = customer_id
    history_res = db.table('messages')\
        .select('sender_type, content, created_at, conversation_id!inner(customer_id)')\
        .eq('conversation_id.customer_id', customer_id)\
        .order('created_at', desc=True)\
        .limit(limit)\
        .execute()
        
    # Return formatted history for the LLM
    formatted_history = []
    if history_res.data:
        for msg in reversed(history_res.data): # Reverse to chronological order
            # Map DB sender_type to Anthropic roles
            sender = msg.get("sender_type")
            role = "user" if sender == "Customer" else "assistant"
            
            formatted_history.append({
                "role": role,
                "content": msg.get("content")
            })
            
    return formatted_history
