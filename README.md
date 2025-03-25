# RAG-Powered PDF Chat with Gemini

This application allows you to upload PDF documents and ask questions about their content using Retrieval-Augmented Generation (RAG) with Google's Gemini models. It also supports general chat without PDF context.

![RAG PDF Chat Demo](https://i.imgur.com/YourImageHere.png)

## Features

- **Dual Chat Modes**: 
  - PDF Document Chat with RAG
  - General Chat with Gemini
- **Advanced PDF Processing**:
  - Text extraction with metadata
  - Semantic chunking
  - Vector embeddings for similarity search
- **Proper RAG Implementation**:
  - Semantic search to find relevant document chunks
  - Source attribution in responses
  - Relevance scoring
- **Flexible Model Selection**:
  - Dynamic model fetching from API
  - Support for multiple Gemini models
- **Persistent Vector Database**:
  - Saves processed documents between sessions
  - Efficient retrieval

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/libdo96/RAGCHAT.git
cd RAGCHAT
```

### Setup the Project

Run the setup script to create a virtual environment and install dependencies:

```bash
python setup.py
```

### Configure API Key

Rename the .env.example to .env and add your Google API key:

macOS/Linux:`mv .env.example .env`
Windows (Powershell) : `Rename-Item .env.example -NewName .env`
Windows (Command prompt): `ren .env.example .env`

Then edit the `.env` file and replace `your_api_key_here` with your actual Google API key.

### Run the Application

```bash
python run.py
```

The application will be available at http://localhost:8501

## Getting a Google API Key

1. Go to the [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Rename the `.env.example` to `.env`
5. Copy the key and add it to your `.env` file

## Environment Variables

The application uses the following environment variables that you can configure in your `.env` file:


## Manual Setup

If you prefer to set up manually:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### General Chat Mode

1. Select "General Chat" in the sidebar
2. Type your question in the input field
3. Press Enter or click the send button
4. View the AI's response

### PDF Chat Mode

1. Select "PDF Document Chat" in the sidebar
2. Upload a PDF document using the file uploader
3. Click "Process PDF" and wait for processing to complete
4. Type your question about the document
5. View the AI's response with source information

## How It Works

### PDF Processing Pipeline

1. **Text Extraction**: Extract text from PDF with page information
2. **Chunking**: Split text into semantic chunks with metadata
3. **Embedding**: Convert chunks to vector embeddings
4. **Storage**: Save in a vector database for efficient retrieval

### RAG Implementation

1. **Query Understanding**: Process the user's question
2. **Semantic Search**: Find the most relevant chunks using vector similarity
3. **Context Assembly**: Format retrieved chunks with source information
4. **Response Generation**: Use Gemini to generate an answer based on the retrieved context
5. **Source Attribution**: Display source information with the response

## Advanced Features

- **Persistent Storage**: Processed documents are saved between sessions
- **Multiple Document Support**: Upload and query across multiple PDFs
- **Source Attribution**: See which documents and pages were used for answers
- **Relevance Scoring**: View how relevant each source was to your question
- **Fallback Mechanisms**: Graceful handling of API limitations and errors

## Limitations

- The application works best with text-based PDFs. Scanned documents may require OCR processing (not included).
- Very large PDFs may take longer to process.
- The quality of answers depends on the content of the uploaded document and the relevance of the retrieved chunks.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
