import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from tmdb.api import search_tmdb, get_tmdb_details
from api_config import API_KEYS

import pytest

@pytest.fixture
def tmdb_key():
    return API_KEYS['tmdb']  # Replace with your TMDB API key for testing

def test_search_tmdb_movie(tmdb_key):
    """
    Test the search_tmdb function for a movie.
    """
    query = "Star Wars The Empire Strikes Back"
    results = search_tmdb(query=query, api_key=tmdb_key, is_tv=False)
    assert "results" in results, "Results should be present in the response"
    assert len(results["results"]) > 0, "There should be at least one result"
    print(f"Search results for movie: {results['results']}")

def test_search_tmdb_tv(tmdb_key):
    """
    Test the search_tmdb function for a TV show.
    """
    query = "Star Wars The Mandalorian"
    results = search_tmdb(query=query, api_key=tmdb_key, is_tv=True)
    assert "results" in results, "Results should be present in the response"
    assert len(results["results"]) > 0, "There should be at least one result"
    print(f"Search results for TV show: {results['results']}")

def test_get_tmdb_details_movie(tmdb_key):
    """
    Test the get_tmdb_details function for a movie.
    """
    tmdb_id = 1891  # TMDB ID for "The Empire Strikes Back"
    details = get_tmdb_details(tmdb_id=tmdb_id, api_key=tmdb_key, is_tv=False)
    assert "title" in details, "Details should contain the title"
    print(f"Details for movie: {details}")

def test_get_tmdb_details_tv(tmdb_key):
    """
    Test the get_tmdb_details function for a TV show.
    """
    tmdb_id = 82856  # TMDB ID for "The Mandalorian"
    details = get_tmdb_details(tmdb_id=tmdb_id, api_key=tmdb_key, is_tv=True)
    assert "name" in details, "Details should contain the name"
    print(f"Details for TV show: {details}")
