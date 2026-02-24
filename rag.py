import os
import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


class RAGEngine:
    def __init__(self, index_path="data/faiss.index"):
        """
        Initialize RAG engine
        """
        load_dotenv()  # Load .env file

        self.client = OpenAI()  # Reads OPENAI_API_KEY automatically
        self.index_path = index_path
        self.chunks = []
        self.index = None

    # ==============================
    # 1️⃣ Load & Chunk Documents
    # ==============================
    def load_documents(self, file_path, chunk_size=500):
        """
        Load text file and split into chunks
        """
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        self.chunks = self._chunk_text(text, chunk_size)

        embeddings = self._create_embeddings(self.chunks)

        self._build_faiss_index(embeddings)

    def _chunk_text(self, text, chunk_size):
        """
        Simple text chunking
        """
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks

    # ==============================
    # 2️⃣ Create Embeddings
    # ==============================
    def _create_embeddings(self, texts):
        """
        Generate embeddings using OpenAI
        """
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        embeddings = [item.embedding for item in response.data]

        return np.array(embeddings, dtype="float32")

    def _embed_query(self, query):
        """
        Embed a single query
        """
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )

        embedding = response.data[0].embedding

        return np.array([embedding], dtype="float32")

    # ==============================
    # 3️⃣ FAISS Index
    # ==============================
    def _build_faiss_index(self, embeddings):
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

    def _load_index(self):
        if self.index is None:
            self.index = faiss.read_index(self.index_path)

    def _retrieve(self, query, k=5):
        self._load_index()

        query_embedding = self._embed_query(query)

        D, I = self.index.search(query_embedding, min(k, self.index.ntotal))

        return [self.chunks[i] for i in I[0]]

    # ==============================
    # 4️⃣ Generate Final Answer
    # ==============================
    def generate_answer(self, question, k=5):
        retrieved_chunks = self._retrieve(question, k=k)

        context = "\n\n".join(retrieved_chunks)

        prompt = f"""
        Answer ONLY from the given context.
        If the answer is not in the context, say:
        "Answer not found in document."

        Context:
        {context}

        Question:
        {question}

        Answer:
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()