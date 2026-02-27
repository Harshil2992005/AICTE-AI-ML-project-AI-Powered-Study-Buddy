# AI-Powered Study Buddy

An intelligent study assistant that helps you learn from your documents using AI.

## Features

- **Document Upload**: Support for PDF and DOCX files
- **Smart Q&A**: Ask questions and get answers with mark-based formatting (1-7 marks)
- **Flashcards**: Auto-generate flashcards from your study material
- **Summarization**: Get concise summaries of your notes

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Ollama (llama3)
- **Embeddings**: nomic-embed-text
- **Vector DB**: FAISS
- **Framework**: LangChain

## Installation

1. Clone the repository
2. Install Ollama and pull the models:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start Ollama in background
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. Upload a PDF or DOCX file
4. Ask questions, generate flashcards, or summarize!

## License

MIT
