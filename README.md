# Favorites API

A small FastAPI backend that lets users save their favorite Pokémon. I built it as the backend for my PokéAPI browser, so the React frontend can keep a personal list of favorites instead of only browsing.

## Run it

You only need Docker Desktop running:


git clone git@github.com:Divine-Udeze/POKEAPI-BACKEND.git
cd pokeapi-favorites
docker compose up --build


The API is at <http://localhost:8000> and the interactive docs are at <http://localhost:8000/docs>. There's nothing to configure for a local run.

If you'd rather run it without Docker (Python 3.12+):


python3 -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload


## How it works

You log in with a username at `POST /login` and get a token back. Send that token as `Authorization: Bearer <token>` on every `/favorites` request.

| Method | Path              | What it does                  |
| ------ | ----------------- | ----------------------------- |
| POST   | `/login`          | Get a token for a username    |
| POST   | `/favorites`      | Save a favorite               |
| GET    | `/favorites`      | List your favorites           |
| GET    | `/favorites/{id}` | Get one favorite              |
| PATCH  | `/favorites/{id}` | Change the note               |
| DELETE | `/favorites/{id}` | Remove a favorite             |

Your favorites belong to you: the server takes your id from the token, not from the request, and asking for someone else's favorite returns a 404 so it doesn't even confirm that it exists. Login has no password, which is fine for a learning project and not for anything real.

## Why CORS is set up the way it is

Browsers won't let a web page read responses from a different origin unless that server says it's okay, and CORS is how a server says so. My React app runs on `localhost:5173` and this API on `localhost:8000`, so without CORS the browser would block every request from the app, even though the API works fine in `/docs` or `curl` (they don't enforce it). I turned it on deliberately with FastAPI's `CORSMiddleware`: only the origins listed in `CORS_ORIGINS` are allowed (no `*`), only the methods and headers the app actually uses, and no credentials mode, since the token travels in a header rather than a cookie. Because of that header and the `PATCH`/`DELETE` methods, the browser sends an `OPTIONS` preflight request first, and the middleware answers it.

## Settings

| Variable       | Default                 | What it's for                              |
| -------------- | ----------------------- | ------------------------------------------ |
| `JWT_SECRET`   | a dev-only placeholder  | Signs tokens. Set a real one when deploying. |
| `CORS_ORIGINS` | `http://localhost:5173` | Frontend URLs allowed to call the API (comma-separated). |

## Tests and CI


pytest -v && ruff check . && ruff format --check . && mypy app tests


There are 20 tests covering every endpoint, missing and bad tokens, 404s and validation errors. GitHub Actions runs ruff, mypy and pytest on every pull request, and `main` only accepts changes that pass.

## Known limits

Favorites live in memory, so they disappear when the server restarts. A database is the obvious next step.
