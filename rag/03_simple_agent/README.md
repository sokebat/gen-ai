# Simple Agent

A minimal LangChain **ReAct agent**: instead of a fixed pipeline, the LLM decides at each step whether it needs a tool, which one, and what to pass it — looping `Thought → Action → Observation` until it has enough to give a `Final Answer`.

Two tools are wired in:

- **Web search** (`langchain_tavily.TavilySearch`) — for open-ended, current-events questions.
- **`get_weather_data`** — a custom `@tool`-decorated function that calls the Weatherstack REST API for live weather by city.

This is what lets the agent handle a question like *"Find the capital of India and then find its current weather"*: neither tool alone answers it, but the agent chains web search → weather lookup on its own.

## Notebook

- `01_react_agent.ipynb` — builds the tools, LLM, ReAct prompt, and `AgentExecutor`, then runs a multi-step query.

## Setup

This project uses the repo's shared `.venv`, `requirements.txt`, and `GEMINI_API_KEY` (see the root [README](../README.md)). It additionally needs a Weatherstack key in the root `.env`:

```env
WEATHERSTACK_API_KEY=your_weatherstack_api_key_here
```

Get a free Weatherstack key at [weatherstack.com](https://weatherstack.com/).
