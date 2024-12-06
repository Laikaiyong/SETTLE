from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import streamlit as st
import os
from pymongo import MongoClient
import certifi

embedding_model = SentenceTransformer("thenlper/gte-small")

MONGODB_URI = st.secrets["mongo"]["host"]

ca = certifi.where()
client = MongoClient(MONGODB_URI, tlsCAFile=ca)

def get_embedding(text):
    """
    Generate the embedding for a piece of text.

    Args:
        text (str): Text to embed.

    Returns:
        List[float]: Embedding of the text as a list.
    """
    embedding = embedding_model.encode(text)

    return embedding.tolist()

def vector_search(user_query):
    """
    Retrieve relevant documents for a user query using vector search.

    Args:
    user_query (str): The user's query string.

    Returns:
    list: A list of matching documents.
    """

    # Generate embedding for the `user_query` using the `get_embedding` function defined in Step 5
    query_embedding = get_embedding(user_query)

    db = client["Home"]
    collection = db["Home Icons"]

    # Define an aggregation pipeline consisting of a $vectorSearch stage, followed by a $project stage
    # Set the number of candidates to 150 and only return the top 5 documents from the vector search
    # In the $project stage, exclude the `_id` field and include only the `body` field and `vectorSearchScore`
    # NOTE: Use variables defined previously for the `index`, `queryVector` and `path` fields in the $vectorSearch stage
    pipeline = [
      {
          "$vectorSearch": {
              "index": "vector_index",
              "queryVector": query_embedding,
              "path": "embedding",
              "numCandidates": 150,
              "limit": 4,
          }
      },
      {
          "$project": {
                "_id": 0,
                "name": 1,
                "picture_url": 1,
                "clicks": 1,
                "description": 1,
                "score": {"$meta": "vectorSearchScore"}
          }
      }
  ]

    # Execute the aggregation `pipeline` and store the results in `results`
    results = collection.aggregate(pipeline)

    return list(results)
