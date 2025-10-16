import streamlit as st
import requests
import pandas as pd

# --- TMDb API Configuration ---

# Try to get the API key from Streamlit secrets
try:
    API_KEY = st.secrets['api_key']
except (FileNotFoundError, KeyError):
    # If secrets aren't found, set API_KEY to empty and handle the error
    API_KEY = ""

# --- Core API & Data Functions ---

@st.cache_data(ttl=60 * 60 * 12)
def get_movie_details(movie_id):
    """
    Fetches detailed information for a single movie from the TMDb API.
    
    This function retrieves the overview, primary cast (top 5 actors), and the director.
    """
    if not API_KEY:
        st.error("TMDb API key is not configured. Please add it to your secrets.", icon="🚨")
        return {} # Return empty dict if API key is missing

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        details = response.json()

        # Extract cast (top 5)
        cast = [actor['name'] for actor in details.get('credits', {}).get('cast', [])[:5]]
        
        # Find the director from the crew list
        director = next((crew['name'] for crew in details.get('credits', {}).get('crew', []) if crew['job'] == 'Director'), 'N/A')
        
        return {
            "title": details.get('title', 'N/A'),
            "overview": details.get('overview', 'No overview available.'),
            "poster_path": details.get('poster_path'),
            "cast": cast,
            "director": director,
            "id": details.get('id')
        }
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}", icon="🌐")
        return {} # Return empty dict on API failure
    except Exception as e:
        st.error(f"An unexpected error occurred in get_movie_details: {e}", icon="💥")
        return {}

@st.cache_data(ttl=60 * 60 * 6)
def search_movie(query: str):
    """
    Searches for a movie by its title.
    
    This function finds the most popular and relevant movie matching the user's query
    and returns its full details. It acts as our primary "search" tool.
    """
    if not API_KEY:
        st.error("TMDb API key is not configured.", icon="🚨")
        return []

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        if not results:
            return []

        # "Smart" Search: Sort the top 5 results by popularity and pick the best one.
        top_results = sorted(results[:5], key=lambda x: x.get('popularity', 0), reverse=True)
        best_match_id = top_results[0]['id']
        
        # Return a list containing the details of the single best match
        return [get_movie_details(best_match_id)]

    except requests.exceptions.RequestException as e:
        st.error(f"The movie search API request failed: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred during the movie search: {e}")
        return []

def get_recommendations_by_genre(genres):
    """
    Public entry for tool-calling. Normalizes unhashable/proto lists, then
    delegates to a cached inner function keyed by a hashable tuple.
    """
    # Normalize to a stable, hashable tuple of lowercase strings
    try:
        normalized = tuple(sorted([str(g).strip().lower() for g in list(genres)]))
    except Exception:
        # Fallback: treat as single string
        normalized = (str(genres).strip().lower(),)
    return _cached_get_recommendations_by_genre(normalized)


@st.cache_data(ttl=60 * 60 * 6)
def _cached_get_recommendations_by_genre(genres_key: tuple[str, ...]):
    """
    Cached implementation that expects a hashable tuple of genres.
    """
    if not API_KEY:
        st.error("TMDb API key is not configured.", icon="🚨")
        return []

    try:
        genre_dict = get_genre_dict()

        # Map normalized names to IDs
        genre_ids = [genre_dict[g] for g in genres_key if g in genre_dict]
        if not genre_ids:
            return []

        genre_id_string = ",".join(map(str, genre_ids))
        discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genre_id_string}&sort_by=popularity.desc"

        response = requests.get(discover_url)
        response.raise_for_status()
        movies = response.json().get('results', [])
        if not movies:
            return []

        top_5_movie_ids = [movie['id'] for movie in movies[:5]]
        detailed_movies = [get_movie_details(movie_id) for movie_id in top_5_movie_ids]
        return [movie for movie in detailed_movies if movie]

    except requests.exceptions.RequestException as e:
        st.error(f"The genre recommendation API request failed: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while getting recommendations: {e}")
        return []

@st.cache_data(ttl=60 * 60 * 24)
def get_genre_dict():
    """
    Fetch and cache the TMDb genre mapping of name -> id.
    """
    if not API_KEY:
        return {}
    genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}"
    try:
        response = requests.get(genre_url)
        response.raise_for_status()
        genre_list = response.json().get('genres', [])
        return {g['name'].lower(): g['id'] for g in genre_list}
    except Exception:
        return {}


@st.cache_data(ttl=60 * 60 * 6)
def get_similar_movies(title: str):
    """
    Finds up to 5 movies similar to the given movie title.

    This function first searches TMDb for the best-matching movie ID for the provided
    title, then queries the "similar" endpoint, and finally enriches each result with
    full details using get_movie_details.
    """
    if not API_KEY:
        st.error("TMDb API key is not configured.", icon="🚨")
        return []

    # 1) Search for the best match to obtain a movie ID
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
    try:
        search_resp = requests.get(search_url)
        search_resp.raise_for_status()
        search_results = search_resp.json().get('results', [])

        if not search_results:
            return []

        # Pick best match by popularity among top 5
        top_results = sorted(search_results[:5], key=lambda x: x.get('popularity', 0), reverse=True)
        best_match_id = top_results[0]['id']

        # 2) Query the similar movies endpoint
        similar_url = f"https://api.themoviedb.org/3/movie/{best_match_id}/similar?api_key={API_KEY}"
        similar_resp = requests.get(similar_url)
        similar_resp.raise_for_status()
        similar_results = similar_resp.json().get('results', [])

        if not similar_results:
            return []

        # 3) Enrich top 5 with detailed info
        top_5_ids = [movie['id'] for movie in similar_results[:5]]
        detailed = [get_movie_details(mid) for mid in top_5_ids]
        return [m for m in detailed if m]

    except requests.exceptions.RequestException as e:
        st.error(f"The similar movies API request failed: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while getting similar movies: {e}")
        return []