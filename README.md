# ReplyMind: AI Customer Service for Telegram

ReplyMind acts as the "brain" behind a business's official Telegram bot. It automates 80% of customer service inquiries using OpenAI's GPT models, while seamlessly handing off complex, edge-case questions back to the human business owners directly within Telegram.

## 🌟 How It Works (The Core Flow)

There are two primary users in the ReplyMind ecosystem:
1. **The Business Owner (Your Client)**: E.g., a restaurant owner, an online store operator, or a real estate agent.
2. **The Customer (The End User)**: The person messaging the business to buy food, ask about a product, etc.

### Phase 1: Onboarding
1. **The Business Owner** creates their own bot on Telegram by talking to `@BotFather` and secures a **Bot Token**.
2. They sign up on the **ReplyMind Web Dashboard**.
3. They input their newly created **Bot Token** and their personal **Telegram ID**.
4. The Web Dashboard automatically tells Telegram to route all incoming messages from this new bot to the ReplyMind backend API.

### Phase 2: AI Auto-Responses (High Confidence)
1. A **Customer** opens Telegram and messages the business bot (e.g., *"What time do you close today?"*).
2. The ReplyMind Backend processes the message, retrieves the specific business rules for that owner, and asks the **OpenAI LLM** for a response.
3. If the AI knows the answer based on the rules (generates a **high confidence score**), ReplyMind instantly responds to the customer. 
4. *Result: The Customer receives immediate, accurate customer service.*

### Phase 3: Human Handoff (Low Confidence)
1. A **Customer** asks a highly specific or unusual question (e.g., *"Can you cater a 300-person completely vegan wedding?"*).
2. ReplyMind asks the AI, which generates a **low confidence score** (it doesn't have enough context to answer accurately).
3. ReplyMind does **NOT** respond to the customer. Instead, it sends an **Alert** directly to the **Business Owner's personal Telegram account**:
   > 🚨 *Action Required: New complex message from John.*
   > *Message: "Can you cater a 300-person completely vegan wedding?"*
   > 👉 *Reply directly to this message to answer the customer.*
4. **The Business Owner** swipes left to **Reply** to the alert message on their phone and types their human answer.
5. ReplyMind catches the Owner's text and seamlessly forwards it back to the Customer.
6. *Result: Complex edge-cases are handled personally by the owner without ever leaving the Telegram app.*

---

## 🛠 Tech Stack
- **Backend Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **AI / LLM:** OpenAI GPT-4o-mini
- **Frontend / Dashboard:** React, Vite, TailwindCSS
- **Hosting:** Render (Backend), Vercel/Netlify (Frontend)

---

## 🚀 Local Development Setup

Follow these steps to run the bot and the web dashboard on your local machine.

### 1. Prerequisites
- Python 3.12+ installed
- Node.js v18+ installed
- A Supabase account and project
- An OpenAI API key
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 2. Clone the Repository
```bash
git clone https://github.com/asgerami/replymindbot.git
cd replymindbot
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_KEY=your_openai_api_key
```

Run the backend server:
```bash
uvicorn app.main:app --reload
```
*Note: Telegram webhooks require a public HTTPS URL. For local backend testing, use a tool like [Ngrok](https://ngrok.com/) to expose port 8000.*

### 4. Database Setup
1. Go to your Supabase project dashboard.
2. Open the SQL Editor and run the script found in `backend/database_schema.sql` to create all required tables (Business Owners, Customers, Conversations, Messages, Analytics).

### 5. Frontend Setup
```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend` directory:
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Run the frontend dashboard:
```bash
npm run dev
```

---

## 🌍 Deployment on Render (Backend)

The live version of the FastAPI bot server is hosted on Render.

1. Create a new "Web Service" on Render.
2. Select your repository.
3. Configuration Settings:
   - **Root Directory:** `backend` (⚠️ Crucial setting)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables from your local `.env`.

Once deployed, use the React Web Dashboard to securely set up your Bot Token webhook and start serving customers automatically!
