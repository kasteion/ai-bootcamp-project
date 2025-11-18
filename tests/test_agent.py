from main import run_agent_sync
from utils import get_tool_calls

def test_agent_tool_calls_present():
    result = run_agent_sync("Crea un repertorio que hable del amor de Dios")
    print(result)
    tool_calls = get_tool_calls(result)

    # Tool calls
    assert len(tool_calls) > 0, "No tool calls found"
    
    # At least 5 vector_search calls
    assert len([tool_call for tool_call in tool_calls if tool_call.name == 'vector_search']) >= 5

    # At least 5 get_full_song_by_title calls
    assert len([tool_call for tool_call in tool_calls if tool_call.name == 'get_full_song_by_title']) >= 5
