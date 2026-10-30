from data_ingestion.config import ACTS, BM25_DIR, CHUNKS_DIR, COLLECTION, EMBED_MODEL, OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_DIR, QDRANT_URL

CHAT_MODEL = "gpt-6-luna"  
VECTOR_TOP_K = 3          # hybrid search (Day 12): 3 chunks by meaning
BM25_TOP_K = 2            # + 2 more by keywords (section numbers, exact words)
MAX_HISTORY = 6           # past chat messages sent to the model (3 user + 3 assistant)
NOT_FOUND = "I couldn't find this in the laws I have."
OFF_TOPIC = "I can only answer questions about Indian law."
NOTICE = "Not legal advice: this shows what the text of the law says. Talk to a lawyer about your case."