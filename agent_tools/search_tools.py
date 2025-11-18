from qdrant_client import QdrantClient, models
from typing import TypedDict, List
import data_ingestion.github_data_reader as reader
import data_ingestion.chordpro_parser as parser

dimensionality = 384
model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
collection_name = "asacriband-chords"

qd_client = QdrantClient('http://localhost:6333')

songs = reader.read_github_data('Asacri', 'asacriband-chords')
chunks = parser.parse_and_chunk(songs)

class SearchResult(TypedDict):
    """Represents a single search result entry."""
    title: str
    content: str
    key: str

class SearchTools:
    def vector_search(self, query: str, num_results=15) -> List[SearchResult]:
        """
        Performs a vector search looking for lyrics related with the query.

        Args:
            query (str): The search query string.

        Returns:
            List[SearchResult]: A list of search results. Each result dictionary contains:
                - title (str): The title of the song.
                - content (str): The content of the song that matched.
                - key (str): The key the of the song.
        """
        vector = models.Document(text=query, model=model_name)

        query_points = qd_client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=num_results,
            with_payload=True
        )

        results = []

        for point in query_points.points:
            results.append(point.payload)

        return results

    def get_full_song_by_title(self, title: str) -> SearchResult:
        """
        Retrieve full song by title

        Args:
            title (str): The title of the song
        
        Returns:
            SearchResult: The full song
                - title (str): The title of the song.
                - content (str): The content of the song.
                - key (str): The key the of the song.
        """
        sections = [chunk for chunk in chunks if chunk.title == title]
        if len(sections) == 0:
            return ""
        
        title = sections[0].title
        key = sections[0].key
        content = ' '.join([section.content for section in sections])
        return SearchResult(title = title, content=content, key=key)