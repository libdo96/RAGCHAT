import streamlit as st
import os
import tempfile
import traceback
import requests
from modules.pdf_processor import extract_text_from_pdf, split_text_into_chunks
from modules.vector_store import VectorStore
from modules.rag_engine import RAGEngine
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set your GOOGLE_API_KEY in a .env file")
    st.stop()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Error configuring Google Generative AI: {str(e)}")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="RAG-Powered PDF Chat",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
    }
    .chat-message.assistant {
        background-color: #475063;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .content {
        width: 80%;
    }
    .sidebar .sidebar-content {
        background-color: #262730;
    }
    .stButton>button {
        width: 100%;
    }
    .input-container {
        display: flex;
        align-items: center;
    }
    .input-box {
        flex-grow: 1;
        margin-right: 10px;
    }
    .send-button {
        flex-shrink: 0;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
    }
    .source-info {
        font-size: 0.8rem;
        color: #9e9e9e;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'vector_store' not in st.session_state:
    # Initialize vector store with appropriate embedding provider
    try:
        st.session_state.vector_store = VectorStore(embedding_provider="google")
    except Exception as e:
        st.session_state.vector_store = VectorStore(embedding_provider="sentence_transformer")

if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = RAGEngine(model_name="gemini-1.5-flash")
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'current_model' not in st.session_state:
    st.session_state.current_model = "gemini-1.5-flash"
    
if 'uploaded_pdfs' not in st.session_state:
    st.session_state.uploaded_pdfs = []
    
if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = "general"  # Options: "general", "pdf"
    
if 'available_models' not in st.session_state:
    st.session_state.available_models = []

if 'processing_status' not in st.session_state:
    st.session_state.processing_status = None

# Function to fetch available models
def get_available_models():
    try:
        # Try to fetch models from endpoint
        response = requests.get("http://localhost:8000/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            st.session_state.available_models = models
            return models
        else:
            # If endpoint returns error but we have cached models, use those
            if st.session_state.available_models:
                return st.session_state.available_models
            # Otherwise use default models silently
            return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    except:
        # If endpoint is unavailable but we have cached models, use those
        if st.session_state.available_models:
            return st.session_state.available_models
        # Otherwise use default models silently
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

# Function to process uploaded PDF
def process_pdf(uploaded_file):
    try:
        # Update processing status
        st.session_state.processing_status = f"Processing {uploaded_file.name}..."
        
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = tmp_file.name
        
        # Extract text from PDF with metadata
        text_data = extract_text_from_pdf(pdf_path)
        
        # Split text into chunks with metadata
        chunks, metadata_list = split_text_into_chunks(text_data)
        
        # Add chunks to vector store
        st.session_state.vector_store.add_documents(chunks, metadata_list)
        
        # Add to list of uploaded PDFs
        if uploaded_file.name not in st.session_state.uploaded_pdfs:
            st.session_state.uploaded_pdfs.append(uploaded_file.name)
        
        # Clean up the temporary file
        os.unlink(pdf_path)
        
        # Switch to PDF chat mode
        st.session_state.chat_mode = "pdf"
        
        # Update processing status
        st.session_state.processing_status = f"Successfully processed {uploaded_file.name} ({len(chunks)} chunks)"
        time.sleep(2)  # Show success message briefly
        st.session_state.processing_status = None
        
        return True
    except Exception as e:
        # Update processing status
        st.session_state.processing_status = f"Error processing {uploaded_file.name}: {str(e)}"
        time.sleep(3)  # Show error message briefly
        st.session_state.processing_status = None
        return False

# Function to update the model
def update_model(model_name):
    if model_name != st.session_state.current_model:
        st.session_state.current_model = model_name
        st.session_state.rag_engine.update_model(model_name)
        return True
    return False

# Function to generate response
def generate_response(user_question):
    try:
        with st.spinner("Thinking..."):
            if st.session_state.chat_mode == "general":
                # General chat mode - just use the model directly
                model = genai.GenerativeModel(st.session_state.current_model)
                response = model.generate_content(user_question)
                return {"text": response.text, "sources": None}
            elif st.session_state.chat_mode == "pdf":
                # RAG approach: retrieve relevant chunks and generate response
                relevant_chunks = st.session_state.vector_store.search(user_question, top_k=5)
                
                if not relevant_chunks:
                    return {
                        "text": "I don't have any relevant information to answer this question. Please upload a PDF with relevant content.",
                        "sources": None
                    }
                
                # Generate response using RAG
                response_text = st.session_state.rag_engine.generate_response(user_question, relevant_chunks)
                
                # Extract source information for display
                sources = []
                for chunk in relevant_chunks:
                    if "metadata" in chunk and chunk["metadata"]:
                        source = {
                            "text": chunk["text"][:100] + "...",  # Preview of the chunk
                            "score": chunk["score"],
                            "source": chunk["metadata"].get("source", "Unknown"),
                            "page": chunk["metadata"].get("page_num", "Unknown")
                        }
                        sources.append(source)
                
                return {"text": response_text, "sources": sources}
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        return {"text": error_msg, "sources": None}

# Sidebar
with st.sidebar:
    st.title("📚 Chat Settings")
    
    # Chat mode selection
    st.subheader("Chat Mode")
    chat_modes = {
        "general": "General Chat",
        "pdf": "PDF Document Chat"
    }
    selected_mode = st.radio(
        "Select chat mode:",
        options=list(chat_modes.keys()),
        format_func=lambda x: chat_modes[x],
        index=0 if st.session_state.chat_mode == "general" else 1
    )
    
    if selected_mode != st.session_state.chat_mode:
        st.session_state.chat_mode = selected_mode
        st.session_state.chat_history = []  # Clear chat history when switching modes
        st.experimental_rerun()
    
    # Model selection
    st.subheader("Model Selection")
    available_models = get_available_models()
    selected_model = st.selectbox(
        "Choose a model", 
        available_models, 
        index=available_models.index(st.session_state.current_model) if st.session_state.current_model in available_models else 0
    )
    
    if st.button("Apply Model"):
        if update_model(selected_model):
            st.success(f"Model updated to {selected_model}")
    
    # PDF Upload section (only show if in PDF mode)
    if st.session_state.chat_mode == "pdf":
        st.subheader("Upload Documents")
        uploaded_file = st.file_uploader("Upload a PDF document", type="pdf", key="sidebar_uploader")
        
        if uploaded_file:
            if st.button("Process PDF"):
                process_pdf(uploaded_file)
        
        # Display uploaded PDFs
        if st.session_state.uploaded_pdfs:
            st.subheader("Uploaded PDFs")
            for pdf in st.session_state.uploaded_pdfs:
                st.text(f"• {pdf}")
    
    # Clear options
    st.subheader("Clear Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()
    
    with col2:
        if st.session_state.chat_mode == "pdf" and st.button("Clear PDFs"):
            st.session_state.vector_store.clear()
            st.session_state.uploaded_pdfs = []
            st.success("All documents cleared!")
            st.experimental_rerun()
    
    # Show current model info
    st.info(f"Current model: {st.session_state.current_model}")
    
    # Show processing status if active
    if st.session_state.processing_status:
        st.warning(st.session_state.processing_status)

# Main content area
if st.session_state.chat_mode == "general":
    st.title("Chat with Gemini")
    st.markdown("Ask any question and get AI-powered answers.")
else:
    st.title("PDF Document Chat with Gemini")
    st.markdown("Ask questions about your uploaded PDF documents and get AI-powered answers.")

# Chat interface
st.subheader("Chat")

# Display chat messages
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user">
            <div class="content">
                <p><strong>You:</strong> {message['content']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sources_html = ""
        if "sources" in message and message["sources"]:
            sources_html = "<div class='source-info'><strong>Sources:</strong><ul>"
            for source in message["sources"]:
                sources_html += f"<li>{source['source']}"
                if source['page'] != "Unknown":
                    sources_html += f" (Page {source['page']})"
                sources_html += f" - Relevance: {source['score']:.2f}</li>"
            sources_html += "</ul></div>"
            
        st.markdown(f"""
        <div class="chat-message assistant">
            <div class="content">
                <p><strong>AI:</strong> {message['content']}</p>
                {sources_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Input area with send button
col1, col2 = st.columns([6, 1])

with col1:
    user_question = st.text_input(
        "Type your message:", 
        key="user_question",
        label_visibility="collapsed"
    )

# Check if there's a document uploaded before allowing questions in PDF mode
docs_available = True
if st.session_state.chat_mode == "pdf":
    docs_available = not st.session_state.vector_store.is_empty()
    
    if not docs_available:
        st.warning("Please upload a PDF document using the sidebar before asking questions in PDF mode.")

with col2:
    send_button = st.button("📤", disabled=not docs_available if st.session_state.chat_mode == "pdf" else False)

# Process the message when send button is clicked or Enter is pressed
if (send_button or user_question and user_question.endswith('\n')) and user_question:
    # Remove newline if present (from pressing Enter)
    if user_question.endswith('\n'):
        user_question = user_question[:-1]
        
    # Add user question to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    
    # Generate and add response
    response = generate_response(user_question)
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response["text"],
        "sources": response["sources"]
    })
    
    # Clear the input box by rerunning the app
    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Powered by Google Gemini and Streamlit")