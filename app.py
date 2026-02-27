import streamlit as st
import tempfile
import os
from core_logic import process_document, get_qa_chain, generate_flashcards, summarize_notes

st.set_page_config(
    page_title="Study Buddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .app-header {
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .stCard {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 10px 10px 0px 0px;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    /* Flashcard styling */
    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    /* Answer card styling */

    .answer-card {
    background: #1e293b;        /* Dark slate */
    padding: 18px;
    border-radius: 12px;
    border-left: 5px solid #667eea;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    color: #f1f5f9;             /* Soft white text */
}
    
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Success message */
    .success-msg {
        padding: 15px;
        border-radius: 10px;
        background: #d4edda;
        color: #155724;
    }
    
    /* Warning message */
    .warning-msg {
        padding: 15px;
        border-radius: 10px;
        background: #fff3cd;
        color: #856404;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "summary" not in st.session_state:
    st.session_state.summary = None
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; color: white; padding: 10px;">
        <h2>📄 Document Upload</h2>
    </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader(
        "Upload your study materials",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX (Max 200MB)"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if file and st.button("Index Document", use_container_width=True):
            with st.spinner("📚 Processing your document..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
                        tmp.write(file.getbuffer())
                        st.session_state.vector_db = process_document(tmp.name)
                        st.session_state.flashcards = []
                        st.session_state.summary = None
                        st.session_state.last_answer = None
                    st.success("✅ Document indexed successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("Clear All", use_container_width=True):
            st.session_state.vector_db = None
            st.session_state.flashcards = []
            st.session_state.summary = None
            st.session_state.last_answer = None
            st.rerun()
    
    # Document info
    if st.session_state.vector_db:
        st.markdown("---")
        st.markdown("""
        <div style="color: white; text-align: center;">
            <p>✅ <b>Document Ready</b></p>
            <p>You can now ask questions, generate flashcards, or summarize!</p>
        </div>
        """, unsafe_allow_html=True)

# Main content
st.markdown("""
<div class="app-header">
    <h1>📚 Study Buddy</h1>
    <p>Your AI-powered study assistant</p>
</div>
""", unsafe_allow_html=True)

# Check if document is uploaded or not
if not st.session_state.vector_db:
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2>👋 Welcome to Study Buddy!</h2>
        <p>Please upload a document in the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "🎯 Flashcards", "📝 Summary"])
    
    with tab1:
        st.markdown("### Ask Questions")
        st.markdown("Ask questions about your study material. You can specify marks like '1 mark', '2 marks', '7 marks' etc.")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input(
                "Your question",
                placeholder="e.g., What is CSMA/CA? 1 mark",
                label_visibility="collapsed"
            )
        with col2:
            search_btn = st.button("🔍 Get Answer", use_container_width=True)
        
        if search_btn and query:
            if st.session_state.vector_db:
                with st.spinner("🤔 Finding the best answer..."):
                    try:
                        response = get_qa_chain(st.session_state.vector_db)(query)
                        st.session_state.last_answer = response
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Display answer
        if st.session_state.last_answer:
            st.markdown("---")
            st.markdown("### Answer")
            
            # Check for out of topic response
            if "out-of-topic" in st.session_state.last_answer.lower() or "not present" in st.session_state.last_answer.lower():
                st.warning("⚠️ " + st.session_state.last_answer)
            else:
                st.markdown(f"""
                <div class="answer-card">
                    {st.session_state.last_answer}
                </div>
                """, unsafe_allow_html=True)
            
            # Copy button
            if st.button("📋 Copy Answer"):
                st.code(st.session_state.last_answer)
                st.toast("Answer copied to clipboard!")
    
    with tab2:
        st.markdown("### Flashcards")
        st.markdown("Generate flashcards to test your knowledge")
        
        if st.button("🎲 Generate Flashcards", use_container_width=True):
            with st.spinner("🎯 Creating flashcards..."):
                try:
                    st.session_state.flashcards = generate_flashcards(st.session_state.vector_db)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Display flashcards
        if st.session_state.flashcards:
            st.markdown("---")
            
            # Add session state for card visibility
            if "show_answers" not in st.session_state:
                st.session_state.show_answers = {}
            
            for i, card in enumerate(st.session_state.flashcards):
                with st.expander(f"📚 Flashcard {i+1}", expanded=False):
                    st.markdown(f"**Question:** {card['question']}")
                    st.markdown("---")
                    
                    # Toggle answer visibility
                    if f"card_{i}" not in st.session_state.show_answers:
                        st.session_state.show_answers[f"card_{i}"] = False
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"👁️ Show Answer", key=f"show_{i}"):
                            st.session_state.show_answers[f"card_{i}"] = True
                            st.rerun()
                    
                    if st.session_state.show_answers.get(f"card_{i}", False):
                        st.markdown(f"""
                        <div style="background:e8f5e9; padding: 15px; border-radius: 10px; margin-top: 10px;">
                            <b>Answer:</b> {card['answer']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🔄 Hide Answer", key=f"hide_{i}"):
                            st.session_state.show_answers[f"card_{i}"] = False
                            st.rerun()
        else:
            st.info("👈 Click 'Generate Flashcards' to create practice cards from your document")
    
    with tab3:
        st.markdown("### Summarize Notes")
        st.markdown("Get a concise summary of your study material")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            length = st.slider("Summary length (words)", 100, 1000, 300)
        with col2:
            summarize_btn = st.button("📝 Summarize", use_container_width=True)
        
        if summarize_btn:
            with st.spinner("📝 Generating summary..."):
                try:
                    st.session_state.summary = summarize_notes(st.session_state.vector_db, length)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Display summary of content 
        if st.session_state.summary:
            st.markdown("---")
            st.markdown("### Summary")
            
            # Checks for warning
            if st.session_state.summary.startswith("⚠️"):
                st.warning(st.session_state.summary.split("\n\n")[0])
                content = "\n\n".join(st.session_state.summary.split("\n\n")[1:])
            else:
                content = st.session_state.summary
            
            st.markdown(f"""
            <div style="background:#1e293b; padding: 20px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); line-height: 1.8;">
                {content}
            </div>
            """, unsafe_allow_html=True)
            
            # Word count in no
            word_count = len(content.split())
            st.caption(f"📊 Summary contains approximately {word_count} words")
        else:
            st.info("👈 Adjust the slider and click 'Summarize' to get your notes summary")

# Footer last element 
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Study Buddy v2.0 | Powered by LangChain & Ollama</p>
</div>
""", unsafe_allow_html=True)
