# Gen AI Workspace

A shared Python environment (`.venv`, `.env`, `requirements.txt`) for multiple notebook-based Generative AI projects, organized by topic into subfolders.

```
.
├── .venv/                # shared virtual environment (not committed)
├── .env                  # shared API keys (not committed)
├── .env.example          # template for .env
├── requirements.txt      # shared Python dependencies for all projects
├── README.md
└── <topic>/               # one folder per project area, grouped by topic
```

Each subfolder is self-contained and may include its own notebooks, README, and supporting assets (images, data, etc.), but all share the same environment and dependencies defined here.

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

Copy `.env.example` to `.env` and fill in your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## 4. Run a Notebook

```bash
jupyter notebook
```

Then open the notebook for the project you want to explore under its topic folder.
