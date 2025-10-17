import streamlit as st
import google.generativeai as genai
from google.ai import generativelanguage as glm
import helpers
import json

# --- 1. API and Model Configuration ---
try:
    genai.configure(api_key=st.secrets["gemini_api_key"]) # type: ignore
except Exception as e:
    st.error(f"Error configuring the Gemini API: {e}", icon="🚨")
    st.stop()

# --- 2. Tool Definition ---
tools = [
    helpers.search_movie,
    helpers.get_recommendations_by_genre,
    helpers.get_similar_movies,
    helpers.get_trending_movies,
    helpers.get_top_rated_movies,
    helpers.get_movies_by_actor,
    helpers.get_movies_by_director,
]

# --- 3. Model and Chat Initialization ---
safety_settings = {
    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
}

model = genai.GenerativeModel( # type: ignore
    model_name="models/gemini-2.5-flash-preview-05-20",
    safety_settings=safety_settings
)
chat = model.start_chat()

# --- 4. App Setup and State Initialization ---
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
st.title("🎬 Gemini Movie Recommender")

with st.sidebar:
    if st.button("Clear cached data"):
        st.cache_data.clear()
        st.success("Cache cleared.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I'm your movie-buff assistant. Ask me to find a movie by title or recommend something by genre!"}
    ]

# --- 5. UI Display ---
# Use enumerate to get the index of each message
for msg_index, message in enumerate(st.session_state.chat_history):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "results" in message:
            results = message["results"]
            if results:
                if isinstance(results, dict):
                    results = [results]
                
                num_columns = min(len(results), 5)
                cols = st.columns(num_columns)
                for i, movie in enumerate(results):
                    with cols[i % num_columns]:
                        if movie and movie.get("poster_path"): # type: ignore
                            st.image(f"https://image.tmdb.org/t/p/w200{movie.get('poster_path')}") # type: ignore
                        if movie:
                            st.markdown(f"**{movie.get('title', 'N/A')}**") # type: ignore
                            # --- THE KEY FIX ---
                            # Add the message index to the key to guarantee uniqueness
                            unique_key = f"details_{msg_index}_{movie.get('id')}_{i}" # type: ignore
                            if st.button("Show Details", key=unique_key):
                                    st.session_state.selected_movie = movie # type: ignore
                                    st.rerun()

if 'selected_movie' in st.session_state and st.session_state.selected_movie:
    movie = st.session_state.selected_movie
    with st.container(border=True):
        st.subheader(f"Details for: {movie.get('title')}") # type: ignore
        col1, col2 = st.columns([1, 2])
        with col1:
             if movie.get('poster_path'): # type: ignore
                st.image(f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}", use_container_width=True) # type: ignore
        with col2:
            st.write(f"**Synopsis:** {movie.get('overview', 'No synopsis available.')}") # type: ignore
            st.write(f"**Cast:** {', '.join(movie.get('cast', ['N/A']))}") # type: ignore
            st.write(f"**Director:** {movie.get('director', 'N/A')}") # type: ignore
            if st.button("Back to Chat"):
                del st.session_state.selected_movie
                st.rerun()

# --- 6. User Input and Chat Logic ---
if prompt := st.chat_input("Ask me for a movie, genre, or something similar..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = chat.send_message(prompt, tools=tools)
        response_part = response.candidates[0].content.parts[0]

        if hasattr(response_part, 'function_call') and response_part.function_call:
            with st.spinner("Calling my movie database tool... 🎬"):
                function_call = response_part.function_call
                tool_function = next((f for f in tools if f.__name__ == function_call.name), None)

                if tool_function:
                    tool_response = tool_function(**dict(function_call.args))
                    
                    response_text = ""
                    if tool_response:
                        if isinstance(tool_response, list):
                            # Customize message slightly based on which tool responded
                            if function_call.name == 'get_recommendations_by_genre':
                                response_text = "Of course! Here are some recommendations by genre:"
                            elif function_call.name == 'get_similar_movies':
                                response_text = "Got it! Here are movies similar to your request:"
                            elif function_call.name == 'get_trending_movies':
                                response_text = "Here are the trending movies right now:"
                            elif function_call.name == 'get_top_rated_movies':
                                response_text = "Here are top rated movies:" 
                            elif function_call.name == 'get_movies_by_actor':
                                response_text = "Here are movies featuring that actor:" 
                            elif function_call.name == 'get_movies_by_director':
                                response_text = "Here are movies directed by that person:"
                            else:
                                response_text = "Of course! Here are some recommendations I found for you:"
                        else:
                            response_text = f"You got it. Here is the result for '{tool_response.get('title')}':"
                    else:
                        response_text = "Sorry, I couldn't find anything matching your request."
                    
                    assistant_message = {"role": "assistant", "content": response_text}
                    if tool_response:
                        assistant_message["results"] = tool_response # type: ignore
                    
                    st.session_state.chat_history.append(assistant_message)
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Error: Could not find the tool '{function_call.name}'."})
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})

    except (IndexError, AttributeError, genai.types.StopCandidateException) as e: # type: ignore
        st.error("An API or safety error occurred. Please try again.")

    st.rerun()

