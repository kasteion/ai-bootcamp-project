from typing import List

from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.messages import FunctionToolCallEvent

from agent_tools.search_tools import SearchTools

# ===========================
# CALLBACK
# ===========================

class NamedCallback:

    def __init__(self, agent):
        self.agent_name = agent.name

    async def print_function_calls(self, ctx, event):
        # Detect nested streams
        if hasattr(event, "__aiter__"):
            async for sub in event:
                await self.print_function_calls(ctx, sub)
            return

        if isinstance(event, FunctionToolCallEvent):
            tool_name = event.part.tool_name
            args = event.part.args
            print(f"TOOL CALL ({self.agent_name}): {tool_name}({args})")

    async def __call__(self, ctx, event):
        return await self.print_function_calls(ctx, event)
    
# ===========================
# STRUCTURED OUTPUT
# ===========================

class Search(BaseModel):
    """keyword used for search and the song titles found"""
    keyword: str = Field(..., description="The keyword searched")
    titles: List[str] = Field(..., description = "A list of song titles from the search results")

class SearchPhase(BaseModel):
    """A list of the searches done by keyword and the relevant songs found"""
    searches: List[Search] = Field(..., description="A list of at 5 searches done to find relevant songs")

class SongList(BaseModel):
    "List of recommended songs with a score"
    title: str = Field(..., description="The title of the recommended song")
    key: str = Field(..., description="Key of the recommended song")

class SongScore(BaseModel):
    """"""
    title: str = Field(..., description="The title of the recommended song")
    key: str = Field(..., description="The key of the recommended song")
    score: int = Field(..., description="The score of the recommended song based on it's relevance")

class RepertoireEvaluation(BaseModel):
    "Final repertoire evaluation"
    songScores: List[SongScore] = Field(..., description="A list of 5 song titles with key and score")
    score: int = Field(..., description="Score for the complete repertoire")
    justification: str = Field(..., description="Justification of the score given to the repertoire")

class Repertoire(BaseModel):
    """The complete repertoir across all phases"""
    searchPhase: List[SearchPhase] = Field(..., description="Search stage report")
    songList: List[SongList] = Field(..., description = "A list of 4-5 recommended songs")
    repertoireEvaluation: RepertoireEvaluation = Field(..., description="Final repertoire evaluation")

# ===========================
# AGENT INSTRUCTIONS
# ===========================

instructions = """
Eres un agente cuyo objetivo es recomendar un listado de canciones 
basadas en un tema en el que el usuario se quiera enfocar.

OBJETIVO

Dado el tema en que el usuario quiere enfocarse, ejecuta búsquedas 
en la base de datos con la letra de las canciones para encontra canciones
relacionadas con el tema. Encuentra 4 o 5 canciones diferentes para usar 
como repertorio de canciones basadas en ese tema.

PROCESO

Fase 1 - Búsqueda inicial

- Tomando el input del usuario crea 5 palabras claves diferentes relacionadas con con ese tema.
- Utiliza `vector_search()` para buscar en la base de datos canciones relacionadas con las palabras clave.
- No te detengas hasta hacer 5 búsquedas.
- NO HAGAS MAS DE 7 BUSQUEDAS.

Fase 2 - Generar lista

Con el output de la Fase 1:

- Genera una lista de 4 a 5 títulos de las canciones y su key

Fase 3 - Evaluar lista

Con el output de la Fase 2:

- Utiliza solo las canciones de la fase 2 y obten la canción completa con `get_full_song_by_title()`
- Evalúa cada canción y asigna un score de 0 a 100 deacuerdo a que tan acertada es con respecto al tema que el usuario quiere
- Evalúa todo el repertorio y asigna un score de 0 a 100 deacuerdo a su relevancia y al score de las canciones.
- Escribe una justificación de score del repertorio
- EN ESTA FASE NO TIENES PERMITIDO volver a ejecutar `vector_search()`
"""

def create_agent() -> Agent:
    tools = SearchTools()

    agent_tools = [tools.vector_search, tools.get_full_song_by_title]

    agent = Agent(
        name="recomendations",
        instructions=instructions,
        tools=agent_tools,
        model='openai:gpt-4o-mini',
        output_type=Repertoire
    )

    return agent