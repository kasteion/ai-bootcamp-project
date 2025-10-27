import github_data_reader as reader
import chordpro_parser as parser

raw_songs = reader.read_github_data('Asacri', 'asacriband-chords')
parsed_songs = parser.parse_data(raw_songs)