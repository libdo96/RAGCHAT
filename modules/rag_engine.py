import google.generativeai as genai

class RAGEngine:
    """
    Retrieval-Augmented Generation (RAG) engine using Google's Gemini models.
    """
    
    def __init__(self, model_name="gemini-1.5-flash"):
        """
        Initialize the RAG engine.
        
        Args:
            model_name (str): The name of the Gemini model to use
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
    def generate_response(self, query, context_chunks):
        """
        Generate a response to the query using the retrieved context chunks.
        
        Args:
            query (str): The user's question
            context_chunks (list): List of relevant document chunks
            
        Returns:
            str: The generated response
        """
        if not context_chunks:
            return "I don't have any relevant information to answer this question."
        
        # Format context with metadata
        formatted_context = []
        for i, chunk in enumerate(context_chunks):
            source_info = ""
            if "metadata" in chunk and chunk["metadata"]:
                meta = chunk["metadata"]
                if "source" in meta:
                    source_info += f"Source: {meta['source']}"
                if "page_num" in meta:
                    source_info += f", Page: {meta['page_num']}"
            
            formatted_chunk = f"[Document {i+1}] {source_info}\n{chunk['text']}\n"
            formatted_context.append(formatted_chunk)
        
        # Join formatted context
        context_text = "\n".join(formatted_context)
        
        # Create the prompt with context
        prompt = f"""
        You are an AI assistant that answers questions based on the provided document excerpts.
        
        Document excerpts:
        {context_text}
        
        User question: {query}
        
        Instructions:
        1. Answer the question based ONLY on the information provided in the document excerpts. and fulfill any demands of the user
        2. If the document excerpts don't contain enough information to answer the question, say "I don't have enough information to answer this question from provided document." and answer it by your knowledge
        3. If you use information from a specific document excerpt, mention which document you're referring to.
        4. Keep your answer concise and to the point.
        5. Do not make up information that is not in the document excerpts.
        
        Answer:
        """
        
        try:
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I encountered an error while trying to answer your question. Please try again."
    
    def update_model(self, model_name):
        """
        Update the model being used.
        
        Args:
            model_name (str): The name of the new model to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.model_name = model_name
            self.model = genai.GenerativeModel(model_name)
            return True
        except Exception as e:
            print(f"Error updating model: {e}")
            return False