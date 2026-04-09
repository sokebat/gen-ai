# Simple Web RAG

RAG means Retrieval-Augmented Generation. In simple words, the app reads a web page, finds the most useful parts, and then uses Gemini to answer your question from that page.

This app:

- scrapes text from a public URL
- chunks the content
- builds a FAISS vector store with Gemini embeddings
- answers questions with Gemini using retrieved page context

## What Each File Does

- `app.py`: This is the Streamlit user interface. It shows the input boxes, buttons, status messages, and answers.
- `rag_service.py`: This is the RAG logic. It does the scraping, chunking, embedding, vector storage, and answering.
- `requirements.txt`: This lists the Python packages the project needs.
- `.env`: This stores your Gemini API key locally.

## Virtual Environment Setup

This project is intended to run inside a local virtual environment named `.venv`.

### Windows PowerShell

Create the environment:

```powershell
py -3 -m venv .venv
```

If `py` is not available, try:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip and install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### One-command setup

You can also use the included PowerShell helper:

```powershell
.\setup_venv.ps1
```

## Environment Variables

Copy `.env.example` to `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Run

Make sure `.venv` is activated, then run:

```powershell
streamlit run app.py
```

## First Run Example

1. Start the app with `streamlit run app.py`
2. Paste a public URL like `https://example.com`
3. Click **Build Knowledge Base**
4. Ask a question like `What is this page about?`

## How It Works Under the Hood

This app follows a simple RAG pipeline:

1. You enter a URL in the Streamlit app.
2. `app.py` calls `build_vectorstore()` from `rag_service.py`.
3. `scrape_url()` downloads the page and extracts readable text.
4. `chunk_text()` splits that text into smaller chunks.
5. Gemini embeddings convert each chunk into a vector.
6. FAISS stores those vectors so the app can search them quickly later.
7. When you ask a question, `answer_question()` retrieves the most relevant chunks.
8. Gemini receives your question plus those chunks and writes the final answer.

## Project Flow

- user enters URL
- app scrapes text
- text becomes chunks
- chunks become embeddings
- FAISS stores them
- retriever finds the best chunks
- Gemini answers from those chunks

