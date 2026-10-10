text = 'what is the day today?'

text -> tokens (toneization)
tokens = ['what', 'is', 'the', 'day', 'today', '?']
what = 152
is = 72....

tokens = [152, 72, 31, 45, 67, 12]  # hypothetical token IDs (token id)

tokens -> transformers (attention + neural network ) -> next token 

tokens -> list of tokens -> text




33000 tokens

user query + system prompt (50 lines) + context (500 lines) + chat history(last 10 chats) = input tokens - 20k
reasoning - reasoning tokens - 10k
genereate answer + image generate = output tokens -5k

need = 35k

max_tokens_output = 4096 


total tokens = input tokens + reasoning tokens + output tokens



1000 chunks -> embeddings

query -> embdeeings 

cosine_similarity(query, chunks) -> (0,1)

0.8
0.74
0.7
0.68
0.65
0.62
0.61
0.58
.....

top-k = 5
top-p = 0.6
