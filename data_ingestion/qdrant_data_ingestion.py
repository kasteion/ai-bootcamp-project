import github_data_reader as reader
import chordpro_parser as parser

songs = reader.read_github_data('Asacri', 'asacriband-chords')
chunks = parser.parse_and_chunk(songs)

from qdrant_client import QdrantClient, models

from fastembed import TextEmbedding
from fastembed.common.model_description import ModelSource, PoolingType

qd_client = QdrantClient(url='http://localhost:6333', embedding_batch_size=1)

# dimensionality = 384
# model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
# collection_name = "asacriband-chords"

# qd_client.delete_collection(collection_name)

# qd_client.create_collection(
#     collection_name=collection_name,
#     vectors_config=models.VectorParams(
#         size=dimensionality,
#         distance=models.Distance.COSINE
#     )
# )

dimensionality = 384
model_name = 'multilingual'
collection_name = "asacriband-chords"

TextEmbedding.add_custom_model(
    model=model_name,
    pooling=PoolingType.MEAN,
    normalization=True,
    sources=ModelSource(hf="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
    dim=dimensionality
)
model = TextEmbedding(model_name=model_name)

points = []

for i, doc in enumerate(chunks):
    text = doc.content
    text = text.strip()
    vector = models.Document(text=text, model=model_name)


    if (len(text) > 0):
        point = models.PointStruct(id=i, vector=vector, payload={ 'title': doc.title, 'content': doc.content, 'key': doc.key })
        points.append(point)

qd_client.upsert(
    collection_name=collection_name,
    points=points
)