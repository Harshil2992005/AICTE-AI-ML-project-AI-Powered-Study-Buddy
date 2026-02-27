import os
import re
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

load_dotenv()

# Project Configurations
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Study-Buddy-V2"
MAX_FILE_SIZE = 200 * 1024 * 1024
OUT_OF_TOPIC_RESPONSE = "Sorry, you have entered an out-of-topic question. This information is not present in your uploaded documents."

# Mark-Based Logic Definitions
MARK_PROMPTS = {
    "7": "Provide a comprehensive answer (approx 350-420 words) with headings, examples, and analogies. Max 420 words.",
    "4": "Provide a detailed answer (approx 200 words) with bullet points. Max 200 words.",
    "3": "Provide a concise answer (approx 150 words) with 2-3 key points. Max 150 words.",
    "2": "Provide a short answer (approx 80-100 words). Max 100 words.",
    "1": "Provide a one-liner answer (approx 30 words). Answer in EXACTLY ONE SENTENCE."
}

def validate_file_size(file_path):
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        raise ValueError("File exceeds 200MB limit.")

def process_document(file_path):
    validate_file_size(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    loader = PyPDFLoader(file_path) if ext == '.pdf' else UnstructuredWordDocumentLoader(file_path)
    docs = loader.load()
    
    # Optimized Chunking for context preservation
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
    chunks = text_splitter.split_documents(docs)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = FAISS.from_documents(chunks, embeddings)
    setattr(vector_db, 'total_chars', sum(len(d.page_content) for d in docs))
    return vector_db

def detect_marks(query):
    query_lower = query.lower()
    patterns = [(r'\b7\s*marks?\b', '7'), (r'\b4\s*marks?\b', '4'), 
                (r'\b3\s*marks?\b', '3'), (r'\b2\s*marks?\b', '2'), 
                (r'\b(one\s*liner|1\s*mark)\b', '1')]
    for pat, m in patterns:
        if re.search(pat, query_lower): return m
    return None

def get_qa_chain(vector_db):
    llm = ChatOllama(model="llama3", temperature=0.3)
    
    def build_chain(query):
        #  Similarity Thresholding (Lower is better in FAISS)
        docs_with_scores = vector_db.similarity_search_with_score(query, k=5)
        min_score = min(score for doc, score in docs_with_scores)
        
        # Threshold: if score > 1.1, the distance is too high (no match)
        if min_score > 1.1: 
            return OUT_OF_TOPIC_RESPONSE

        context = "\n\n".join(doc.page_content for doc, score in docs_with_scores)
        marks = detect_marks(query)
        instruction = MARK_PROMPTS.get(marks or "", "Explain clearly using bullet points.")
        
        prompt = PromptTemplate.from_template(f"""
        System: You are a strict academic tutor. Answer ONLY using the context below. 
        If info is missing, say: '{OUT_OF_TOPIC_RESPONSE}'.
        Requirement: {instruction}
        Context: {{context}}
        Question: {{question}}
        Answer:""")

        chain = ({"context": lambda x: context, "question": RunnablePassthrough()} 
                 | prompt | llm | StrOutputParser())
        
        response = chain.invoke(query)
        
        #  One-Liner Truncation
        if marks == "1":
            response = response.split('.')[0] + '.'
        return response

    return build_chain

# Summarization, Quiz, and Flashcard functions  ---
def generate_flashcards(vector_db, num_flashcards=5):
    llm = ChatOllama(model="llama3", temperature=0.5)
    retriever = vector_db.as_retriever(search_kwargs={"k": 8})
    retrieved_docs = retriever.invoke("key concepts definitions")
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    prompt = PromptTemplate.from_template("Create {num} flashcards. Format: Q: [Question] A: [Answer]\nContext: {context}")
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"num": num_flashcards, "context": context})
    
    cards = []
    for pair in result.split("Q:")[1:]:
        if "A:" in pair:
            parts = pair.split("A:")
            cards.append({"question": parts[0].strip(), "answer": parts[1].strip()})
    return cards

def summarize_notes(vector_db, word_count=300):
    llm = ChatOllama(model="llama3", temperature=0.3)
    docs = vector_db.as_retriever().invoke("summary")
    context = "\n\n".join(d.page_content for d in docs[:5])
    
    # Context-Aware Summarization
    if vector_db.total_chars < 1000:
        word_count = 150
        warning = "⚠️ Short document; summary limited.\n\n"
    else: warning = ""
        
    prompt = PromptTemplate.from_template(f"Summarize in exactly {word_count} words.\nContext: {{context}}")
    chain = prompt | llm | StrOutputParser()
    summary = chain.invoke({"context": context})
    return warning + " ".join(summary.split()[:word_count])
