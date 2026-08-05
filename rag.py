"""
rag.py — SIFRA
RAG chain: retrieves relevant chunks from FAISS, sends to Groq LLM,
returns structured compliance verdict.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()

VECTORSTORE_DIR = Path("vectorstore")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

SYSTEM_PROMPT = """You are SIFRA, an expert dangerous goods compliance assistant.
You have access to ADR (road), IMDG (sea), and IATA DGR (air) regulatory documents.

Using ONLY the context provided below, answer the compliance query.
Do not invent rules that are not in the context.

Context:
{context}

Query: {question}

Respond in this exact format:

VERDICT: [COMPLIANT / NON-COMPLIANT / MISSING DATA]
UN NUMBER: [e.g. UN1090 or "Not found in context"]
HAZARD CLASS: [e.g. Class 3 — Flammable Liquid or "Not found"]
PACKING GROUP: [I / II / III or "Not applicable"]
TRANSPORT MODE: [Road (ADR) / Sea (IMDG) / Air (IATA DGR)]
REQUIRED DOCUMENTS:
- [document 1]
- [document 2]
- [document 3]
NOTES: [Any important conditions, exemptions, or quantity limits. If context is insufficient, say so clearly.]
"""


def load_chain():
    if not VECTORSTORE_DIR.exists():
        raise FileNotFoundError(
            "Vector store not found. Run `python ingest.py` first."
        )

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.load_local(
        str(VECTORSTORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6},
    )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    prompt = PromptTemplate(
        template=SYSTEM_PROMPT,
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )

    return chain


def query_compliance(chemical: str, transport_mode: str, chain) -> dict:
    question = (
        f"Is {chemical} compliant for transport by {transport_mode}? "
        f"What is its UN number, hazard class, packing group, and what documents are required?"
    )

    result = chain.invoke({"query": question})
    answer = result["result"]
    sources = result["source_documents"]

    # Extract unique source regulations cited
    regulations = list({doc.metadata.get("regulation", "Unknown") for doc in sources})

    return {
        "answer": answer,
        "sources": regulations,
        "num_chunks": len(sources),
    }
