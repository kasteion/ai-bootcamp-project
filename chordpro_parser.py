import re
from typing import List
from dataclasses import dataclass
from github_data_reader import RawRepositoryFile

@dataclass
class SongData:
    title: str
    key: str
    time: str
    section: str
    content: str

def parse_chordpro(text: str) -> List[SongData]:
    """
    Parse a ChordPro-formatted text into a list of SongData objects.
    
    - Extracts metadata (title, key, time)
    - Splits the song into sections using {comment: SECTION_NAME}
    - Removes chords inside square brackets (e.g. [C], [G/B])
    - Replaces newlines with spaces and normalizes spacing
    
    Args:
        text (str): Raw song text in ChordPro format.
        
    Returns:
        List[SongData]: Parsed sections of the song.
    """
    # --- Extract metadata ---
    title_match = re.search(r"\{title:\s*(.*?)\}", text, re.IGNORECASE)
    key_match = re.search(r"\{key:\s*(.*?)\}", text, re.IGNORECASE)
    time_match = re.search(r"\{time:\s*(.*?)\}", text, re.IGNORECASE)
    
    title = title_match.group(1).strip() if title_match else "Unknown"
    key = key_match.group(1).strip() if key_match else "Unknown"
    time = time_match.group(1).strip() if time_match else "Unknown"

    # --- Split into sections by {comment: SECTION_NAME} ---
    section_pattern = re.compile(
        r"\{comment:\s*(.*?)\}\s*([\s\S]*?)(?=\{comment:|\Z)", re.IGNORECASE
    )

    sections = []
    for match in section_pattern.finditer(text):
        section_name = match.group(1).strip()
        section_content = match.group(2).strip()

        # --- Remove chords like [C], [Gmaj7], [D/F#], etc. ---
        section_content = re.sub(r"\[[^\]]+\]", "", section_content)

        # --- Replace newlines with spaces and clean spacing ---
        section_content = section_content.replace("\n", " ")
        section_content = re.sub(r"\s{2,}", " ", section_content).strip()

        # --- Replace other unwanted characters ---
        section_content = section_content.replace("-", "")
        section_content = section_content.replace("|", "")
        section_content = section_content.replace("/", "")
        
        # --- Strip ---
        section_content = section_content.strip()

        sections.append(SongData(
            title=title,
            key=key,
            time=time,
            section=section_name,
            content=section_content
        ))

    return sections

def parse_and_chunk(data_raw: List[RawRepositoryFile]) -> List[SongData]:
    data_parsed = []
    
    for f in data_raw:
        data = parse_chordpro(f.content)
        data_parsed.extend(data)

    return data_parsed