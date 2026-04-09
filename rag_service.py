import os
from dataclasses import dataclass
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


load_dotenv()

DEFAULT_CHUNK_SIZE = 500
DEFAULT_TOP_K = 3
EMBEDDING_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "gemini-2.5-flash"
REQUEST_TIMEOUT = 20
USER_AGENT = "Mozilla/5.0 (compatible; GeminiURLRAGStreamlit/1.0)"
FALLBACK_ANSWER = "I don't know based on the provided document."


@dataclass(frozen=True)
class BuildResult:
    """Small container holding everything created during indexing."""
    vectorstore: FAISS
    chunks: List[str]
    raw_text: str


def validate_environment() -> str:
    """Return the Gemini API key or raise a clear error."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY was not found. Add it to your environment or a local .env file."
        )
    return api_key


    """Step 1: download the page and keep only readable text."""
def scrape_url(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    text = soup.get_text(separator=" ")
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        raise ValueError("The URL was fetched, but no readable text was found.")

    return cleaned_text


    """Step 2: break the page into smaller chunks for retrieval."""
def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
    words = text.split()
    if not words:
        return []

    return [
        " ".join(words[index:index + chunk_size])
        for index in range(0, len(words), chunk_size)
    ]


    """Step 3: turn chunks into embeddings and store them in FAISS."""
def build_vectorstore(url: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> BuildResult:
    validate_environment()

    raw_text = scrape_url(url)
    chunks = chunk_text(raw_text, chunk_size=chunk_size)
    if not chunks:
        raise ValueError("The page content could not be split into chunks.")

    documents = [
        Document(page_content=chunk, metadata={"source": url, "chunk_number": index + 1})
        for index, chunk in enumerate(chunks)
    ]

    # Gemini converts each chunk into a numeric vector called an embedding.
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(documents, embeddings)
    return BuildResult(vectorstore=vectorstore, chunks=chunks, raw_text=raw_text)


    """Step 4: retrieve the best chunks, then ask Gemini to answer from them."""
def answer_question(
    vectorstore: FAISS,
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> Tuple[str, List[Document]]:
    validate_environment()

    # The retriever finds the chunks most related to the user's question.
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    prompt = ChatPromptTemplate.from_template(
        """Answer the question based ONLY on the following context.
If the context does not contain the answer, say exactly: "I don't know based on the provided document."

Context:
{context}

Question: {input}"""
    )

    # Gemini gets both the question and the retrieved chunks as context.
    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0)
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
    response = rag_chain.invoke({"input": question})

    answer = (response.get("answer") or "").strip() or FALLBACK_ANSWER
    context_docs = response.get("context", [])
    return answer, context_docs
