from fastembed import TextEmbedding

embedding_model = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embeddings = embedding_model.embed(["Hello world!"])
print(next(embeddings))