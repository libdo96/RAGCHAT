import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import os
import pickle
import uuid

class VectorStore:
    """
    A vector store for document embeddings with support for multiple embedding providers.
    """
    
    def __init__(self, embedding_provider="sentence_transformer", model_name="all-MiniLM-L6-v2", storage_dir="./vector_db"):
        """
        Initialize the vector store.
        
        Args:
            embedding_provider (str): The embedding provider to use ('google' or 'sentence_transformer')
            model_name (str): The name of the embedding model to use
            storage_dir (str): Directory to store the vector database
        """
        self.embedding_provider = embedding_provider
        self.model_name = model_name
        self.storage_dir = storage_dir
        self.documents = []
        self.document_metadata = []
        self.embeddings = None
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize the embedding model
        if embedding_provider == "google":
            try:
                self.embedding_model = genai.Embedding()
                print("Using Google's embedding model")
            except Exception as e:
                print(f"Failed to initialize Google embedding model: {e}")
                self.embedding_provider = "sentence_transformer"
                self.embedding_model = SentenceTransformer(model_name)
                print(f"Falling back to sentence-transformers: {model_name}")
        else:
            try:
                self.embedding_model = SentenceTransformer(model_name)
                print(f"Using sentence-transformers: {model_name}")
            except Exception as e:
                print(f"Failed to initialize sentence-transformer model: {e}")
                try:
                    self.model_name = "paraphrase-MiniLM-L3-v2"
                    self.embedding_model = SentenceTransformer(self.model_name)
                    print(f"Falling back to simpler model: {self.model_name}")
                except:
                    raise ValueError("Could not initialize any embedding model")
        
        # Try to load existing database
        self.load_database()
        
    def embed_text(self, text):
        """
        Generate embeddings for a piece of text.
        
        Args:
            text (str): The text to embed
            
        Returns:
            numpy.ndarray: The embedding vector
        """
        if self.embedding_provider == "google":
            try:
                result = self.embedding_model.embed_content(
                    content=text,
                    task_type="retrieval_document"
                )
                return np.array(result["embedding"])
            except Exception as e:
                print(f"Error with Google embedding: {e}")
                # If Google embedding fails, try to fall back to sentence-transformers
                if not isinstance(self.embedding_model, SentenceTransformer):
                    self.embedding_provider = "sentence_transformer"
                    self.embedding_model = SentenceTransformer(self.model_name)
                return self.embedding_model.encode(text)
        else:
            return self.embedding_model.encode(text)
    
    def add_documents(self, documents, metadata=None):
        """
        Add documents to the vector store.
        
        Args:
            documents (list): List of document texts
            metadata (list, optional): List of metadata dictionaries for each document
        """
        if not documents:
            return
            
        # Process metadata
        if metadata is None:
            metadata = [{"id": str(uuid.uuid4()), "index": i} for i in range(len(documents))]
        elif len(metadata) != len(documents):
            raise ValueError("Length of metadata must match length of documents")
        
        # Add documents and metadata
        self.documents.extend(documents)
        self.document_metadata.extend(metadata)
        
        # Generate embeddings
        new_embeddings = []
        for doc in documents:
            try:
                embedding = self.embed_text(doc)
                new_embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding: {e}")
                # Use a zero vector as fallback
                new_embeddings.append(np.zeros(768))  # typical embedding dimension
        
        # Convert to numpy array
        new_embeddings_array = np.array(new_embeddings)
        
        # Add to existing embeddings
        if self.embeddings is None:
            self.embeddings = new_embeddings_array
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings_array])
        
        # Save the updated database
        self.save_database()
    
    def search(self, query, top_k=5):
        """
        Search for documents similar to the query.
        
        Args:
            query (str): The search query
            top_k (int): Number of results to return
            
        Returns:
            list: List of most similar documents with metadata
        """
        if not self.documents or self.embeddings is None or len(self.embeddings) == 0:
            return []
            
        try:
            # Generate embedding for the query
            if self.embedding_provider == "google":
                query_result = self.embedding_model.embed_content(
                    content=query,
                    task_type="retrieval_query"
                )
                query_embedding = np.array([query_result["embedding"]])
            else:
                query_embedding = np.array([self.embedding_model.encode(query)])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get indices of top_k most similar documents
            k = min(top_k, len(self.documents))
            top_indices = np.argsort(similarities)[-k:][::-1]
            
            # Return the documents and their similarity scores
            results = []
            for idx in top_indices:
                results.append({
                    "text": self.documents[idx],
                    "score": float(similarities[idx]),
                    "metadata": self.document_metadata[idx]
                })
                
            return results
        except Exception as e:
            print(f"Error in search: {e}")
            return []
    
    def save_database(self):
        """
        Save the vector database to disk.
        """
        try:
            database = {
                "documents": self.documents,
                "document_metadata": self.document_metadata,
                "embeddings": self.embeddings,
                "embedding_provider": self.embedding_provider,
                "model_name": self.model_name
            }
            with open(os.path.join(self.storage_dir, "vector_db.pkl"), "wb") as f:
                pickle.dump(database, f)
            print(f"Database saved with {len(self.documents)} documents")
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def load_database(self):
        """
        Load the vector database from disk.
        """
        try:
            db_path = os.path.join(self.storage_dir, "vector_db.pkl")
            if os.path.exists(db_path):
                with open(db_path, "rb") as f:
                    database = pickle.load(f)
                self.documents = database.get("documents", [])
                self.document_metadata = database.get("document_metadata", [])
                self.embeddings = database.get("embeddings", None)
                print(f"Database loaded with {len(self.documents)} documents")
                return True
        except Exception as e:
            print(f"Error loading database: {e}")
        return False
    
    def clear(self):
        """
        Clear the vector store.
        """
        self.documents = []
        self.document_metadata = []
        self.embeddings = None
        
        # Remove the database file
        try:
            db_path = os.path.join(self.storage_dir, "vector_db.pkl")
            if os.path.exists(db_path):
                os.remove(db_path)
        except Exception as e:
            print(f"Error removing database file: {e}")
    
    def is_empty(self):
        """
        Check if the vector store is empty.
        
        Returns:
            bool: True if empty, False otherwise
        """
        return len(self.documents) == 0 or self.embeddings is None
