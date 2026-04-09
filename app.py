from typing import Any, Dict, Optional

import requests
import streamlit as st

from rag_service import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TOP_K,
    FALLBACK_ANSWER,
    answer_question,
    build_vectorstore,
    validate_environment,
)


st.set_page_config(
    page_title="Simple Web RAG",
    page_icon=":material/menu_book:",
    layout="wide",
)


def init_state() -> None:
    if "vector_cache" not in st.session_state:
        st.session_state.vector_cache = {}
    if "active_key" not in st.session_state:
        st.session_state.active_key = None
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None
    if "last_context_docs" not in st.session_state:
        st.session_state.last_context_docs = []
    if "last_error" not in st.session_state:
        st.session_state.last_error = None


def reset_session() -> None:
    st.session_state.vector_cache = {}
    st.session_state.active_key = None
    st.session_state.last_answer = None
    st.session_state.last_context_docs = []
    st.session_state.last_error = None


def build_cache_key(url: str, chunk_size: int) -> str:
    return f"{url.strip()}::{chunk_size}"


def get_cached_index(cache_key: str) -> Optional[Dict[str, Any]]:
    return st.session_state.vector_cache.get(cache_key)


def format_user_error(error: Exception) -> str:
    if isinstance(error, EnvironmentError):
        return "Your Gemini API key is missing. Add `GEMINI_API_KEY` to your `.env` file first."

    if isinstance(error, ValueError):
        message = str(error)
        if "readable text" in message:
            return "I opened the page, but I could not find readable text on it."
        if "split into chunks" in message:
            return "The page content was too small or empty, so the app could not build the knowledge base."
        return message

    if isinstance(error, requests.HTTPError):
        return "The website returned an error. Check the URL and make sure the page is public."

    if isinstance(error, requests.ConnectionError):
        return "I could not reach that website. Check your internet connection and the URL."

    if isinstance(error, requests.Timeout):
        return "The website took too long to respond. Please try again."

    if isinstance(error, requests.RequestException):
        return "There was a problem reading that website. Please try another public URL."

    return (
        "Something went wrong while talking to Gemini or building the app data. "
        "Please try again."
    )


def handle_build(url: str, chunk_size: int) -> None:
    if not url.strip():
        raise ValueError("Please enter a URL before building the knowledge base.")

    cache_key = build_cache_key(url, chunk_size)
    cached_index = get_cached_index(cache_key)
    st.session_state.last_error = None
    st.session_state.last_answer = None
    st.session_state.last_context_docs = []

    if cached_index:
        st.session_state.active_key = cache_key
        return

    with st.spinner("Reading the website and creating your knowledge base..."):
        build_result = build_vectorstore(url=url, chunk_size=chunk_size)

    st.session_state.vector_cache[cache_key] = {
        "url": url.strip(),
        "chunk_size": chunk_size,
        "vectorstore": build_result.vectorstore,
        "chunks": build_result.chunks,
        "raw_text": build_result.raw_text,
    }
    st.session_state.active_key = cache_key


def handle_question(question: str, top_k: int) -> None:
    active_key = st.session_state.active_key
    if not active_key:
        raise ValueError("Build the knowledge base first, then ask your question.")

    cached_index = st.session_state.vector_cache[active_key]
    with st.spinner("Thinking about your question..."):
        answer, context_docs = answer_question(
            vectorstore=cached_index["vectorstore"],
            question=question,
            top_k=top_k,
        )

    st.session_state.last_answer = answer
    st.session_state.last_context_docs = context_docs
    st.session_state.last_error = None


def render_header() -> None:
    st.title("Simple Web RAG")
    st.caption("A beginner-friendly app that reads a web page and lets you ask questions about it.")

    st.markdown(
        """
        **What this app does**  
        You give this app a web page URL.  
        It reads the page, saves the important parts in a searchable format,
        and then uses Gemini to answer your questions using that page as evidence.
        """
    )

    with st.expander("How to use this app", expanded=True):
        st.markdown(
            """
            1. Paste a public website URL.
            2. Click **Build Knowledge Base**.
            3. Ask questions about that page.
            """
        )

    with st.expander("How it works under the hood", expanded=False):
        st.markdown(
            """
            1. **Fetch the page**: the app downloads the web page and keeps the readable text.
            2. **Split into chunks**: the text is broken into smaller pieces so retrieval is easier.
            3. **Create embeddings + store them**: Gemini embeddings turn each chunk into numbers, and FAISS stores them for fast search.
            4. **Retrieve + answer**: when you ask a question, the app finds the most relevant chunks and sends them to Gemini to answer from.
            """
        )


def render_api_status() -> None:
    try:
        validate_environment()
        st.success("API key loaded. The app is ready.")
    except EnvironmentError as exc:
        st.error(format_user_error(exc))
        st.info("Open `.env`, add your Gemini key, save the file, and refresh the app.")


def render_status() -> None:
    active_key = st.session_state.active_key
    if not active_key:
        st.info("Step 1: Add a URL below, then click **Build Knowledge Base**.")
        return

    cached_index = st.session_state.vector_cache[active_key]
    st.success("Knowledge base is ready.")
    st.write(
        "The app has read the page, split it into smaller text chunks, and stored those chunks in a searchable vector database."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Chunks created", len(cached_index["chunks"]))
    with col2:
        st.metric("Chunk size", cached_index["chunk_size"])

    st.markdown(f"**Source URL:** `{cached_index['url']}`")


def render_answer() -> None:
    if not st.session_state.last_answer:
        st.info("Step 3: Ask a question after the knowledge base is ready.")
        return

    st.subheader("Answer")
    st.caption("This is Gemini's answer based on the page content that was retrieved.")
    if st.session_state.last_answer == FALLBACK_ANSWER:
        st.warning(st.session_state.last_answer)
    else:
        st.write(st.session_state.last_answer)

    docs = st.session_state.last_context_docs
    if docs:
        st.caption("The section below shows the evidence chunks used to answer your question.")
        with st.expander("See why the app answered this", expanded=False):
            for index, doc in enumerate(docs, start=1):
                source = doc.metadata.get("source", "Unknown source")
                chunk_number = doc.metadata.get("chunk_number", "?")
                st.markdown(
                    f"**Source chunk {index}**  \n"
                    f"Page: `{source}`  \n"
                    f"Chunk number: `{chunk_number}`"
                )
                st.write(doc.page_content)
                if index < len(docs):
                    st.divider()


def main() -> None:
    init_state()
    render_header()
    render_api_status()

    st.subheader("Step 1: Choose a web page")
    url = st.text_input(
        "Website URL to learn from",
        value="https://example.com",
        placeholder="https://example.com",
    )

    with st.expander("Advanced settings", expanded=False):
        st.write("You can ignore these settings for now. The default values are good for learning.")
        chunk_size = st.number_input(
            "Chunk size",
            min_value=100,
            max_value=2000,
            value=DEFAULT_CHUNK_SIZE,
            step=100,
            help="This controls how much text goes into each chunk. Bigger chunks keep more text together.",
        )
        top_k = st.slider(
            "How many matching chunks to use",
            min_value=1,
            max_value=10,
            value=DEFAULT_TOP_K,
            help="This controls how many relevant chunks are sent to Gemini when answering.",
        )

    build_col, reset_col = st.columns([3, 1])
    with build_col:
        if st.button("Build Knowledge Base", type="primary", use_container_width=True):
            try:
                handle_build(url=url, chunk_size=int(chunk_size))
            except Exception as exc:
                st.session_state.last_error = format_user_error(exc)

    with reset_col:
        if st.button("Reset Session", use_container_width=True):
            reset_session()

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    render_status()

    st.subheader("Step 3: Ask a question")
    question = st.text_input(
        "Ask a question about the page",
        placeholder="What is the main idea of this page?",
    )

    ask_disabled = st.session_state.active_key is None or not question.strip()
    if st.button("Ask Question", use_container_width=True, disabled=ask_disabled):
        try:
            handle_question(question=question.strip(), top_k=int(top_k))
        except Exception as exc:
            st.session_state.last_error = format_user_error(exc)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    render_answer()


if __name__ == "__main__":
    main()
