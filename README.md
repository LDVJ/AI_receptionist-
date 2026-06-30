# AI Receptionist

An AI-powered virtual receptionist for hotels. Each hotel gets a unique chat endpoint where guests can ask questions and receive answers grounded strictly in that hotel's own FAQ data — no hallucinated information, with unanswerable questions logged for staff follow-up.

## Problem It Solves

Hotels get repetitive guest questions (check-in time, WiFi password, parking, amenities) that don't need a human every time. This system lets each hotel admin maintain their own FAQ data, and guests get instant, accurate answers — strictly grounded in that hotel's data, with a safe fallback when the AI doesn't know the answer.

## Tech Stack

- **Backend:** FastAPI (async)
- **Database:** PostgreSQL, accessed via async SQLAlchemy (asyncpg driver)
- **Migrations:** Alembic
- **AI:** Google Gemini API (`gemini-2.5-flash`) with structured JSON output
- **Auth:** OAuth2PasswordBearer + JWT (python-jose), 24-hour token expiry
- **Frontend:** Vanilla HTML / CSS / JavaScript (guest chat interface)
- **Deployment:** Render

## Core Architecture Decisions

- **Per-hotel grounding:** Each hotel is identified via a unique `slug`. Guest questions are answered using only that hotel's FAQ data, passed as context to Gemini — never from Gemini's general knowledge.
- **No in-memory AI sessions:** All conversation data is persisted to PostgreSQL. No state is held in memory between requests.
- **Structured AI output:** Gemini is constrained to a JSON schema (`{ "answered": bool, "message": str }`), so the backend can programmatically detect when a question couldn't be answered from the provided context.
- **Unanswerable question handling:** When Gemini cannot answer from the given FAQ context, the guest receives a generic fallback message, and the question is logged to a dedicated table for hotel staff to review and address later — instead of letting the AI guess.

## Database Schema

| Table | Purpose |
|---|---|
| `users` | Hotel admin accounts (auth) |
| `hotels` | Hotel profile, slug, welcome message |
| `hotel_faqs` | FAQ/policy entries per hotel |
| `conversations` | Every guest question + AI response, with an `was_answerable` flag |
| `unanswered_questions` | Questions Gemini couldn't answer, linked to the conversation row, for staff review |

All primary keys are UUIDs stored as `String(32)`.

## API Overview

### Admin (Authenticated)
- `POST /auth/signup` — Create hotel admin account + hotel record
- `POST /auth/login` — Returns JWT
- `POST/PUT/DELETE /faqs` — Manage hotel FAQ entries (admin-scoped)
- `PUT /hotels/welcome-message` — Set/update hotel welcome message

### Guest (Public)
- `GET /chat/{slug}` — Returns hotel's welcome message (or default fallback if unset)
- `POST /chat/{slug}` — Guest sends a question; returns an AI-generated, FAQ-grounded answer

## How a Guest Question Is Handled

1. Guest hits `/chat/{slug}` — backend looks up the hotel by slug.
2. Backend fetches that hotel's FAQ data from PostgreSQL.
3. Question + FAQ context is sent to Gemini with a system prompt restricting it to hotel-provided data only.
4. Gemini returns a structured response: whether it could answer, and the message text.
5. The conversation is logged to the `conversations` table.
6. If Gemini couldn't answer, the question is additionally logged to `unanswered_questions`, and the guest receives a safe fallback message instead of a guess.

## Setup

```bash
# Clone and install dependencies
git clone <repo-url>
cd ai-receptionist
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Fill in: DATABASE_URL, GEMINI_API_KEY, JWT_SECRET_KEY

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

Visit `/docs` for interactive API documentation.

## Known Limitations

- Gemini free-tier quota is limited (20 requests/day at time of writing) — not yet suitable for production-scale traffic without a paid plan.
- Admin frontend (FAQ management UI) is not yet built — FAQ management is currently API-only via `/docs`.
- No automated test suite yet; testing has been manual via `/docs` and the guest chat UI.

## Roadmap

- [ ] Admin-facing frontend for FAQ and welcome message management
- [ ] Automated tests for grounding accuracy and fallback behavior
- [ ] Rate limiting / quota management for Gemini API usage at scale
- [ ] Multi-language support

## Author

Jyotirmay Verma — [GitHub](https://github.com/LDVJ) · [LinkedIn](https://www.linkedin.com/in/jyotirmay-verma-7453392a7/)