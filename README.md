# ReplyMind Bot

ReplyMind Bot is an AI-powered Telegram assistant designed for business owners to automate customer interactions. It intelligently routes messages based on confidence scores, provides auto-replies for routine inquiries, and drafts responses for complex queries.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **LLM:** Anthropic Claude 3
- **Hosting:** Render

---

## 🚀 Local Development Setup

Follow these steps to run the bot on your local machine.

### 1. Prerequisites
- Python 3.12+ installed
- A Supabase account and project
- An Anthropic API key
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 2. Clone the Repository
```bash
git clone https://github.com/asgerami/replymindbot.git
cd replymindbot
```

### 3. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Environment Variables
Create a `.env` file in the `backend` directory:
```bash
touch .env
```
Add the following keys to your `.env` file:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 6. Database Setup
1. Go to your Supabase project dashboard.
2. Open the SQL Editor and run the script found in `backend/database_schema.sql` to create the required tables.
3. Add a row to the `business_owners` table with your Telegram `telegram_bot_token` and your personal `telegram_id` (so the bot can alert you).
4. Copy the generated `id` (UUID) from this row—you will need it for the webhook setup.

### 7. Run the Server Locally
```bash
uvicorn app.main:app --reload
```
The server will start at `http://localhost:8000`.

*Note: Telegram webhooks require a public HTTPS URL. For local testing, use a tool like [Ngrok](https://ngrok.com/) to expose your local port 8000.*

---

## 🌍 Deployment on Render

The live version of the bot is hosted on Render.

### Deployment Configuration
When setting up a new Web Service on Render, use the following settings:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory:** `backend` (⚠️ Crucial setting)

### Environment Variables on Render
Add these under the `Environment` tab in your Render dashboard:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `ANTHROPIC_API_KEY`

---

## 🔗 Telegram Webhook Configuration

When deployed (or running via Ngrok), you must register your URL so Telegram knows where to send incoming messages.

Open your browser and navigate to the following URL (replace the bracketed items):

```text
https://api.telegram.org/bot\<YOUR_BOT_TOKEN\>/setWebhook\?url\=https://\<YOUR_RENDER_URL\>/webhook/telegram/\<YOUR_OWNER_UUID\>
```

- `<YOUR_BOT_TOKEN>`: The token from @BotFather.
- `<YOUR_RENDER_URL>`: Your deployed address (e.g., `replymindbot.onrender.com`).
- `<YOUR_OWNER_UUID>`: The UUID copied from the `business_owners` Supabase table.

If successful, you will see a JSON response stating `"Webhook was set"`.
