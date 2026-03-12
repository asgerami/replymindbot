-- ReplyMind Supabase Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Business Owners
CREATE TABLE business_owners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_bot_token TEXT NOT NULL,
    telegram_id TEXT,
    owner_name TEXT NOT NULL,
    plan_tier TEXT DEFAULT 'Starter',
    auto_reply_rules JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customers
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_owner_id UUID REFERENCES business_owners(id) ON DELETE CASCADE,
    telegram_id TEXT NOT NULL,
    first_name TEXT,
    username TEXT,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(business_owner_id, telegram_id)
);

-- Memory Profiles
CREATE TABLE memory_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID UNIQUE REFERENCES customers(id) ON DELETE CASCADE,
    historical_orders JSONB DEFAULT '[]'::jsonb,
    preferences TEXT DEFAULT 'Amharic/English',
    summary TEXT,
    lifetime_interactions INT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    business_owner_id UUID REFERENCES business_owners(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'Open',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type TEXT NOT NULL CHECK (sender_type IN ('Customer', 'Assistant', 'Owner')),
    content TEXT NOT NULL,
    confidence_score FLOAT,
    status TEXT DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics Events
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_owner_id UUID REFERENCES business_owners(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
