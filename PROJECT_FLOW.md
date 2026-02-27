# Study Buddy - Technical Documentation & Flow Guide

## 1. Project Overview

### 1.1 What is Study Buddy?

Study Buddy is an AI-powered study assistant application designed to help students learn more effectively from their own study materials. It acts as a personal tutor that can answer questions, generate flashcards, and summarize notes—all powered by local AI technology without sending data to external servers.

### 1.2 Core Problem Solved

Students often struggle with:
- Understanding lengthy textbooks and notes
- Preparing for exams with limited time
- Generating practice questions independently
- Getting concise summaries for quick revision

Study Buddy addresses these challenges by allowing students to upload their PDF or DOCX study materials and interact with them through an intelligent AI interface.

---

## 2. System Architecture & Code Flow

### 2.1 High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Input    │────▶│  Streamlit UI    │────▶│  Core Logic     │
│  (PDF/DOCX)     │     │  (app.py)        │     │ (core_logic.py) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  FAISS Vector   │
                                               │  Database       │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Ollama (LLM)   │
                                               │  Llama 3        │
                                               └─────────────────┘
```

### 2.2 Detailed Code Flow

#### Step 1: Document Upload & Processing

**File:** `app.py` (Lines 126-145)

```
User uploads PDF/DOCX file
        │
        ▼
app.py receives file → Creates temporary file
        │
        ▼
process_document(file_path) called [core_logic.py:34]
        │
        ├──▶ validate_file_size() - Checks if file < 200MB
        │
        ├──▶ Loader Selection:
        │      • PDF → PyPDFLoader
        │      • DOCX → UnstructuredWordDocumentLoader
        │
        ├──▶ Document Loading - Extracts text content
        │
        ├──▶ Text Chunking [core_logic.py:41]
        │      • chunk_size: 1200 characters
        │      • chunk_overlap: 300 characters
        │      • Preserves context between chunks
        │
        ├──▶ Embedding Generation [core_logic.py:44]
        │      • Model: nomic-embed-text
        │      • Converts text chunks to vector embeddings
        │
        └──▶ FAISS Vector Store Creation [core_logic.py:45]
               • Stores embeddings locally
               • Enables similarity search
```

#### Step 2: Question Answering Flow

**File:** `app.py` (Lines 185-226)

```
User enters question with optional marks (e.g., "What is CSMA/CA? 7 marks")
        │
        ▼
get_qa_chain(vector_db) invoked [core_logic.py:58]
        │
        ├──▶ Similarity Search [core_logic.py:63]
        │      • Searches top 5 relevant chunks
        │      • Uses FAISS similarity_search_with_score()
        │
        ├──▶ Relevance Threshold Check [core_logic.py:66-68]
        │      • If score > 1.1 → Returns "Out of Topic" response
        │      • Prevents hallucination
        │
        ├──▶ Mark Detection [core_logic.py:49-56]
        │      • Regex patterns detect: 7, 4, 3, 2, 1 marks
        │      • Maps to word count requirements
        │
        ├──▶ Prompt Construction [core_logic.py:74-80]
        │      • System: Academic tutor persona
        │      • Context: Retrieved document chunks
        │      • Requirement: Mark-based word limit
        │
        ├──▶ LLM Generation [core_logic.py:85]
        │      • Model: Llama 3 (temperature: 0.3)
        │      • Generates answer based on context
        │
        └──▶ Answer Formatting [core_logic.py:88-90]
               • One-liner truncation if 1 mark
```

#### Step 3: Flashcard Generation Flow

**File:** `app.py` (Lines 228-273) and `core_logic.py` (Lines 95-110)

```
User clicks "Generate Flashcards"
        │
        ▼
generate_flashcards(vector_db) called [core_logic.py:95]
        │
        ├──▶ Context Retrieval
        │      • Uses retriever with k=8 documents
        │      • Searches for "key concepts definitions"
        │
        ├──▶ Flashcard Prompt [core_logic.py:101]
        │      • Requests 5 flashcards (default)
        │      • Format: Q: [Question] A: [Answer]
        │
        ├──▶ LLM Generation [core_logic.py:103]
        │      • Llama 3 with temperature 0.5
        │
        ├──▶ Parsing Response [core_logic.py:105-109]
        │      • Splits by "Q:" and "A:" delimiters
        │      • Creates structured flashcard objects
        │
        └──▶ Display in UI with show/hide functionality
```

#### Step 4: Summary Generation Flow

**File:** `app.py` (Lines 275-314) and `core_logic.py` (Lines 112-126)

```
User adjusts word count slider → Clicks "Summarize"
        │
        ▼
summarize_notes(vector_db, word_count) called [core_logic.py:112]
        │
        ├──▶ Document Retrieval
        │      • Top 5 documents retrieved
        │      • Searches for "summary"
        │
        ├──▶ Length Validation [core_logic.py:118-121]
        │      • If document < 1000 chars: limit to 150 words
        │      • Add warning message
        │
        ├──▶ Summarization Prompt [core_logic.py:123]
        │      • "Summarize in exactly X words"
        │
        ├──▶ LLM Generation [core_logic.py:125]
        │
        ├──▶ Word Count Truncation [core_logic.py:126]
        │      • Ensures exact word count
        │
        └──▶ Display with warning if applicable
```

---

## 3. Technical Components

### 3.1 Technology Stack

| Component | Technology | Version/Purpose |
|-----------|------------|-----------------|
| Frontend | Streamlit | Web UI Framework |
| LLM | Ollama (Llama 3) | Local AI Model |
| Embeddings | nomic-embed-text | Text Vectorization |
| Vector DB | FAISS | Similarity Search |
| Framework | LangChain | LLM Orchestration |
| Monitoring | LangSmith | Tracing & Debugging |

### 3.2 Key Features Implemented

1. **Mark-Based Answer System**
   - 7 marks: 350-420 words (detailed essay)
   - 4 marks: 200 words (concise explanation)
   - 3 marks: 150 words (brief answer)
   - 2 marks: 80-100 words (short answer)
   - 1 mark: 30 words (one-liner)

2. **Anti-Hallucination Guardrails**
   - Similarity threshold: 1.1 (FAISS distance)
   - Out-of-topic detection
   - Context-only responses

3. **Document Processing**
   - Supported formats: PDF, DOCX
   - Maximum file size: 200MB
   - Chunk size: 1200 characters
   - Overlap: 300 characters

---

## 4. Legal & Compliance Documentation

### 4.1 Data Privacy

- **Local Processing**: All document processing occurs locally on the user's machine. No data is transmitted to external servers (except for Ollama API calls if using cloud-based Ollama).

- **No Data Retention**: The application does not store uploaded documents after the session ends. Vector databases exist only in memory during active sessions.

- **User Responsibility**: Users are responsible for ensuring they have the right to upload and process documents through the system.

### 4.2 AI Model Usage

- **Llama 3 by Meta**: The application uses Llama 3 as its language model. Users should review Meta's Llama 3 License terms for commercial usage restrictions.

- **Ollama**: Local deployment of LLMs. Users must comply with Ollama's terms of service.

### 4.3 Intellectual Property Considerations

1. **User Content**: Users retain full ownership of documents they upload to the system.

2. **Generated Content**: AI-generated answers, summaries, and flashcards should be verified for accuracy before use in academic or professional settings.

3. **Attribution**: When using this tool for academic purposes, students should verify the AI-generated content against source materials and follow their institution's academic integrity policies.

### 4.4 Academic Integrity

This tool is designed to assist learning, not replace it. Users should:
- Verify AI-generated answers against source documents
- Use summaries as study aids, not sole learning material
- Follow their institution's academic honesty policies
- Not submit AI-generated content as their own work without proper attribution

---

## 5. Deployment & Operational Considerations

### 5.1 System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8+
- **RAM**: Minimum 8GB recommended (for Ollama models)
- **Storage**: 4GB+ for Llama 3 and nomic-embed-text models
- **Ollama**: Must be installed and running locally

### 5.2 Security Best Practices

1. **Environment Variables**: Keep `.env` file secure and never commit to version control
2. **API Keys**: LangSmith API key should remain confidential
3. **File Validation**: Input validation implemented for file sizes and types
4. **Session Management**: Streamlit handles session state securely

---

## 6. References

### 6.1 Official Documentation

1. **Streamlit Documentation**
   - https://docs.streamlit.io/
   - Primary UI framework

2. **LangChain Documentation**
   - https://python.langchain.com/docs/
   - LLM orchestration and RAG pipeline

3. **Ollama Documentation**
   - https://github.com/ollama/ollama
   - Local LLM deployment

4. **FAISS Documentation**
   - https://faiss.ai/
   - Facebook AI Similarity Search

### 6.2 Academic & Technical References

5. **RAG (Retrieval-Augmented Generation)**
   - Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
   - https://arxiv.org/abs/2005.11401

6. **Vector Embeddings**
   - Reimers, N., & Gurevych, I. (2019). "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"
   - https://arxiv.org/abs/1908.10084

7. **Text Chunking Strategies**
   - "Chunking Strategies for LLM Applications"
   - https://python.langchain.com/docs/how_to/#chunking

### 6.3 Related Technologies

8. **Llama 3 Model**
   - Meta AI. (2024). "Introducing Llama 3"
   - https://ai.meta.com/llama/

9. **PDF Parsing Libraries**
   - PyPDF: https://pypdf.readthedocs.io/
   - python-docx: https://python-docx.readthedocs.io/

---

## 7. Troubleshooting Guide

### Common Issues

| Issue | Solution |
|-------|----------|
| Ollama not running | Start Ollama service: `ollama serve` |
| Model not found | Pull models: `ollama pull llama3` && `ollama pull nomic-embed-text` |
| Out of memory | Close other applications or use smaller chunk sizes |
| File too large | Reduce file size below 200MB |
| Slow responses | Reduce k value in similarity search |

---

## 8. Version History

| Version | Date | Changes |
|---------|------|---------|
| V1.0 | Initial | Basic Q&A functionality |
| V2.0 | Current | Mark-based answers, flashcards, summarization, anti-hallucination |

---

## 9. Contact & Support

For issues and contributions:
- Review existing code in `app.py` and `core_logic.py`
- Check LangChain and Ollama documentation for deep dives
- Ensure all dependencies in `requirements.txt` are installed

---

*This documentation was generated to provide comprehensive understanding of the Study Buddy application flow, implementation details, and legal considerations.*
