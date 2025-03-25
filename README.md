# RAG-Powered PDF Chat with Gemini 1.5 Flash

This application allows you to upload PDF documents and ask questions about their content. It uses Retrieval-Augmented Generation (RAG) with Google's Gemini 1.5 Flash model to provide accurate answers based on the document content.

## Features

- PDF document upload and processing
- Text extraction and chunking
- Vector embedding and similarity search
- RAG-powered question answering using Gemini 1.5 Flash
- Simple chat interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Getting a Google API Key

1. Go to the [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

## Running the Application

Run the Streamlit app:

```
streamlit run app.py
```

The application will be available at http://localhost:8501

## Usage

1. Upload a PDF document using the file uploader
2. Wait for the document to be processed
3. Type your question in the text input field
4. View the AI's response based on the document content

## How It Works

1. **PDF Processing**: The application extracts text from the uploaded PDF and splits it into manageable chunks.
2. **Vector Embedding**: Each text chunk is converted into a vector embedding using a sentence transformer model.
3. **Retrieval**: When you ask a question, the application finds the most relevant text chunks using cosine similarity.
4. **Generation**: The relevant chunks are sent to the Gemini 1.5 Flash model along with your question to generate a contextually accurate response.

## Limitations

- The application works best with text-based PDFs. Scanned documents may require OCR processing (not included).
- Very large PDFs may take longer to process.
- The quality of answers depends on the content of the uploaded document.