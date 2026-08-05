"""
ingest.py — SIFRA
Reads regulatory PDFs from data/, chunks them, embeds with sentence-transformers,
and saves a FAISS vector store to vectorstore/.

Run once before starting the app:
    python ingest.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

DATA_DIR = Path("data")
VECTORSTORE_DIR = Path("vectorstore")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

PDF_FILES = [
    "ADR_2023.pdf",
    "IMDG_2022.pdf",
    "IATA_DGR_2024.pdf",
]


def load_pdfs():
    docs = []
    for filename in PDF_FILES:
        path = DATA_DIR / filename
        if not path.exists():
            print(f"⚠️  Skipping {filename} — not found in data/")
            continue
        print(f"📄 Loading {filename}...")
        loader = PyPDFLoader(str(path))
        pages = loader.load()
        # Tag each page with its source regulation
        for page in pages:
            page.metadata["regulation"] = filename.replace(".pdf", "")
        docs.extend(pages)
        print(f"   → {len(pages)} pages loaded")
    return docs


def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"\n✂️  Split into {len(chunks)} chunks")
    return chunks


def build_vectorstore(chunks):
    print(f"\n🔢 Embedding with {EMBEDDING_MODEL}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    VECTORSTORE_DIR.mkdir(exist_ok=True)
    vectorstore.save_local(str(VECTORSTORE_DIR))
    print(f"✅ Vector store saved to {VECTORSTORE_DIR}/")
    return vectorstore


if __name__ == "__main__":
    print("=== SIFRA Ingestion Pipeline ===\n")

    if not DATA_DIR.exists():
        DATA_DIR.mkdir()
        print(f"Created data/ folder. Add your PDFs there and run again.\n")
        exit(0)

    docs = load_pdfs()

    if not docs:
        print("\n❌ No PDFs loaded. Add PDFs to data/ and run again.")
        exit(1)

    chunks = split_docs(docs)
    build_vectorstore(chunks)
    print("\n🚀 Done! Run `python app.py` to start SIFRA.")
