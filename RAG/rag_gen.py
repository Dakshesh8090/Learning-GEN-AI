# PDF load karne ka
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import asyncio
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings  

load_dotenv()

async def index_document():
    PDF_PATH = "Dsa.pdf"

    # Load PDF
    loader = PyPDFLoader(PDF_PATH)
    raw_docs = loader.load()

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunked_docs = text_splitter.split_documents(raw_docs)
    print(f"Number of chunks created: {len(chunked_docs)}")

    # Embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    print("Embeddings model initialized successfully.")

    # Pinecone setup
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "rag-index"

    pc.delete_index("rag-index")
    print("Old index deleted ")

    # Create index if not exists
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=384,  
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    # Store chunked docs (NOT raw_docs)
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunked_docs,
        embedding=embeddings,
        index_name=index_name
    )

    print("Data stored successfully ")


async def main():
    print("Starting document indexing...")
    await index_document()

asyncio.run(main())