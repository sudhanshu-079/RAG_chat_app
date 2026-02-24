from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
import os

load_dotenv()

client = OpenAI()

def create_embeddings(texts):
    """
    texts: list of strings
    returns: NumPy array (len(texts), embedding_dim) float32
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )

    embeddings = [item.embedding for item in response.data]

    return np.array(embeddings, dtype="float32")


def embed_query(query):
    """
    Embed a single query string
    returns: 2D NumPy array (1, dim)
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    embedding = response.data[0].embedding

    return np.array([embedding], dtype="float32")