import sys
import asyncio
import repertoire_agent
from tqdm import tqdm

agent = repertoire_agent.create_agent()
callback = repertoire_agent.NamedCallback(agent)

async def run_agent(user_prompt: str):
    results = await agent.run(
        user_prompt=user_prompt,
        event_stream_handler=callback
    )
    return results

def run_agent_sync(user_prompt: str):
    return asyncio.run(run_agent(user_prompt))

def format_output(output):
    response = ["Te recomiendo tocar las siguientes canciones:\n"]
    evaluation = output.repertoireEvaluation
    for song in evaluation.songScores:
        response.append(f"  - '{song.title}' en clave de {song.key} con una relevancia del: {song.score}%\n")

    response.append(f"\nLuego de la evaluación este repertorio tiene una relvancia del {evaluation.score}%\n")

    response.append("\nJustificación:\n")
    response.append(evaluation.justification)
    return "\n".join(response)

def main():
    if len(sys.argv) != 2:
        print("Usage main.py '<request>'")
        return
    
    user_prompt = sys.argv[1]
    result = run_agent_sync(user_prompt=user_prompt)
    print(format_output(result.output))


if __name__ == "__main__":
    main()