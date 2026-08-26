# RAG Projects

This repo holds one shared Python environment (`.venv`, `.env`, `requirements.txt`) used by multiple notebook-based RAG projects, each in its own subfolder.

```
.
├── .venv/                 # shared virtual environment (not committed)
├── .env                   # shared Gemini API key (not committed)
├── .env.example           # template for .env
├── requirements.txt       # shared Python dependencies for all projects
├── README.md
├── 01_web-rag/             # project: reads a public web page, answers questions about it
├── 02_corrective-rag/      # project: RAG with retrieval grading and web-search fallback
└── 03_simple_agent/        # project: minimal ReAct agent with web search + weather tools
```

## 1. Create the Virtual Environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate
```

If `py` is not available, use `python -m venv .venv` instead.

## 2. Install Dependencies

With `.venv` activated:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Set Your Environment Variables

Copy `.env.example` to `.env` (already done for you if you're reading this after setup) and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```


