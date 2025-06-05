import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import json
import uuid
import redis
from langchain_google_genai import GoogleGenerativeAI
from utils import safe_json_dumps
from dotenv import load_dotenv,dotenv_values,set_key
class RedisVectorStore:
    def __init__(self, redis_client):
        load_dotenv("venv/.env")
        self.redis = redis_client
        self.model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.llm=GoogleGenerativeAI(model="gemini-2.0-flash")
    def store_document(self, text, meta):
        vector = np.array(self.model.embed_documents([text])).flatten().astype(np.float32)
        key = f"doc:{str(uuid.uuid4())}"
        json_str=safe_json_dumps(meta)
        # Store the actual data
        self.redis.hset(key, mapping={
            "text": text,
            "metadata": json_str
        })
        self.redis.set(f"{key}:vector", vector.tobytes())
        return key

    def cosine_similarity(self, vec1, vec2):
        return float(np.dot(vec1, vec2))

    def query_similar(self, query_text, top_k=3):
        query_vec = np.array(self.model.embed_query(query_text)).astype(np.float32)
        all_keys = [k.decode() for k in self.redis.keys("doc:*") if not k.decode().endswith(":vector")]
        scores = []
        
        for key in all_keys:
            vec_bytes = self.redis.get(f"{key}:vector")
            if vec_bytes:
                doc_vec = np.frombuffer(vec_bytes, dtype=np.float32)
                sim = self.cosine_similarity(query_vec, doc_vec)
                scores.append((sim, key))

        top_matches = sorted(scores, reverse=True)[:top_k]
        retrieved_docs = []
        
        for sim, key in top_matches:
            text = self.redis.hget(key, "text").decode()
            metadata = json.loads(self.redis.hget(key, "metadata"))
            retrieved_docs.append(f"[Source: {metadata.get('source', 'unknown')}]\n{text}")

        context = "\n\n".join(retrieved_docs)
        
        # Prompt for the LLM
        final_prompt = f"""You are a business assistant. Use the following context to answer the user's query.
    give a professional answer
    Context:
    {context}

    User Query: {query_text}

    Answer:"""

        # LLM call (pseudo-code, replace with your model)
        answer = self.llm.invoke(final_prompt)

        return {
            "query": query_text,
            "answer": answer,
            "matches": [{"key": k, "score": s} for s, k in top_matches]
        }


        return results
    def clear_database(self):
        """
        Deletes all keys in the current Redis database.
        """
        self.redis.flushdb()
       # confirmation = input("Are you sure you want to delete all data in Redis? Type 'YES' to confirm: ")
        # if confirmation == "YES":
            
        #     print("Redis database cleared.")
        # else:
        #     print("Operation cancelled.")
    

    
if __name__ == "__main__":
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=False)
    
    store = RedisVectorStore(redis_client)
    store.clear_database()
    # Store a document
    store.store_document("This is an invoice for April", {"type": "invoice"})
    store.store_document("Hey just checkin on your invoice documents", {"type": "fraud"})
    store.store_document("Your policies dont incline with gdpr", {"type": "complaint"})
    
    
    # Query similar
    results = store.query_similar("what are the invoices for?", top_k=2)
    print(results)
