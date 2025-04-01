import pytest
import sys
import osinsert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
print("sys.path before modification:", sys.path)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))from tmdb.scraper import find_tmdb_id, process_media_entry
print("sys.path after modification:", sys.path)

from tmdb.scraper import find_tmdb_id, process_media_entry
from tmdb.api import search_tmdb, get_tmdb_details
import pandas as pd

@pytest.fixture
def mock_row_movie():
    return pd.Series({
        "Name": "The Empire Strikes Back",
        "Show/Trilogy": None,
        "Season": None,
        "Episode Number": None,
        "Media Type": "movie"
    })

@pytest.fixture
def mock_row_tv():
    return pd.Series({
        "Name": None,
        "Show/Trilogy": "The Mandalorian",
        "Season": 1,
        "Episode Number": 1,
        "Media Type": "tv"
    })

@pytest.fixture
def tmdb_key():
    return "your_tmdb_api_key_here"  # Replace with your TMDB API key for testing

def test_find_tmdb_id_movie(mock_row_movie, tmdb_key):
    """
    Test the find_tmdb_id function for a movie.
    """
    tmdb_id = find_tmdb_id(mock_row_movie, tmdb_key)
    assert tmdb_id is not None, "TMDB ID should not be None for a valid movie"
    print(f"TMDB ID for movie: {tmdb_id}")

def test_find_tmdb_id_tv(mock_row_tv, tmdb_key):
    """
    Test the find_tmdb_id function for a TV show.
    """
    tmdb_id = find_tmdb_id(mock_row_tv, tmdb_key)
    assert tmdb_id is not None, "TMDB ID should not be None for a valid TV show"
    print(f"TMDB ID for TV show: {tmdb_id}")

def test_process_media_entry_movie(mock_row_movie, tmdb_key):
    """
    Test the process_media_entry function for a movie.
    """
    details = process_media_entry(mock_row_movie, tmdb_key, gem_key="dummy_gemini_key")
    assert details is not None, "Details should not be None for a valid movie"
    assert "title" in details, "Details should contain the title"
    print(f"Processed details for movie: {details}")

def test_process_media_entry_tv(mock_row_tv, tmdb_key):
    """
    Test the process_media_entry function for a TV show.
    """
    details = process_media_entry(mock_row_tv, tmdb_key, gem_key="dummy_gemini_key")
    assert details is not None, "Details should not be None for a valid TV show"
    assert "title" in details, "Details should contain the title"
    print(f"Processed details for TV show: {details}")
