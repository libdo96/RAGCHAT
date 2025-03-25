import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import uuid

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary with extracted text and metadata
    """
    text = ""
    metadata = {
        "source": os.path.basename(pdf_path),
        "path": pdf_path,
        "id": str(uuid.uuid4())
    }
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata["total_pages"] = len(pdf_reader.pages)
            
            # Extract text page by page with page numbers
            pages_text = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                pages_text.append({
                    "page_num": page_num + 1,
                    "text": page_text
                })
                text += page_text + "\n\n"
            
            metadata["pages"] = pages_text
            
            # Try to extract PDF metadata
            if pdf_reader.metadata:
                for key, value in pdf_reader.metadata.items():
                    if key.startswith('/'):
                        clean_key = key[1:].lower()
                        metadata[clean_key] = value
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    
    return {"text": text, "metadata": metadata}

def split_text_into_chunks(text_data, chunk_size=1000, chunk_overlap=200):
    """
    Split text into overlapping chunks with metadata.
    
    Args:
        text_data (dict): Dictionary with text and metadata
        chunk_size (int): The size of each chunk
        chunk_overlap (int): The overlap between chunks
        
    Returns:
        tuple: (chunks, metadata_list)
    """
    text = text_data["text"]
    doc_metadata = text_data["metadata"]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    # Create metadata for each chunk
    metadata_list = []
    for i, chunk in enumerate(chunks):
        chunk_metadata = {
            "chunk_id": str(uuid.uuid4()),
            "chunk_index": i,
            "document_id": doc_metadata.get("id"),
            "source": doc_metadata.get("source"),
            "total_chunks": len(chunks)
        }
        
        # Try to determine which page this chunk is from
        if "pages" in doc_metadata:
            # Simple heuristic: check if chunk text appears in page text
            for page_info in doc_metadata["pages"]:
                if chunk in page_info["text"]:
                    chunk_metadata["page_num"] = page_info["page_num"]
                    break
        
        metadata_list.append(chunk_metadata)
    
    return chunks, metadata_list
