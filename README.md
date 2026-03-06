
# 🤣 Joke Bot

A retrieval-augmented chatbot that answers with jokes from a curated 100-joke database. Built with Flask, containerised with Docker, and deployed to Google Cloud Run.

## How it works

1. `FetchJokes.py` pulls 100 unique, filtered jokes from [JokeAPI v2](https://v2.jokeapi.dev/) and saves them to `jokes_database.json`
2. On startup, `app.py` loads the database into memory
3. User messages are sent to OpenRouter (Claude 3 Haiku) with the full joke database injected as system context
4. The LLM retrieves relevant jokes naturally — it cannot generate new ones outside the database

## Stack

| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| LLM | Claude 3 Haiku via OpenRouter |
| Joke source | JokeAPI v2 |
| Containerisation | Docker |
| Deployment | Google Cloud Run |

## Project structure

```
.
├── app.py                  # Flask app + OpenRouter integration
├── FetchJokes.py           # Data pipeline — fetches and stores jokes
├── jokes_database.json     # 100-joke static database
├── templates/
│   └── index.html          # Chat UI
├── Dockerfile
└── requirements.txt
```

## Setup

Create a `.env` file in the root directory with the following:

```
OPENROUTER_API_KEY=your_key_here
```