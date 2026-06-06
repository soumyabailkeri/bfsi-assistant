from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

# Load and split document
def load_documents():
    loader = TextLoader("banking_policy.txt")
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    return chunks

# Create vector store
def create_vector_store():
    chunks = load_documents()
    
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    return vectorstore

# Search and answer
def rag_answer(question: str, vectorstore) -> str:
    # Find relevant chunks
    relevant_docs = vectorstore.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    messages = [
        SystemMessage(content="""You are a helpful banking assistant. 
        Answer questions based ONLY on the provided policy document context.
        If the answer is not in the context, say so clearly.
        Always cite which policy section your answer comes from."""),
        HumanMessage(content=f"""Context from banking policy:
{context}

Question: {question}""")
    ]
    
    response = llm.invoke(messages)
    return response.content

# Initialize vector store once
vectorstore = create_vector_store()
print("Vector store created successfully!")

if __name__ == "__main__":
    # Test it
    questions = [
        "What documents do I need for a home loan?",
        "What is the maximum ATM withdrawal per day?",
        "What is the minimum credit score for a personal loan?"
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {rag_answer(q, vectorstore)}")