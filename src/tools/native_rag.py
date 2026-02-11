import numpy as np
from pypdf import PdfReader
from mistralai import Mistral
from sklearn.metrics.pairwise import cosine_similarity
from config import MISTRAL_API_KEY

class NativeRAG:
    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        self.vector_db = [] # In-memory storage: [{"text": str, "vector": array}]
        self.chunk_size = 500 # Characters per chunk

    def ingest_pdf(self, file_path):
        """
        1. Parse PDF
        2. Chunk Text
        3. Vectorize (Embed)
        """
        print(f"[RAG] 📂 Ingesting {file_path}...")
        
        # 1. Read PDF
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
            
        # 2. Manual Chunking (Sliding Window)
        chunks = [full_text[i:i+self.chunk_size] for i in range(0, len(full_text), self.chunk_size)]
        
        # 3. Vectorize in Batch
        # Mistral embeddings API
        embeddings_batch = self.client.embeddings.create(
            model="mistral-embed",
            inputs=chunks
        )
        
        # Store in "DB"
        self.vector_db = [] # Reset for demo (or append for multi-doc)
        for i, chunk in enumerate(chunks):
            self.vector_db.append({
                "text": chunk,
                "vector": embeddings_batch.data[i].embedding
            })
        
        print(f"[RAG] ✅ Indexed {len(chunks)} chunks.")

    def retrieve(self, query, top_k=3):
        """
        1. Embed Query
        2. Math (Cosine Similarity)
        3. Return Top K
        """
        if not self.vector_db:
            return ""

        # Embed User Query
        query_emb = self.client.embeddings.create(
            model="mistral-embed",
            inputs=[query]
        ).data[0].embedding

        # Convert list to numpy array for speed
        db_vectors = np.array([item["vector"] for item in self.vector_db])
        query_vector = np.array([query_emb])

        # Calculate Similarity (Dot Product / Norm)
        similarities = cosine_similarity(query_vector, db_vectors)[0]
        
        # Get Top K indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # Construct Context String
        context = "\n---\n".join([self.vector_db[i]["text"] for i in top_indices])
        return context