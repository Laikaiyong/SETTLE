from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os
from pymongo import MongoClient
import certifi

MONGODB_URI = ""

ca = certifi.where()
client = MongoClient(MONGODB_URI, tlsCAFile=ca)

db = client["Home"]
collection = db["Home Icons"]

all_items = list(collection.find({}, {
    "_id": 0,
    "name": 1,
    "picture_url": 1,
    "clicks": 1,
    "description": 1
}))

embedding_model = SentenceTransformer("thenlper/gte-small")

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


embedded_docs = []
for doc in tqdm(all_items):
    doc["embedding"] = get_embedding(doc["description"])

    embedded_docs.append(doc)

collection.delete_many({})
collection.insert_many(embedded_docs)

print("Data ingestion into MongoDB completed")
