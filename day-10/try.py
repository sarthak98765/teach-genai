day 8 -> basic RAG chatbot
day 9 -> data parsing, data cleaning, chunking
day 10 -> chunks (with metadata) -> embeddings , vector database

embedding:
words/senteneces convert into numberical vectors 

text-embedding-3-small
[0.23, -0.7......] -> 1536 dimensions -> 50 MB

text-embedding-3 large -> 3072 dimesnions -> 150 MB

miniLM -> 356 dimensions

1. difference in dimensions

explain sarthak? 

height 
weight
age
gender

dimensions increase -> search better -> embeedinfs size increase -> cost high

2. similarity (198 chunks)
top_k = 5

query -> "what is law of protest?" -> tokenization -> token id -> embeddings (textembedinng 3 small) -> [1536 vectors]
chunk0 = [1536 vectors]
chunks 1 = [1536 vectors]
...
chunks 198 =[1536 vectoes]

cosine similairty = a (vector) . b (vector) / |a|*|b|
--------------------------------------------------------
q = np.array([1, 1, 0, 0, 0, 0])                 # made-up vectors, not from a model
toy_chunks = {"C1 murder":             [2, 2, 0, 0, 0, 0],
              "C2 culpable homicide":  [1, 1, 1, 0, 0, 0],
              "C3 hurt":               [1, 0, 1, 0, 0, 0],
              "C4 theft":              [0, 0, 0, 1, 1, 0],
              "C5 biryani recipe":     [-1, 0, 0, 0, 1, 0]}

q , c2 -> simialriy 

q.c2=[1, 1, 0, 0, 0, 0].[1, 1, 1, 0, 0, 0] = 1 + 1 + 0 +0+0+ 0 = 2
|q| = underooot (2) =1.41
|c2| = underrot (3) = 1.73

cosine similairy (q,c2) = 2/(1.41) *(1.73) = 2/2.44 = 0.819
cosine similairy (q,c1) = 0.7
cosine similairy (q,c3) = 1
cosine similairy (q,c4) = 0.2
cosine similairy (q,c5) = 0.4

-1,1
similarity score = -1 to 1

chunks -> embeddings -> (vectordbs)
columns name 
features, -> fixed schema 

traditional: sql -> fixed schema -> data retrivee
vector db -> there is no fixed schema 

qdrant, pinecone, weaviate -> these 3 are generally used in production
faiss

198

5000 chunks -> 90% chunks eleiminate --> 7 % elimiate 

1. Brute force
2. IVF
3. HNSW 

shamli -> indore 
shamli (local streets) -> main road -> Highway/expressway -> main road -> streets -> aapka ghar

expressway/highway -> 1km = 1 min 
main road = 4-5 min
local streets = 1km = 10-15 min

5000 chunks 
400 chunks - concept 1 (food)
300 chunks - concept 2 (travel)


embeddings create 
vector search  -> optimization step -> HNSW algorithm (qdrant, pinecone)
top k chunks 
LLM 
thinking (reasonign) -> ltency
generation (throughput)

< 10 seconds



day 10 -> embeddings, indexing(HNSW), vectordb
day 11 -> retireval (chatbot)
day 12-> hybrid (vector + bm25 search)
day 13 -> re-ranking
day 14 -> evals and observaibility


1. Qdrant
2. Pinecone
3. Weaviate




query -> user query -> LLM
1. re-write
2. multi-qeury
3. hyde

what is the crime of killing? -> LLM (system prompt)-> query re-write 

query = what is fees of iit delhi in 2026? -> llm -> 3 multiple queries -> 5

query 1= what is the tution fees of iit delhi in 2026 -> 5 
query 2 = what is the hostel fees of iit delhi in 2026 -> 5
query 3 = what is the total fees of iit dlehi in 2026 -> 5

15 -> de-duplication -> 12 -> re-ranker -> top 5


temperature - entropy (cretivaness)
top_k -> top chunks 
top_p -> threshold (top probability) -> 0.8 

cost reduce ->> LLM model
latency reduce
answer performance increase

recall@k, precision@k