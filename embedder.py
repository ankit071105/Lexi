from sentence_transformers import SentenceTransformer
import chromadb

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.Client()
collection = client.get_or_create_collection("policy_docs")

def embed_and_store(chunks, doc_name):
    embeddings = embedding_model.encode(chunks)
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i].tolist()],
            ids=[f"{doc_name}_{i}"]
        )

def query_top_chunks(query, k=3):
    q_embed = embedding_model.encode([query])[0].tolist()
    results = collection.query(query_embeddings=[q_embed], n_results=k)
    return results['documents'][0]
