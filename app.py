import streamlit as st
import json
import time
from io import BytesIO
import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
import chromadb
import re
import google.generativeai as genai

# Set page configuration
st.set_page_config(
    page_title="Lexi - Insurance Claims Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3.2rem;
        background: linear-gradient(135deg, #0d4e83 0%, #0d299b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #2D3748;
        margin-bottom: 1.2rem;
        font-weight: 700;
        letter-spacing: -0.3px;
    }
    
    .success-box {
        background: linear-gradient(135deg, #F0FFF4 0%, #E6FFFA 100%);
        padding: 1.4rem;
        color: rgb(1, 1, 12);
        border-radius: 12px;
        border-left: 5px solid #38A169;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .error-box {
        background: linear-gradient(135deg, #FFF5F5 0%, #FFFAF0 100%);
        padding: 1.4rem;
                color: rgb(1, 1, 12);
        border-radius: 12px;
        border-left: 5px solid #E53E3E;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .info-box {
        background: linear-gradient(135deg, #EBF8FF 0%, #E6FFFA 100%);
        padding: 1.4rem;
                color: rgb(1, 1, 12);
        border-radius: 12px;
        border-left: 5px solid #3182CE;
        margin-bottom: 1.4rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .json-box {
        background-color: #F7FAFC;
        padding: 1.4rem;
        border-radius: 12px;
                color: rgb(1, 1, 12);
        font-family: 'Fira Code', monospace;
        white-space: pre-wrap;
        margin-bottom: 1.4rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #052f6d 0%, #051935 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.9rem 1.8rem;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.2);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #0051CC 0%, #003D99 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 102, 255, 0.3);
    }
    
    .uploaded-file {
        background: linear-gradient(135deg, #FFFAF0 0%, #FFF5F5 100%);
        padding: 1.2rem;
                color: rgb(1, 1, 12);
        border-radius: 10px;
        border-left: 5px solid #ED8936;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .file-icon {
        font-size: 1.6rem;
        margin-right: 0.9rem;
    }
    
    .decision-approved {
        background: linear-gradient(135deg, #F0FFF4 0%, #C6F6D5 100%);
        padding: 1.2rem;
                color: rgb(1, 1, 12);
        border-radius: 10px;
        border-left: 5px solid #38A169;
        box-shadow: 0 4px 12px rgba(72, 187, 120, 0.15);
    }
    
    .decision-rejected {
        background: linear-gradient(135deg, #FFF5F5 0%, #FED7D7 100%);
        padding: 1.2rem;
        border-radius: 10px;
                color: rgb(1, 1, 12);
        border-left: 5px solid #E53E3E;
        box-shadow: 0 4px 12px rgba(245, 101, 101, 0.15);
    }
    
    .decision-insufficient {
        background: linear-gradient(135deg, #FFFAF0 0%, #FEEBC8 100%);
        padding: 1.2rem;
                color: rgb(1, 1, 12);
        border-radius: 10px;
        border-left: 5px solid #DD6B20;
        box-shadow: 0 4px 12px rgba(237, 137, 54, 0.15);
    }
    
    .clause-box {
        background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
        padding: 1.1rem;
        border-radius: 8px;
                color: rgb(1, 1, 12);
        margin-bottom: 0.9rem;
        border-left: 4px solid #4299E1;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .tab-content {
        padding: 1.8rem;
        border-radius: 14px;
                color: rgb(1, 1, 12);
        background: linear-gradient(135deg, #F7FAFC 0%, #FFFFFF 100%);
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
                color: rgb(1, 1, 12);
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    
    .step-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
       background: linear-gradient(135deg, #0f0120 0%, #020c36 100%);
        color: white;
        border-radius: 50%;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .hero-section {
       background: linear-gradient(135deg, #0f0120 0%, #020c36 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2.5rem;
        text-align: center;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.15);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'embedding_model' not in st.session_state:
    st.session_state.embedding_model = None
if 'chroma_collection' not in st.session_state:
    st.session_state.chroma_collection = None
if 'chroma_client' not in st.session_state:
    st.session_state.chroma_client = None

# Your Gemini API key (hidden from users)
GEMINI_API_KEY = "AIzaSyAETxVxx9E-bicGEjNEsXFaGSnMtleRd00"  # Replace with your actual API key

# Initialize ChromaDB and model
def initialize_components():
    if st.session_state.embedding_model is None:
        with st.spinner("🧠 Loading document analysis engine..."):
            try:
                st.session_state.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                st.error(f"❌ Failed to initialize analysis engine: {str(e)}")
                return False
    
    if st.session_state.chroma_client is None:
        try:
            st.session_state.chroma_client = chromadb.Client()
            st.session_state.chroma_collection = st.session_state.chroma_client.get_or_create_collection("policy_docs")
        except Exception as e:
            st.error(f"❌ Failed to initialize document database: {str(e)}")
            return False
    
    return True

# Text extraction functions
def extract_text_from_pdf(content):
    text = ""
    try:
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
    return text

def extract_text_from_docx(content):
    text = ""
    try:
        doc = Document(BytesIO(content))
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n\n"
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
    return text

def extract_text(filename, content):
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(content)
    elif filename.lower().endswith(".docx"):
        return extract_text_from_docx(content)
    else:
        try:
            return content.decode("utf-8")
        except:
            try:
                return content.decode("latin-1")
            except:
                return str(content)

# Text chunking function
def chunk_text(text, chunk_size=500):
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para
            
            if len(current_chunk) > chunk_size:
                words = current_chunk.split()
                current_chunk = ""
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= chunk_size:
                        if current_chunk:
                            current_chunk += " " + word
                        else:
                            current_chunk = word
                    else:
                        chunks.append(current_chunk)
                        current_chunk = word
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

# Embedding and storage functions
def embed_and_store(chunks, doc_name):
    if not initialize_components():
        return False
    
    try:
        embeddings = st.session_state.embedding_model.encode(chunks)
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            st.session_state.chroma_collection.add(
                documents=[chunk],
                embeddings=[embedding.tolist()],
                ids=[f"{doc_name}_{i}"]
            )
        return True
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return False

# Query function
def query_top_chunks(query, k=3):
    if not initialize_components():
        return None
    
    try:
        q_embed = st.session_state.embedding_model.encode([query])[0].tolist()
        results = st.session_state.chroma_collection.query(
            query_embeddings=[q_embed], 
            n_results=k
        )
        return results['documents'][0] if results['documents'] else None
    except Exception as e:
        st.error(f"Error searching documents: {str(e)}")
        return None

# LLM integration with Gemini Flash 1.5
def generate_answer(question, chunks):
    if not chunks:
        return {"error": "No relevant content found in uploaded documents."}
    
    try:
        # Configure Gemini with your API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create the model - using Gemini Flash 1.5
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create the prompt
        prompt = f"""
As an expert insurance claims evaluator, analyze the policy context and provide a structured JSON response.

Policy Context:
{chr(10).join(chunks)}

Claim Question: {question}

Provide your analysis in this exact JSON format:
{{
  "decision": "Approved" or "Rejected" or "Insufficient Information",
  "amount": "INR value or N/A",
  "justification": "Explanation with policy references",
  "referenced_clauses": ["clause excerpt 1", "clause excerpt 2", ...]
}}

Return ONLY valid JSON, no additional text.
"""
        
        # Generate the response
        response = model.generate_content(prompt)
        
        return {
            "context_used": chunks, 
            "answer": response.text, 
            "model": "Gemini Flash 1.5"
        }
    except Exception as e:
        return {"error": f"Analysis error: {str(e)}"}

# Clear all data function
def clear_all_data():
    try:
        if st.session_state.chroma_client:
            st.session_state.chroma_client = chromadb.Client()
            st.session_state.chroma_collection = st.session_state.chroma_client.get_or_create_collection("policy_docs")
    except:
        st.session_state.chroma_client = None
        st.session_state.chroma_collection = None
    
    st.session_state.uploaded_files = []
    st.session_state.processing_complete = False
    st.success("All data cleared successfully!")

# App header
st.markdown('<h1 class="main-header">📋 Lexi - Insurance Claims Assistant</h1>', unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero-section">
    <h2 style="color: white; font-size: 2.2rem; margin-bottom: 1rem;">Intelligent Claims Processing Made Simple</h2>
    <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin-bottom: 2rem;">
        Upload policy documents, ask questions, and get instant claim evaluations with referenced policy clauses.
    </p>
    <div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 2rem;">
        <div class="stat-box">
            <div style="font-size: 2rem; font-weight: 700;">⏱️</div>
            <div>Faster Processing</div>
        </div>
        <div class="stat-box">
            <div style="font-size: 2rem; font-weight: 700;">📑</div>
            <div>Policy Analysis</div>
        </div>
        <div class="stat-box">
            <div style="font-size: 2rem; font-weight: 700;">✅</div>
            <div>Accurate Decisions</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Features section
st.markdown("### 🚀 How It Works")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="step-number">1</div>
        <h3>Upload Documents</h3>
        <p>Upload your insurance policy documents in PDF, DOCX, or text format.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="step-number">2</div>
        <h3>Ask Questions</h3>
        <p>Query about specific claim scenarios or policy coverage details.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="step-number">3</div>
        <h3>Get Answers</h3>
        <p>Receive detailed evaluations with referenced policy clauses.</p>
    </div>
    """, unsafe_allow_html=True)

# Main app tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "❓ Ask Questions", "📊 Document Library"])

# Tab 1: Document Upload
with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Upload Policy Documents</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <strong>Supported formats:</strong> PDF, DOCX, TXT files<br>
        <strong>Maximum size:</strong> 200MB per file<br>
        <strong>Privacy:</strong> Your documents are processed securely and never stored on our servers
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drag and drop files or click to browse", 
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Select insurance policy documents to analyze"
    )
    
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in [f.name for f in st.session_state.uploaded_files]:
                st.session_state.uploaded_files.append(file)
        
        st.markdown('<div class="success-box">✅ Documents ready for processing</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Process Documents", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processed_count = 0
            errors = []
            
            for i, file in enumerate(st.session_state.uploaded_files):
                status_text.text(f"📄 Analyzing {file.name}...")
                
                try:
                    content = file.getvalue()
                    text = extract_text(file.name, content)
                    if not text.strip():
                        errors.append(f"{file.name}: No text could be extracted")
                        continue
                        
                    chunks = chunk_text(text)
                    
                    if embed_and_store(chunks, file.name):
                        processed_count += 1
                    else:
                        errors.append(f"{file.name}: Processing failed")
                
                except Exception as e:
                    errors.append(f"{file.name}: {str(e)}")
                
                progress_bar.progress((i + 1) / len(st.session_state.uploaded_files))
                time.sleep(0.1)
            
            if errors:
                error_message = "Some files had issues:\n" + "\n".join(errors)
                st.markdown(f'<div class="error-box">❌ {error_message}</div>', unsafe_allow_html=True)
            else:
                st.session_state.processing_complete = True
                st.markdown(f'<div class="success-box">✅ Successfully processed {processed_count} documents!</div>', unsafe_allow_html=True)
            
            progress_bar.empty()
            status_text.empty()
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Query Interface
with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Claim Evaluation Query</h2>', unsafe_allow_html=True)
    
    if not st.session_state.uploaded_files:
        st.markdown("""
        <div class="info-box">
            <strong>No documents uploaded yet.</strong><br>
            Please upload policy documents first to enable claim evaluation.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
            <strong>Tip:</strong> Ask specific questions about claim eligibility, coverage limits, 
            exclusions, or required documentation for faster, more accurate results.
        </div>
        """, unsafe_allow_html=True)
        
        question = st.text_area(
            "Enter your claim question:",
            placeholder="e.g., Is screen damage covered under the device protection policy? What's the maximum claim amount for accidental damage?",
            height=120
        )
        
        if st.button("🔍 Analyze Claim", use_container_width=True):
            if not question.strip():
                st.error("Please enter a question about the claim.")
            else:
                with st.spinner("🔍 Analyzing policy documents..."):
                    try:
                        top_chunks = query_top_chunks(question)
                        if not top_chunks:
                            st.error("No relevant policy information found for this query.")
                        else:
                            result = generate_answer(question, top_chunks)
                            
                            if "error" in result:
                                st.markdown(f'<div class="error-box">❌ {result["error"]}</div>', unsafe_allow_html=True)
                            else:
                                try:
                                    json_str = result["answer"].strip()
                                    if json_str.startswith("```json"):
                                        json_str = json_str[7:]
                                    if json_str.endswith("```"):
                                        json_str = json_str[:-3]
                                    json_str = re.sub(r'^```|```$', '', json_str, flags=re.MULTILINE).strip()
                                    
                                    answer_data = json.loads(json_str)
                                    
                                    col1, col2 = st.columns([1, 2])
                                    
                                    with col1:
                                        st.subheader("📋 Claim Decision")
                                        decision = answer_data.get("decision", "").lower()
                                        if "approved" in decision:
                                            st.markdown('<div class="decision-approved">✅ Claim Approved</div>', unsafe_allow_html=True)
                                        elif "rejected" in decision:
                                            st.markdown('<div class="decision-rejected">❌ Claim Rejected</div>', unsafe_allow_html=True)
                                        else:
                                            st.markdown('<div class="decision-insufficient">⚠️ More Information Needed</div>', unsafe_allow_html=True)
                                        
                                        st.subheader("💵 Covered Amount")
                                        st.info(answer_data.get("amount", "To be determined"))
                                    
                                    with col2:
                                        st.subheader("📝 Evaluation Details")
                                        st.write(answer_data.get("justification", "No details provided."))
                                    
                                    if answer_data.get("referenced_clauses"):
                                        st.subheader("📑 Policy References")
                                        for i, clause in enumerate(answer_data["referenced_clauses"], 1):
                                            st.markdown(f'<div class="clause-box">{i}. {clause}</div>', unsafe_allow_html=True)
                                    
                                    with st.expander("🔍 View Analysis Context"):
                                        if "context_used" in result:
                                            for i, chunk in enumerate(result["context_used"]):
                                                st.write(f"**Policy Excerpt {i+1}:**")
                                                st.write(chunk)
                                                st.divider()
                                    
                                    with st.expander("📄 View Technical Details"):
                                        st.json(answer_data)
                                
                                except json.JSONDecodeError as e:
                                    st.markdown("### 📄 Analysis Result")
                                    st.write(result["answer"])
                    
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Processed Files
with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Document Library</h2>', unsafe_allow_html=True)
    
    if not st.session_state.uploaded_files:
        st.info("Your document library is empty. Upload policy documents to get started.")
    else:
        st.markdown("""
        <div class="info-box">
            <strong>📚 Library Contents:</strong> These documents are currently available for claim analysis and queries.
        </div>
        """, unsafe_allow_html=True)
        
        for file in st.session_state.uploaded_files:
            file_icon = "📄"
            if file.name.lower().endswith(".pdf"):
                file_icon = "📕"
            elif file.name.lower().endswith(".docx"):
                file_icon = "📘"
                
            st.markdown(f'''
            <div class="uploaded-file">
                <div>
                    <span class="file-icon">{file_icon}</span>
                    <strong>{file.name}</strong> ({file.size} bytes)
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Library", use_container_width=True):
            clear_all_data()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #718096; padding: 2rem; font-size: 0.9rem;'>"
    "Lexi - Insurance Claims Assistant • Secure Document Analysis • © 2023"
    "</div>",
    unsafe_allow_html=True
)