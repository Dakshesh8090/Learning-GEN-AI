from google.genai import types
import os
from dotenv import load_dotenv
import asyncio
from google import genai
from langchain_huggingface import HuggingFaceEmbeddings  
from langchain_pinecone import PineconeVectorStore

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# History
history = []

async def transform_query(question):
    history.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction="You are a query rewriting expert. Based on the provided chat history , rephrase the follow up user question into a complete, standalone question that can be understood without any chat history. Only output the rewritten question and nothing else. If the question is already standalone, just repeat the question as it is."),
    )

    history.pop()
    return response.text.strip()

    #convert the user query into vector 
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
    

vectorstore = PineconeVectorStore(
    index_name="rag-index",
    embedding=embeddings
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 6}
)

async def chatting(question):

    queries = await transform_query(question)

    docs = retriever.invoke(queries)

    context = "\n\n".join([doc.page_content for doc in docs])


    
    config = types.GenerateContentConfig(
            system_instruction=f"""
            You have to behave like a Data Structure and Algorithm Expert. You will be given a context of relevant information and a user question. Your task is to answer the user's question based only on the provided context. If the answer is not in the context, you must say: 'I could not find the answer in the provided document.' Keep your answers clear, concise, and educational.

            Context:{context}

            User Question: {question}
            """
        )

    
    history.append({
            "role": 'user',
            "parts": [{"text": queries}]
    })

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=history,
        config=config
    )

    history.append({
            "role": 'model',
            "parts": [{"text": response.text}]
        })
    
    print("\nAnswer:", response.text)

async def main():
    print("Starting document indexing...")

    while True:
        user_problem = input("Enter your query:")
        if user_problem.lower() == "exit":
            print("Chat ended")
            break

        await chatting(user_problem)

asyncio.run(main())

